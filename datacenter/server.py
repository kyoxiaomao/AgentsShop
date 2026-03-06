import asyncio
import datetime
import json
import os
import time
import uuid
from functools import partial
from typing import Any
from urllib.parse import parse_qs, urlsplit

import websockets
from websockets.datastructures import Headers
from websockets.http11 import Response

from datacenter.service.agents.service_agents import AgentRegistry
from datacenter.service.message.message import MessageService
from datacenter.service.okras.okras import OkrasService


def _server_log_file() -> str:
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "server_debug.jsonl")


def _log_server_event(event: str, data: dict[str, Any] | None = None) -> None:
    payload = {
        "ts": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
        "event": event,
        "data": data or {},
    }
    try:
        with open(_server_log_file(), "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


class ServerState:
    # 服务端状态：缓存 Agent 注册中心、消息服务与状态表
    def __init__(self) -> None:
        # Agent 注册中心
        self.agent_registry = AgentRegistry()
        # 消息服务
        self.message_service = MessageService(
            agent_registry=self.agent_registry,
            msgdata_dir=self._resolve_msgdata_dir(),
        )
        from utils.toolkit_registry import ensure_toolkit_initialized

        ensure_toolkit_initialized()
        self.okras_service = OkrasService(storage_dir=self._resolve_okras_dir())
        # Agent 状态映射
        self._status_map: dict[str, dict[str, str]] = {}

    def _resolve_msgdata_dir(self) -> str:
        # 消息落盘目录
        return os.path.join(os.path.dirname(__file__), "service", "message", "msgdata")

    def _resolve_okras_dir(self) -> str:
        project_root = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(project_root, "tasks", "okras")

    def _now_iso(self) -> str:
        # 统一使用 UTC ISO 时间戳
        return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

    def set_status(self, agent_id: str, status: str) -> None:
        # 更新单个 Agent 状态
        self._status_map[agent_id] = {"status": status, "updated_at": self._now_iso()}

    def get_status_map(self) -> dict[str, dict[str, str]]:
        # 读取状态映射的拷贝
        return dict(self._status_map)


async def send_json(ws, payload: dict[str, Any]) -> None:
    # WebSocket 发送 JSON
    await ws.send(json.dumps(payload, ensure_ascii=False))


def _reason_phrase(status: int) -> str:
    if status == 200:
        return "OK"
    if status == 400:
        return "Bad Request"
    if status == 404:
        return "Not Found"
    return "Error"


def build_json_response(payload: dict[str, Any], status: int = 200) -> Response:
    # 构造 HTTP JSON 响应
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = Headers()
    headers["Content-Type"] = "application/json; charset=utf-8"
    headers["Content-Length"] = str(len(body))
    headers["Access-Control-Allow-Origin"] = "*"
    headers["Access-Control-Allow-Headers"] = "Content-Type"
    headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return Response(status, _reason_phrase(status), headers, body)


async def handle_chat(state: ServerState, ws, payload: dict[str, Any]) -> None:
    # 处理 chat 请求并流式返回
    agent_id = str(payload.get("agent_id") or "").strip()
    content = str(payload.get("content") or "")
    session_id = str(payload.get("session_id") or "default")
    mode = str(payload.get("mode") or "聊天").strip()

    if not agent_id:
        await send_json(ws, {"type": "error", "code": "missing_agent", "message": "agent_id_required"})
        return

    if not content:
        await send_json(ws, {"type": "error", "code": "missing_content", "message": "content_required"})
        return

    if mode == "任务":
        await handle_task_chat(state, ws, agent_id=agent_id, content=content, session_id=session_id, mode=mode)
        return

    try:
        _log_server_event(
            "chat:start",
            {"agent_id": agent_id, "session_id": session_id, "mode": mode},
        )
        started_at = time.perf_counter()
        first_delta_ms: int | None = None
        prev_delta_at = started_at
        state.set_status(agent_id, "busy")
        state.message_service.append_message(agent_id, session_id, "user", content)
        assistant_content = ""
        delta_count = 0
        stream_iter = iter(state.message_service.stream_chat(agent_id, content))
        stream_end = object()
        while True:
            delta = await asyncio.to_thread(next, stream_iter, stream_end)
            if delta is stream_end:
                break
            text = "" if delta is None else str(delta)
            if not text:
                continue
            now = time.perf_counter()
            delta_count += 1
            sent_ts = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
            sent_ms_from_start = max(0, round((now - started_at) * 1000))
            if first_delta_ms is None:
                first_delta_ms = sent_ms_from_start
                _log_server_event(
                    "chat:first_delta",
                    {
                        "agent_id": agent_id,
                        "session_id": session_id,
                        "ms": first_delta_ms,
                        "len": len(text),
                        "preview": text[:30],
                    },
                )
            if delta_count <= 3:
                _log_server_event(
                    "chat:delta_probe",
                    {
                        "agent_id": agent_id,
                        "session_id": session_id,
                        "idx": delta_count,
                        "len": len(text),
                        "since_start_ms": sent_ms_from_start,
                        "gap_ms": max(0, round((now - prev_delta_at) * 1000)),
                        "preview": text[:30],
                    },
                )
            prev_delta_at = now
            assistant_content += text
            await send_json(
                ws,
                {
                    "type": "delta",
                    "content": text,
                    "seq": delta_count,
                    "sent_ts": sent_ts,
                    "sent_ms_from_start": sent_ms_from_start,
                },
            )
        state.message_service.append_message(agent_id, session_id, "assistant", assistant_content)
        state.set_status(agent_id, "idle")
        messages = state.message_service.get_messages(agent_id, session_id)
        await send_json(ws, {"type": "done", "messages": messages})
        _log_server_event(
            "chat:done",
            {
                "agent_id": agent_id,
                "session_id": session_id,
                "delta_count": delta_count,
                "assistant_chars": len(assistant_content),
                "messages_count": len(messages),
                "first_delta_ms": first_delta_ms,
                "total_ms": max(0, round((time.perf_counter() - started_at) * 1000)),
            },
        )
    except Exception as error:
        state.set_status(agent_id, "idle")
        await send_json(ws, {"type": "error", "code": "chat_failed", "message": str(error)})
        _log_server_event(
            "chat:error",
            {
                "agent_id": agent_id,
                "session_id": session_id,
                "mode": mode,
                "error": str(error),
            },
        )


async def handle_task_chat(
    state: ServerState,
    ws,
    *,
    agent_id: str,
    content: str,
    session_id: str,
    mode: str,
) -> None:
    try:
        state.set_status(agent_id, "busy")
        state.message_service.append_message(agent_id, session_id, "user", content)
        _log_server_event("task:start", {"agent_id": agent_id, "session_id": session_id, "mode": mode})

        agent = state.agent_registry.get_agent(agent_id)
        if hasattr(agent, "decompose_task"):
            task_data = await asyncio.to_thread(agent.decompose_task, content)
        else:
            from utils.skills.task_breakdown import decompose_task_text

            task_data = decompose_task_text(content)

        objective = str(task_data.get("objective") or "").strip() or "完成用户任务并给出可验证结果"
        raw_key_results = task_data.get("key_results")
        key_results: list[str] = []
        if isinstance(raw_key_results, list):
            for item in raw_key_results:
                text = str(item or "").strip()
                if text:
                    key_results.append(text)
        if not key_results:
            key_results = ["完成任务执行并输出可复用结果"]

        created_at = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
        o_id = f"o-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        records: list[dict[str, Any]] = []
        for key_result in key_results:
            records.append(
                {
                    "o_id": o_id,
                    "k_id": f"k-{uuid.uuid4().hex}",
                    "O": objective,
                    "K": key_result,
                    "R": {"type": "text", "content": "已生成子目标，待执行"},
                    "A": agent_id,
                    "S": {"score": 0, "rule": "okr_v1", "detail": "任务拆解阶段未执行"},
                    "status": "planned",
                    "session_id": session_id,
                    "source_mode": mode,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            )
        okras_file_path = await asyncio.to_thread(state.okras_service.append_okras_records, records)

        assistant_content = "\n".join(
            [
                f"任务目标（O）：{objective}",
                "关键结果（K）：",
                *[f"{idx + 1}. {value}" for idx, value in enumerate(key_results)],
                f"已写入：{okras_file_path}",
            ]
        )
        state.message_service.append_message(agent_id, session_id, "assistant", assistant_content)
        state.set_status(agent_id, "idle")
        await send_json(
            ws,
            {
                "type": "task_summary",
                "objective": objective,
                "key_results": key_results,
                "okras_file_path": okras_file_path,
            },
        )
        messages = state.message_service.get_messages(agent_id, session_id)
        await send_json(ws, {"type": "done", "messages": messages})
        _log_server_event(
            "task:done",
            {
                "agent_id": agent_id,
                "session_id": session_id,
                "okras_file_path": okras_file_path,
                "key_results_count": len(key_results),
            },
        )
    except Exception as error:
        state.set_status(agent_id, "idle")
        await send_json(ws, {"type": "error", "code": "task_failed", "message": str(error)})
        _log_server_event(
            "task:error",
            {"agent_id": agent_id, "session_id": session_id, "error": str(error)},
        )


async def handle_ws(state: ServerState, ws) -> None:
    # WebSocket 主循环
    peer = getattr(ws, "remote_address", None)
    _log_server_event("ws:open", {"peer": str(peer)})
    try:
        async for raw in ws:
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="ignore")
            try:
                payload = json.loads(raw)
            except Exception:
                _log_server_event("ws:invalid_json", {"peer": str(peer)})
                await send_json(ws, {"type": "error", "code": "invalid_json", "message": "invalid_json"})
                continue

            msg_type = payload.get("type")
            if msg_type == "ping":
                await send_json(ws, {"type": "pong"})
                continue
            if msg_type == "chat":
                await handle_chat(state, ws, payload)
                continue

            await send_json(ws, {"type": "error", "code": "unknown_type", "message": "unknown_type"})
    except Exception as error:
        _log_server_event("ws:error", {"peer": str(peer), "error": str(error)})
        raise
    finally:
        _log_server_event("ws:close", {"peer": str(peer)})


def handle_http_request(state: ServerState, path: str):
    # 处理 HTTP 请求（仅支持只读查询）
    route = urlsplit(path)
    if route.path == "/api/agents":
        agents = state.agent_registry.list_agents()
        payload = {"agents": agents, "status": state.get_status_map()}
        return build_json_response(payload)

    if route.path == "/api/messages":
        query = parse_qs(route.query or "")
        agent_id = (query.get("agent_id") or [""])[0]
        session_id = (query.get("session_id") or ["default"])[0]
        if not agent_id:
            _log_server_event("http:messages_bad_request", {"path": path})
            return build_json_response(
                {"error": "agent_id_required"},
                status=400,
            )
        messages = state.message_service.get_messages(agent_id, session_id)
        return build_json_response({"messages": messages})

    _log_server_event("http:not_found", {"path": path})
    return build_json_response({"error": "not_found"}, status=404)


def process_request(state: ServerState, _conn, request):
    # 处理 WebSocket 之外的 HTTP 请求
    path = str(getattr(request, "path", "") or "")
    if path.startswith("/api/"):
        return handle_http_request(state, path)
    return None


async def serve(host: str, port: int) -> None:
    # 启动混合模式：HTTP 查询 + WebSocket 流式
    state = ServerState()
    handler = partial(handle_ws, state)
    http_handler = partial(process_request, state)
    _log_server_event("server:start", {"host": host, "port": port})
    async with websockets.serve(
        handler,
        host,
        port,
        ping_interval=None,
        process_request=http_handler,
    ):
        await asyncio.Future()


def run() -> None:
    # 服务入口
    host = "127.0.0.1"
    port = 8000
    asyncio.run(serve(host, port))


if __name__ == "__main__":
    run()
