import asyncio
import datetime
import importlib
import json
import socket
import tempfile
import unittest
from pathlib import Path

import websockets


def _allocate_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


class _FakeTaskAgent:
    def decompose_task(self, user_content: str) -> dict:
        return {
            "objective": f"完成任务：{user_content}",
            "key_results": ["拆解任务范围", "输出执行计划"],
        }


class TestOkrasService(unittest.TestCase):
    def test_daily_file_append(self) -> None:
        module = importlib.import_module("datacenter.service.okras.okras")
        service_cls = getattr(module, "OkrasService")
        with tempfile.TemporaryDirectory() as temp_dir:
            service = service_cls(storage_dir=temp_dir)
            created_at = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
            record = {
                "o_id": "o-1",
                "k_id": "k-1",
                "O": "完成任务",
                "K": "拆解子目标",
                "R": {"type": "text", "content": "已生成"},
                "A": "Lila",
                "S": {"score": 0, "rule": "okr_v1", "detail": "未执行"},
                "status": "planned",
                "session_id": "default",
                "source_mode": "任务",
                "created_at": created_at,
                "updated_at": created_at,
            }
            path_one = service.append_okras_records([record])
            record["k_id"] = "k-2"
            path_two = service.append_okras_records([record])
            self.assertEqual(path_one, path_two)
            self.assertTrue(Path(path_one).is_file())
            lines = Path(path_one).read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)


class TestTaskModeWs(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.host = "127.0.0.1"
        self.port = _allocate_port()
        server_module = importlib.import_module("datacenter.server")
        self.state = getattr(server_module, "ServerState")()

        okras_module = importlib.import_module("datacenter.service.okras.okras")
        okras_cls = getattr(okras_module, "OkrasService")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state.okras_service = okras_cls(storage_dir=self.temp_dir.name)
        self.state.agent_registry._instances["Lila"] = _FakeTaskAgent()

        handle_ws = getattr(server_module, "handle_ws")

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
        self.temp_dir.cleanup()

    async def test_task_mode_generates_daily_okras(self) -> None:
        uri = f"ws://{self.host}:{self.port}/ws"
        payload = {
            "type": "chat",
            "agent_id": "Lila",
            "session_id": "task-mode-test",
            "content": "请把这个需求拆分为可执行步骤",
            "mode": "任务",
        }

        task_summary = None
        done_messages = None
        async with websockets.connect(uri, ping_interval=None) as ws:
            await ws.send(json.dumps(payload, ensure_ascii=False))
            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=20)
                event = json.loads(raw)
                if event.get("type") == "task_summary":
                    task_summary = event
                    continue
                if event.get("type") == "done":
                    done_messages = event.get("messages")
                    break
                if event.get("type") == "error":
                    self.fail(f"server_error={event.get('code')} message={event.get('message')}")

        self.assertIsNotNone(task_summary)
        self.assertIsInstance(task_summary.get("key_results"), list)
        self.assertGreaterEqual(len(task_summary.get("key_results")), 1)
        okras_file_path = str(task_summary.get("okras_file_path") or "")
        self.assertTrue(Path(okras_file_path).is_file())
        self.assertIsInstance(done_messages, list)
        self.assertGreaterEqual(len(done_messages), 2)

