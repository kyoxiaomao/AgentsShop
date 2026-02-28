import asyncio
import datetime
import importlib
import json
import logging
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from datacenter.service import build_ui_snapshot, snapshot_path

logger = logging.getLogger("datacenter")

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
CHAT_STORE_FILE = os.path.join(BASE_DIR, "chat_store.json")
STATUS_FILE = os.path.join(BASE_DIR, "status.json")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
CHAT_LOG_FILE = os.path.join(LOGS_DIR, "chat.jsonl")
DEBUG_LOG_FILE = os.path.join(LOGS_DIR, "debug.jsonl")
STREAM_CHUNK_DELAY = float(os.getenv("STREAM_CHUNK_DELAY", "0.02"))
STREAM_CHUNK_SIZE = max(1, int(os.getenv("STREAM_CHUNK_SIZE", "1")))
STREAM_CHUNK_MODE = os.getenv("STREAM_CHUNK_MODE", "raw").lower()

AGENT_MESSAGE_DIRS = {
    "seraAgent": os.path.join(ROOT_DIR, "agents", "queen", "Queen_Sera", "message"),
}

AGENT_CLASS_PATHS = {
    "seraAgent": "agents.queen.Queen_Sera:SeraAgent",
}

AGENT_INSTANCES: dict[str, Any] = {}


def _now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

def _strip_thinking_prefix(text: str) -> str:
    trimmed = text.lstrip()
    if not trimmed.startswith("{") or '"thinking"' not in trimmed:
        return text
    depth = 0
    end_index = None
    for i, ch in enumerate(trimmed):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end_index = i
                break
    if end_index is None:
        return text
    remainder = trimmed[end_index + 1 :].strip()
    return remainder if remainder else text

def _extract_text(value) -> str:
    if isinstance(value, str):
        return _strip_thinking_prefix(value)
    if value is None:
        return ""
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, dict):
                item_type = item.get("type")
                if item_type in {"thinking", "tool_use", "tool_result", "audio", "image", "video"}:
                    continue
                if item_type == "text" and "text" in item:
                    parts.append(str(item.get("text", "")))
                elif "text" in item:
                    parts.append(str(item.get("text", "")))
                elif "content" in item:
                    parts.append(_extract_text(item.get("content")))
                elif "thinking" in item:
                    continue
            else:
                parts.append(_extract_text(item))
        return "\n\n".join([p for p in parts if p is not None])
    if isinstance(value, dict):
        if value.get("type") in {"thinking", "tool_use", "tool_result", "audio", "image", "video"}:
            return ""
        if "text" in value:
            return str(value.get("text", ""))
        if "content" in value:
            return _extract_text(value.get("content"))
        if "thinking" in value:
            return ""
        return ""
    return str(value)

def _read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception as e:
        logger.error("read json failed %s %s", path, e)
        return default


def _write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _update_status(agent_id: str, status: str) -> None:
    data = _read_json(STATUS_FILE, {})
    data[agent_id] = {"status": status, "updated_at": _now_iso()}
    _write_json(STATUS_FILE, data)
    build_ui_snapshot()
    _append_debug_log("status_updated", {"agent_id": agent_id, "status": status})


def _append_markdown(agent_id: str, session_id: str, role: str, content: str) -> None:
    message_dir = AGENT_MESSAGE_DIRS.get(agent_id)
    if not message_dir:
        return
    _ensure_dir(message_dir)
    filename = f"session-{session_id}.md"
    path = os.path.join(message_dir, filename)
    role_label = "用户" if role == "user" else "Agent"
    normalized = _extract_text(content)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"### {role_label} {_now_iso()}\n\n{normalized}\n\n")
    _append_debug_log(
        "markdown_written",
        {"agent_id": agent_id, "session_id": session_id, "role": role, "path": path},
    )


def _load_messages() -> dict:
    return _read_json(CHAT_STORE_FILE, {"version": 1, "sessions": {}})


