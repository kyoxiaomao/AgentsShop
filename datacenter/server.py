import asyncio
import datetime
import json
import os
from functools import partial
from typing import Any
from urllib.parse import parse_qs, urlsplit

import websockets

from datacenter.service.agents.service_agents import AgentRegistry
from datacenter.service.message.message import MessageService


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
        # Agent 状态映射
        self._status_map: dict[str, dict[str, str]] = {}

    def _resolve_msgdata_dir(self) -> str:
        # 消息落盘目录
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_dir, "msgdata")

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


def build_json_response(payload: dict[str, Any], status: int = 200):
    # 构造 HTTP JSON 响应
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Headers", "Content-Type"),
        ("Access-Control-Allow-Methods", "GET, OPTIONS"),
    ]
    return status, headers, body


async def handle_chat(state: ServerState, ws, payload: dict[str, Any]) -> None:
    # 处理 chat 请求并流式返回
    agent_id = str(payload.get("agent_id") or "").strip()
    content = str(payload.get("content") or "")
    session_id = str(payload.get("session_id") or "default")
    mode = payload.get("mode")

    if not agent_id:
        await send_json(ws, {"type": "error", "code": "missing_agent", "message": "agent_id_required"})
        return

    if not content:
        await send_json(ws, {"type": "error", "code": "missing_content", "message": "content_required"})
        return

    try:
        state.set_status(agent_id, "busy")
        state.message_service.append_message(agent_id, session_id, "user", content)
        assistant_content = ""
        for delta in state.message_service.stream_chat(agent_id, content, mode):
            text = "" if delta is None else str(delta)
            if not text:
                continue
            assistant_content += text
            await send_json(ws, {"type": "delta", "content": text})
        state.message_service.append_message(agent_id, session_id, "assistant", assistant_content)
        state.set_status(agent_id, "idle")
        messages = state.message_service.get_messages(agent_id, session_id)
        await send_json(ws, {"type": "done", "messages": messages})
    except Exception as error:
        state.set_status(agent_id, "idle")
        await send_json(ws, {"type": "error", "code": "chat_failed", "message": str(error)})


async def handle_ws(state: ServerState, ws, _path: str) -> None:
    # WebSocket 主循环
    async for raw in ws:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore")
        try:
            payload = json.loads(raw)
        except Exception:
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
            return build_json_response(
                {"error": "agent_id_required"},
                status=400,
            )
        messages = state.message_service.get_messages(agent_id, session_id)
        return build_json_response({"messages": messages})

    return build_json_response({"error": "not_found"}, status=404)


def process_request(state: ServerState, path: str, _request_headers):
    # 处理 WebSocket 之外的 HTTP 请求
    if path.startswith("/api/"):
        return handle_http_request(state, path)
    return None


async def serve(host: str, port: int) -> None:
    # 启动混合模式：HTTP 查询 + WebSocket 流式
    state = ServerState()
    handler = partial(handle_ws, state)
    http_handler = partial(process_request, state)
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
