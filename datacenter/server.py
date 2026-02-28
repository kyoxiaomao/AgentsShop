import asyncio
import datetime
import importlib
import json
import logging
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

from datacenter.message import MessageService
from datacenter.service import build_ui_snapshot, snapshot_path

# 统一日志记录器
logger = logging.getLogger("datacenter")

# 目录与路径基础配置
BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)


# 兼容 Windows：将 venv 的 site-packages 与 pywin32 DLL 加入路径
def _bootstrap_venv_site_packages() -> None:
    site_packages = os.path.join(ROOT_DIR, ".venv", "Lib", "site-packages")
    if not os.path.isdir(site_packages):
        return
    dll_dir = os.path.join(site_packages, "pywin32_system32")
    if os.path.isdir(dll_dir):
        try:
            os.add_dll_directory(dll_dir)
        except Exception:
            pass
    extra_paths = [
        site_packages,
        os.path.join(site_packages, "win32"),
        os.path.join(site_packages, "win32", "lib"),
    ]
    for path in reversed(extra_paths):
        if path not in sys.path and os.path.isdir(path):
            sys.path.insert(0, path)
    try:
        # 强制标准输出为 UTF-8，避免 Windows 默认编码问题
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# 提前注入路径以便导入 agentscope 与其他依赖
_bootstrap_venv_site_packages()

# 运行时数据与日志路径
CHAT_STORE_FILE = os.path.join(BASE_DIR, "chat_store.json")
STATUS_FILE = os.path.join(BASE_DIR, "status.json")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
CHAT_LOG_FILE = os.path.join(LOGS_DIR, "chat.jsonl")
DEBUG_LOG_FILE = os.path.join(LOGS_DIR, "debug.jsonl")

# SSE 流式分片配置
STREAM_CHUNK_DELAY = float(os.getenv("STREAM_CHUNK_DELAY", "0.02"))
STREAM_CHUNK_SIZE = max(1, int(os.getenv("STREAM_CHUNK_SIZE", "1")))
STREAM_CHUNK_MODE = os.getenv("STREAM_CHUNK_MODE", "raw").lower()

# 各 Agent 的 markdown 消息目录
AGENT_MESSAGE_DIRS = {
    "seraAgent": os.path.join(ROOT_DIR, "agents", "queen", "Queen_Sera", "message"),
}

# Agent 类路径映射
AGENT_CLASS_PATHS = {
    "seraAgent": "agents.queen.Queen_Sera:SeraAgent",
}

# 已初始化的 Agent 实例缓存
AGENT_INSTANCES: dict[str, Any] = {}
# 全局消息服务实例（在下方初始化）
MESSAGE_SERVICE: MessageService


# 统一生成 UTC ISO 时间戳
def _now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

# 复用消息服务的文本清洗逻辑
def _strip_thinking_prefix(text: str) -> str:
    return MESSAGE_SERVICE.extract_text(text)

# 对外统一文本提取入口
def _extract_text(value) -> str:
    return MESSAGE_SERVICE.extract_text(value)

# 读取 JSON 文件
def _read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception as e:
        logger.error("read json failed %s %s", path, e)
        return default


# 写入 JSON 文件
def _write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 确保目录存在
def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


# 更新 Agent 状态并刷新 UI 快照
def _update_status(agent_id: str, status: str) -> None:
    data = _read_json(STATUS_FILE, {})
    data[agent_id] = {"status": status, "updated_at": _now_iso()}
    _write_json(STATUS_FILE, data)
    build_ui_snapshot()
    _append_debug_log("status_updated", {"agent_id": agent_id, "status": status})


# 追加 markdown 消息文件
def _append_markdown(agent_id: str, session_id: str, role: str, content: str) -> None:
    MESSAGE_SERVICE.append_markdown(agent_id, session_id, role, content)


# 读取会话存储
def _load_messages() -> dict:
    return _read_json(CHAT_STORE_FILE, {"version": 1, "sessions": {}})


