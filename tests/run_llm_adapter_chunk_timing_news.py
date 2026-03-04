import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.queen.Queen_Sera.sera_agent import SeraAgent
from models.llm_adapter import iter_openai_stream_deltas


def main() -> None:
    prompt = "今日新闻"
    agent = SeraAgent()
    started_at = time.perf_counter()
    last_at = started_at
    chunk_count = 0
    chars = 0

    stream = iter_openai_stream_deltas(
        base_url=agent._direct_base_url,
        api_key=agent._direct_api_key,
        model_name=agent._direct_model_name,
        messages=[
            {"role": "system", "content": agent._sys_prompt},
            {"role": "user", "content": prompt},
        ],
        generate_kwargs={"extra_body": {"enable_thinking": False}},
    )

    for chunk in stream:
        text = "" if chunk is None else str(chunk)
        if not text:
            continue
        now = time.perf_counter()
        chunk_count += 1
        chars += len(text)
        since_start_ms = (now - started_at) * 1000
        gap_ms = (now - last_at) * 1000
        print(
            f"chunk={chunk_count} since_start_ms={since_start_ms:.2f} "
            f"gap_ms={gap_ms:.2f} len={len(text)} text={text}"
        )
        last_at = now

    total_ms = (time.perf_counter() - started_at) * 1000
    print(f"summary chunk_count={chunk_count} chars={chars} total_ms={total_ms:.2f}")


if __name__ == "__main__":
    main()
