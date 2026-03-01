import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import time

from agents.queen.Queen_Sera.sera_agent import SeraAgent


def main() -> int:
    agent = SeraAgent()
    start = time.monotonic()
    chunks = 0
    first_chunk_ms = None
    first_answer_ms = None
    answer_parts: list[str] = []
    for delta in agent.chat_stream("你好你是谁"):
        chunks += 1
        now_ms = int((time.monotonic() - start) * 1000)
        if first_chunk_ms is None:
            first_chunk_ms = now_ms
        if first_answer_ms is None:
            first_answer_ms = now_ms
        answer_parts.append(delta)
    total_ms = int((time.monotonic() - start) * 1000)
    print("首片段耗时(ms):", first_chunk_ms)
    print("首回复耗时(ms):", first_answer_ms)
    print("完整回复耗时(ms):", total_ms)
    print("\n回复内容:\n", "".join(answer_parts).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