# 保存会话存储
def _save_messages(store: dict) -> None:
    _write_json(CHAT_STORE_FILE, store)


# 追加会话消息并返回当前会话列表
def _append_message(agent_id: str, session_id: str, role: str, content: str) -> list[dict]:
    return MESSAGE_SERVICE.append_message(agent_id, session_id, role, content)


# 获取某个会话的消息列表
def _get_messages(agent_id: str, session_id: str) -> list[dict]:
    return MESSAGE_SERVICE.get_messages(agent_id, session_id)


# 追加统一聊天日志
def _append_chat_log(agent_id: str, session_id: str, role: str, content: str) -> None:
    MESSAGE_SERVICE.append_chat_log(agent_id, session_id, role, content)


# 追加调试日志（jsonl）
def _append_debug_log(event: str, payload: dict) -> None:
    _ensure_dir(LOGS_DIR)
    item = {"ts": _now_iso(), "event": event, **payload}
    with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


# 初始化消息服务
MESSAGE_SERVICE = MessageService(
    chat_store_file=CHAT_STORE_FILE,
    logs_dir=LOGS_DIR,
    chat_log_file=CHAT_LOG_FILE,
    debug_log_file=DEBUG_LOG_FILE,
    agent_message_dirs=AGENT_MESSAGE_DIRS,
    debug_logger=_append_debug_log,
)


# 清空聊天日志
def _clear_chat_log() -> None:
    MESSAGE_SERVICE.clear_chat_log()


# 清空聊天存储
def _clear_chat_store() -> None:
    MESSAGE_SERVICE.clear_chat_store()


# 清空 Agent 的 markdown 消息
def _clear_agent_messages() -> None:
    MESSAGE_SERVICE.clear_agent_messages()


# 将文本按长度切分为若干块
def _iter_chunks(text: str, size: int = 1):
    if not text:
        return
    for i in range(0, len(text), size):
        yield text[i : i + size]


# 计算新文本相对旧文本的增量部分
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


# 按配置动态加载并缓存 Agent 实例
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


# 构建并读取 UI 快照
def _ensure_snapshot() -> dict:
    build_ui_snapshot()
    path = snapshot_path()
    snapshot = _read_json(path, {"version": 1, "agents": [], "status": {}})
    _append_debug_log(
        "snapshot_loaded",
        {"agents": len(snapshot.get("agents", [])), "status": len(snapshot.get("status", {}))},
    )
    return snapshot


