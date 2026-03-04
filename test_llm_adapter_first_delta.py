import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.queen.Queen_Sera.sera_agent import SeraAgent
from models.llm_adapter import iter_openai_stream_deltas


def main() -> None:
    prompt = "你好，你是谁？"
    sera = SeraAgent()
    started_at = time.perf_counter()
    first_delta_ms = None
    chunks: list[str] = []

    stream = iter_openai_stream_deltas(
        base_url=sera._direct_base_url,
        api_key=sera._direct_api_key,
        model_name=sera._direct_model_name,
        messages=[
            {"role": "system", "content": sera._sys_prompt},
            {"role": "user", "content": prompt},
        ],
        generate_kwargs={"extra_body": {"enable_thinking": False}},
    )
    for delta in stream:
        text = "" if delta is None else str(delta)
        if not text:
            continue
        if first_delta_ms is None:
            first_delta_ms = (time.perf_counter() - started_at) * 1000
            print(f"first_delta_ms={first_delta_ms:.2f}")
        print(f"delta={text}")
        chunks.append(text)

    print(f"assistant_reply={''.join(chunks).strip()}")


if __name__ == "__main__":
    main()
