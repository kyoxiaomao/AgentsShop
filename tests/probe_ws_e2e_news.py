import asyncio
import datetime
import json
import time

import websockets


async def main() -> None:
    uri = "ws://127.0.0.1:8000/ws"
    payload = {
        "type": "chat",
        "agent_id": "Sera",
        "session_id": "default",
        "content": "今日新闻",
        "mode": "聊天",
    }
    started_at = time.perf_counter()
    async with websockets.connect(uri, ping_interval=None) as ws:
        await ws.send(json.dumps(payload, ensure_ascii=False))
        while True:
            raw = await ws.recv()
            event = json.loads(raw)
            kind = event.get("type")
            if kind == "delta":
                seq = int(event.get("seq") or 0)
                sent_ms = int(event.get("sent_ms_from_start") or 0)
                sent_ts = event.get("sent_ts")
                recv_ms = (time.perf_counter() - started_at) * 1000
                e2e_ms = None
                if isinstance(sent_ts, str):
                    sent_epoch = datetime.datetime.fromisoformat(sent_ts.replace("Z", "+00:00")).timestamp() * 1000
                    e2e_ms = time.time() * 1000 - sent_epoch
                print(f"seq={seq} sent_ms={sent_ms} recv_ms={recv_ms:.2f} e2e_ms={e2e_ms:.2f} len={len(str(event.get('content') or ''))}")
                continue
            if kind == "done":
                print("done")
                break
            if kind == "error":
                print(f"error={event.get('message')}")
                break


if __name__ == "__main__":
    asyncio.run(main())