def _save_messages(store: dict) -> None:
    _write_json(CHAT_STORE_FILE, store)


def _append_message(agent_id: str, session_id: str, role: str, content: str) -> list[dict]:
    store = _load_messages()
    sessions = store.setdefault("sessions", {})
    key = f"{agent_id}:{session_id}"
    items = sessions.setdefault(key, [])
    normalized = _extract_text(content)
    item = {"role": role, "content": normalized, "ts": _now_iso()}
    items.append(item)
    _save_messages(store)
    _append_debug_log(
        "message_stored",
        {"agent_id": agent_id, "session_id": session_id, "role": role, "length": len(normalized)},
    )
    return items


def _get_messages(agent_id: str, session_id: str) -> list[dict]:
    store = _load_messages()
    raw_messages = store.get("sessions", {}).get(f"{agent_id}:{session_id}", [])
    messages = [
        {**item, "content": _extract_text(item.get("content"))}
        if isinstance(item, dict)
        else {"role": "assistant", "content": _extract_text(item), "ts": _now_iso()}
        for item in raw_messages
    ]
    _append_debug_log(
        "messages_loaded",
        {"agent_id": agent_id, "session_id": session_id, "count": len(messages)},
    )
    return messages


def _append_chat_log(agent_id: str, session_id: str, role: str, content: str) -> None:
    _ensure_dir(LOGS_DIR)
    normalized = _extract_text(content)
    item = {
        "ts": _now_iso(),
        "agent_id": agent_id,
        "session_id": session_id,
        "role": role,
        "content": normalized,
    }
    with open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def _append_debug_log(event: str, payload: dict) -> None:
    _ensure_dir(LOGS_DIR)
    item = {"ts": _now_iso(), "event": event, **payload}
    with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def _clear_chat_log() -> None:
    _ensure_dir(LOGS_DIR)
    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")
    with open(DEBUG_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")


def _clear_chat_store() -> None:
    _write_json(CHAT_STORE_FILE, {"version": 1, "sessions": {}})


def _clear_agent_messages() -> None:
    for _agent_id, message_dir in AGENT_MESSAGE_DIRS.items():
        if not os.path.isdir(message_dir):
            continue
        for name in os.listdir(message_dir):
            if name.endswith(".md"):
                try:
                    os.remove(os.path.join(message_dir, name))
                except Exception:
                    continue


def _iter_chunks(text: str, size: int = 1):
    if not text:
        return
    for i in range(0, len(text), size):
        yield text[i : i + size]


def _diff_text(next_text: str, prev_text: str) -> str:
    if not next_text:
        return ""
    if next_text.startswith(prev_text):
        return next_text[len(prev_text) :]
    max_len = min(len(next_text), len(prev_text))
    idx = 0
    while idx < max_len and next_text[idx] == prev_text[idx]:
        idx += 1
    return next_text[idx:]


def _get_agent(agent_id: str):
    class_path = AGENT_CLASS_PATHS.get(agent_id)
    if class_path is None:
        raise ValueError(f"unknown agent {agent_id}")
    module_path, class_name = class_path.split(":")
    try:
        module = importlib.import_module(module_path)
        agent_cls = getattr(module, class_name)
    except Exception as e:
        _append_debug_log(
            "agent_import_failed",
            {"agent_id": agent_id, "class_path": class_path, "error": str(e)},
        )
        raise
    if agent_id not in AGENT_INSTANCES:
        AGENT_INSTANCES[agent_id] = agent_cls()
        _append_debug_log("agent_initialized", {"agent_id": agent_id, "class": agent_cls.__name__})
    return AGENT_INSTANCES[agent_id]


def _ensure_snapshot() -> dict:
    build_ui_snapshot()
    path = snapshot_path()
    snapshot = _read_json(path, {"version": 1, "agents": [], "status": {}})
    _append_debug_log(
        "snapshot_loaded",
        {"agents": len(snapshot.get("agents", [])), "status": len(snapshot.get("status", {}))},
    )
    return snapshot


class ApiHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args) -> None:
        return
    def _send_json(self, data: dict, status_code: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def _send_sse(self, payload: dict) -> None:
        raw = f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
        self.wfile.write(raw)
        self.wfile.flush()

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/agents":
            _append_debug_log("http_get_agents", {"path": self.path})
            self._send_json(_ensure_snapshot())
            return
        if parsed.path == "/api/messages":
            query = parse_qs(parsed.query)
            agent_id = (query.get("agent_id") or ["seraAgent"])[0]
            session_id = (query.get("session_id") or ["default"])[0]
            _append_debug_log(
                "http_get_messages",
                {"agent_id": agent_id, "session_id": session_id, "path": self.path},
            )
            self._send_json(
                {"agent_id": agent_id, "session_id": session_id, "messages": _get_messages(agent_id, session_id)}
            )
            return
        self._send_json({"error": "not_found"}, status_code=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/debug":
            payload = self._read_body()
            if isinstance(payload, dict):
                event = payload.get("event", "frontend_log")
                data = payload.get("data", {})
                if not isinstance(data, dict):
                    data = {"value": data}
                _append_debug_log(event, {"source": "frontend", **data})
            self._send_json({"ok": True})
            return
        if parsed.path == "/api/chat/stream":
            payload = self._read_body()
            agent_id = payload.get("agent_id") or "seraAgent"
            content = (payload.get("content") or "").strip()
            session_id = payload.get("session_id") or "default"
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            _append_debug_log(
                "http_post_chat_stream",
                {"agent_id": agent_id, "session_id": session_id, "length": len(content)},
            )
            _append_debug_log("stream_opened", {"agent_id": agent_id, "session_id": session_id})
            if not content:
                _append_debug_log("stream_empty_content", {"agent_id": agent_id, "session_id": session_id})
                self._send_sse({"type": "error", "message": "empty_content"})
                return
            try:
                _update_status(agent_id, "busy")
                agent = _get_agent(agent_id)
                if hasattr(agent, "model") and hasattr(agent.model, "stream"):
                    agent.model.stream = True
                try:
                    from agentscope.message import Msg
                except Exception as e:
                    _append_debug_log("agentscope_missing", {"error": str(e)})
                    _append_debug_log(
                        "stream_agent_error",
                        {"agent_id": agent_id, "session_id": session_id, "stage": "import_msg", "error": str(e)},
                    )
                    self._send_sse({"type": "error", "message": str(e)})
                    return
                msg = Msg(name="User", content=content, role="user")
                _append_debug_log("agent_reply_start", {"agent_id": agent_id, "session_id": session_id})
                _append_debug_log(
                    "stream_mode",
                    {"agent_id": agent_id, "session_id": session_id, "mode": "agent_queue"},
                )

                async def _stream_reply():
                    # 基于 agentscope 的消息队列实现流式：agent.reply 在后台推理，队列里持续产出中间消息
                    stream_start = time.monotonic()
                    last_text = ""
                    chunk_count = 0
                    idle_rounds = 0
                    stream_last_received = False
                    first_queue_ms = None
                    first_delta_ms = None
                    reply_done_ms = None
                    # 创建专用队列用于接收 agent 的流式消息
                    stream_queue = asyncio.Queue(maxsize=200)
                    agent.set_msg_queue_enabled(True, stream_queue)
                    try:
                        # 异步执行推理任务，同时从队列读取增量内容
                        reply_task = asyncio.create_task(agent.reply(msg))
                        self._send_sse({"type": "start"})
                        while True:
                            # 推理结束且队列已清空时结束流式循环
                            if reply_task.done() and stream_last_received and (
                                agent.msg_queue is None or agent.msg_queue.empty()
                            ):
                                break
                            if agent.msg_queue is None:
                                await asyncio.sleep(0.05)
                                continue
                            try:
                                # 从队列取出最新消息（包含中间增量）
                                queued = await asyncio.wait_for(
                                    agent.msg_queue.get(),
                                    timeout=0.2,
                                )
                                idle_rounds = 0
                            except asyncio.TimeoutError:
                                # 队列暂时无数据，若推理已完成则累计空转次数以便退出
                                if reply_task.done() and reply_done_ms is None:
                                    reply_done_ms = int((time.monotonic() - stream_start) * 1000)
                                if reply_task.done():
                                    idle_rounds += 1
                                    if idle_rounds >= 5 and (
                                        agent.msg_queue is None or agent.msg_queue.empty()
                                    ):
                                        break
                                continue
                            queued_msg, _is_last, _speech = queued
                            if first_queue_ms is None:
                                first_queue_ms = int((time.monotonic() - stream_start) * 1000)
                            if _is_last:
                                stream_last_received = True
                            # 从队列消息中提取文本内容（过滤 thinking/tool 等），并计算增量，避免重复输出
                            current_text = _extract_text(getattr(queued_msg, "content", ""))
                            delta = _diff_text(current_text, last_text)
                            if delta:
                                if STREAM_CHUNK_MODE == "raw":
                                    self._send_sse({"type": "delta", "content": delta})
                                    chunk_count += 1
                                else:
                                    # 按配置拆分成更小块，模拟逐字/逐块输出
                                    for piece in _iter_chunks(delta, STREAM_CHUNK_SIZE):
                                        self._send_sse({"type": "delta", "content": piece})
                                        chunk_count += 1
                                        if STREAM_CHUNK_DELAY > 0:
                                            await asyncio.sleep(STREAM_CHUNK_DELAY)
                                if first_delta_ms is None:
                                    first_delta_ms = int((time.monotonic() - stream_start) * 1000)
                                last_text = current_text
                        reply_msg = await reply_task
                        if reply_done_ms is None:
                            reply_done_ms = int((time.monotonic() - stream_start) * 1000)
                        # 收尾：从最终回复中提取文本内容，并补齐剩余部分
                        reply_text = _extract_text(getattr(reply_msg, "content", ""))
                        tail = _diff_text(reply_text, last_text)
                        if tail:
                            if STREAM_CHUNK_MODE == "raw":
                                self._send_sse({"type": "delta", "content": tail})
                                chunk_count += 1
                            else:
                                for piece in _iter_chunks(tail, STREAM_CHUNK_SIZE):
                                    self._send_sse({"type": "delta", "content": piece})
                                    chunk_count += 1
                                    if STREAM_CHUNK_DELAY > 0:
                                        await asyncio.sleep(STREAM_CHUNK_DELAY)
                            last_text = reply_text
                        stream_end_ms = int((time.monotonic() - stream_start) * 1000)
                        timing = {
                            "queue_first_ms": first_queue_ms,
                            "delta_first_ms": first_delta_ms,
                            "reply_done_ms": reply_done_ms,
                            "stream_end_ms": stream_end_ms,
                        }
                        return reply_text, chunk_count, timing
                    finally:
                        agent.set_msg_queue_enabled(False)

                reply_text, chunk_count, timing = asyncio.run(_stream_reply())
                _append_debug_log(
                    "stream_reply_extracted",
                    {"agent_id": agent_id, "session_id": session_id, "length": len(reply_text)},
                )
                _append_debug_log(
                    "stream_timing",
                    {
                        "agent_id": agent_id,
                        "session_id": session_id,
                        "queue_first_ms": timing.get("queue_first_ms"),
                        "delta_first_ms": timing.get("delta_first_ms"),
                        "reply_done_ms": timing.get("reply_done_ms"),
                        "stream_end_ms": timing.get("stream_end_ms"),
                        "chunks": chunk_count,
                    },
                )
                _append_debug_log(
                    "agent_reply_end",
                    {"agent_id": agent_id, "session_id": session_id, "length": len(reply_text)},
                )
                _append_debug_log(
                    "stream_chunks_sent",
                    {"agent_id": agent_id, "session_id": session_id, "chunks": chunk_count},
                )
                _append_message(agent_id, session_id, "user", content)
                _append_markdown(agent_id, session_id, "user", content)
                _append_chat_log(agent_id, session_id, "user", content)
                _append_message(agent_id, session_id, "assistant", reply_text)
                _append_markdown(agent_id, session_id, "assistant", reply_text)
                _append_chat_log(agent_id, session_id, "assistant", reply_text)
                _update_status(agent_id, "idle")
                messages = _get_messages(agent_id, session_id)
                self._send_sse({"type": "done", "messages": messages})
                _append_debug_log(
                    "stream_persisted",
                    {"agent_id": agent_id, "session_id": session_id, "messages": len(messages)},
                )
                _append_debug_log(
                    "http_post_chat_stream_done",
                    {"agent_id": agent_id, "session_id": session_id, "messages": len(messages)},
                )
            except Exception as e:
                _update_status(agent_id, "offline")
                self._send_sse({"type": "error", "message": str(e)})
                _append_debug_log(
                    "stream_exception",
                    {"agent_id": agent_id, "session_id": session_id, "error": str(e)},
                )
                _append_debug_log(
                    "http_post_chat_stream_error",
                    {"agent_id": agent_id, "session_id": session_id, "error": str(e)},
                )
            return
        if parsed.path != "/api/chat":
            self._send_json({"error": "not_found"}, status_code=404)
            return
        payload = self._read_body()
        agent_id = payload.get("agent_id") or "seraAgent"
        content = (payload.get("content") or "").strip()
        session_id = payload.get("session_id") or "default"
        _append_debug_log(
            "http_post_chat",
            {"agent_id": agent_id, "session_id": session_id, "length": len(content)},
        )
        if not content:
            self._send_json({"error": "empty_content"}, status_code=400)
            return
        try:
            _update_status(agent_id, "busy")
            agent = _get_agent(agent_id)
            try:
                from agentscope.message import Msg
            except Exception as e:
                _append_debug_log("agentscope_missing", {"error": str(e)})
                self._send_json({"error": "agentscope_missing", "detail": str(e)}, status_code=500)
                return
            msg = Msg(name="User", content=content, role="user")
            _append_debug_log("agent_reply_start", {"agent_id": agent_id, "session_id": session_id})
            response = asyncio.run(agent.reply(msg))
            reply_text = _extract_text(getattr(response, "content", ""))
            _append_debug_log(
                "agent_reply_end",
                {"agent_id": agent_id, "session_id": session_id, "length": len(reply_text)},
            )
            _append_message(agent_id, session_id, "user", content)
            _append_markdown(agent_id, session_id, "user", content)
            _append_chat_log(agent_id, session_id, "user", content)
            _append_message(agent_id, session_id, "assistant", reply_text)
            _append_markdown(agent_id, session_id, "assistant", reply_text)
            _append_chat_log(agent_id, session_id, "assistant", reply_text)
            _update_status(agent_id, "idle")
            messages = _get_messages(agent_id, session_id)
            self._send_json(
                {"agent_id": agent_id, "session_id": session_id, "reply": reply_text, "messages": messages}
            )
            _append_debug_log(
                "http_post_chat_done",
                {"agent_id": agent_id, "session_id": session_id, "messages": len(messages)},
            )
        except Exception as e:
            _update_status(agent_id, "offline")
            self._send_json({"error": "reply_failed", "detail": str(e)}, status_code=500)
            _append_debug_log(
                "http_post_chat_error",
                {"agent_id": agent_id, "session_id": session_id, "error": str(e)},
            )


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ApiHandler)
    _append_debug_log("server_started", {"host": host, "port": port})
    server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    _clear_chat_log()
    _clear_chat_store()
    _clear_agent_messages()
    serve()
