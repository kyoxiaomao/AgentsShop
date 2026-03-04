import asyncio
import importlib
import json
import socket
import sys
import time
import types
import unittest
from pathlib import Path

import websockets

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_DATACENTER_DIR = _PROJECT_ROOT / "datacenter"
_DATACENTER_PKG = types.ModuleType("datacenter")
_DATACENTER_PKG.__path__ = [str(_DATACENTER_DIR)]
sys.modules["datacenter"] = _DATACENTER_PKG
_SERVER_MODULE = importlib.import_module("datacenter.server")
ServerState = _SERVER_MODULE.ServerState
handle_ws = _SERVER_MODULE.handle_ws


def _allocate_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


class TestUiLikeChatSera(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.host = "127.0.0.1"
        self.port = _allocate_port()
        self.state = ServerState()

        async def _ws_handler(ws) -> None:
            await handle_ws(self.state, ws)

        self._server = await websockets.serve(
            _ws_handler,
            self.host,
            self.port,
            ping_interval=None,
        )

    async def asyncTearDown(self) -> None:
        self._server.close()
        await self._server.wait_closed()

    async def test_ui_like_chat_with_sera_records_first_delta_time(self) -> None:
        uri = f"ws://{self.host}:{self.port}/ws"
        payload = {
            "type": "chat",
            "agent_id": "Sera",
            "session_id": "ui-like-test",
            "content": "你好你是谁",
            "mode": "聊天",
        }
        first_delta_ms = None
        chunks: list[str] = []
        done_messages = None
        started_at = time.perf_counter()

        async with websockets.connect(uri, ping_interval=None) as ws:
            await ws.send(json.dumps(payload, ensure_ascii=False))
            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=120)
                event = json.loads(raw)
                event_type = event.get("type")
                if event_type == "delta":
                    text = str(event.get("content") or "")
                    if text:
                        print(f"delta={text}")
                        chunks.append(text)
                        if first_delta_ms is None:
                            first_delta_ms = (time.perf_counter() - started_at) * 1000
                            print(f"first_delta_ms={first_delta_ms:.2f}")
                    continue
                if event_type == "done":
                    done_messages = event.get("messages")
                    break
                if event_type == "error":
                    self.fail(f"server_error={event.get('code')} message={event.get('message')}")

        self.assertIsNotNone(first_delta_ms, "未收到首个流式片段")
        full_reply = "".join(chunks).strip()
        print(f"assistant_reply={full_reply}")
        self.assertTrue(full_reply, "流式内容为空")
        self.assertIsInstance(done_messages, list, "done 事件未返回消息列表")
        self.assertGreaterEqual(len(done_messages), 2, "消息落盘数量异常")