# HTTP 请求处理器
class ApiHandler(BaseHTTPRequestHandler):
    # 禁用默认日志输出
    def log_message(self, format, *args) -> None:
        return

    # 发送 JSON 响应
    def _send_json(self, data: dict, status_code: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    # 发送 SSE 消息
    def _send_sse(self, payload: dict) -> None:
        raw = f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
        self.wfile.write(raw)
        self.wfile.flush()

    # 读取 POST 请求体 JSON
    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    # 处理 GET 请求
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

    # 处理 POST 请求
    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/debug":
            # 前端调试日志入口
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
            # SSE 流式对话接口
            payload = self._read_body()
            agent_id = payload.get("agent_id") or "seraAgent"
            content = (payload.get("content") or "").strip()
            session_id = payload.get("session_id") or "default"
            mode = payload.get("mode") or "聊天"
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            _append_debug_log(
                "http_post_chat_stream",
                {"agent_id": agent_id, "session_id": session_id, "length": len(content), "mode": mode},
            )
            _append_debug_log("stream_opened", {"agent_id": agent_id, "session_id": session_id})
            if not content:
                _append_debug_log("stream_empty_content", {"agent_id": agent_id, "session_id": session_id})
                self._send_sse({"type": "error", "message": "empty_content"})
                return
            try:
                _update_status(agent_id, "busy")
                agent = _get_agent(agent_id)
                resolved_mode = str(mode).strip() or "聊天"
                # 聊天模式且 Agent 提供迭代式流输出：直接使用 OpenAI SDK 流式
                if resolved_mode == "聊天" and hasattr(agent, "iter_stream"):
                    _append_debug_log("agent_reply_start", {"agent_id": agent_id, "session_id": session_id})
                    _append_debug_log(
                        "stream_mode",
                        {"agent_id": agent_id, "session_id": session_id, "mode": "direct_openai"},
                    )
                    self._send_sse({"type": "start"})
                    reply_parts: list[str] = []
                    for delta in agent.iter_stream(content):
                        if not delta:
                            continue
                        reply_parts.append(delta)
                        if STREAM_CHUNK_MODE == "raw":
                            self._send_sse({"type": "delta", "content": delta})
                        else:
                            for piece in _iter_chunks(delta, STREAM_CHUNK_SIZE):
                                self._send_sse({"type": "delta", "content": piece})
                                if STREAM_CHUNK_DELAY > 0:
                                    time.sleep(STREAM_CHUNK_DELAY)
                    reply_text = "".join(reply_parts).strip()
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
                        "http_post_chat_stream_done",
                        {"agent_id": agent_id, "session_id": session_id, "messages": len(messages), "mode": resolved_mode},
                    )
                    return
                # 任务/工具模式：使用 agentscope 队列流式
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

                # 基于 agentscope 队列的流式输出包装
                async def _stream_reply():
                    # agent.reply 在后台推理，队列持续产出中间消息
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
                            # 从队列消息中提取文本内容并计算增量，避免重复输出
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
                        # 汇总关键时间点用于诊断
                        timing = {
                            "queue_first_ms": first_queue_ms,
                            "delta_first_ms": first_delta_ms,
                            "reply_done_ms": reply_done_ms,
                            "stream_end_ms": stream_end_ms,
                        }
                        return reply_text, chunk_count, timing
                    finally:
                        # 关闭队列能力，避免影响后续请求
                        agent.set_msg_queue_enabled(False)

                # 执行队列流式并落盘消息
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
                # 异常时更新状态并返回错误
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
        # 非流式对话接口
        payload = self._read_body()
        agent_id = payload.get("agent_id") or "seraAgent"
        content = (payload.get("content") or "").strip()
        session_id = payload.get("session_id") or "default"
        mode = payload.get("mode") or "聊天"
        _append_debug_log(
            "http_post_chat",
            {"agent_id": agent_id, "session_id": session_id, "length": len(content), "mode": mode},
        )
        if not content:
            self._send_json({"error": "empty_content"}, status_code=400)
            return
        try:
            _update_status(agent_id, "busy")
            agent = _get_agent(agent_id)
            resolved_mode = str(mode).strip() or "聊天"
            # 聊天模式走同步单轮对话
            if resolved_mode == "聊天" and hasattr(agent, "chat_once"):
                _append_debug_log("agent_reply_start", {"agent_id": agent_id, "session_id": session_id})
                _timing, reply_text = agent.chat_once(content)
                reply_text = _extract_text(reply_text)
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
                    {"agent_id": agent_id, "session_id": session_id, "messages": len(messages), "mode": resolved_mode},
                )
                return
            try:
                # 任务/工具模式走 agentscope reply
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
            # 异常时返回错误并记录日志
            _update_status(agent_id, "offline")
            self._send_json({"error": "reply_failed", "detail": str(e)}, status_code=500)
            _append_debug_log(
                "http_post_chat_error",
                {"agent_id": agent_id, "session_id": session_id, "error": str(e)},
            )


# 启动 HTTP 服务
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ApiHandler)
    _append_debug_log("server_started", {"host": host, "port": port})
    server.serve_forever()


# 本地直启入口
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    _clear_chat_log()
    _clear_chat_store()
    _clear_agent_messages()
    serve()
