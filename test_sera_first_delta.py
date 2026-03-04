import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.queen.Queen_Sera.sera_agent import SeraAgent


def main() -> None:
    prompt = "你好，你是谁？"
    agent = SeraAgent()
    started_at = time.perf_counter()
    first_delta_ms = None
    chunks: list[str] = []

    for delta in agent.chat_stream(prompt):
        text = "" if delta is None else str(delta)
        if not text:
            continue
        if first_delta_ms is None:
            first_delta_ms = (time.perf_counter() - started_at) * 1000
            print(f"first_delta_ms={first_delta_ms:.2f}")
        print(f"delta={text}")
        chunks.append(text)

    full_reply = "".join(chunks).strip()
    print(f"assistant_reply={full_reply}")


if __name__ == "__main__":
    main()
