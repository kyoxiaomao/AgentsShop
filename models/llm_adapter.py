from typing import Any, Iterator

from openai import OpenAI


# OpenAI 流式输出增量解析器
def iter_openai_stream_deltas(
    *,
    base_url: str,
    api_key: str,
    model_name: str,
    messages: list[dict[str, Any]],
    generate_kwargs: dict[str, Any],
) -> Iterator[str]:
    # 仅使用直连 OpenAI 客户端
    client = OpenAI(base_url=base_url, api_key=api_key)
    # 流式返回，仅产出文本增量
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=True,
        **generate_kwargs,
    )
    for chunk in response:
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        text = getattr(delta, "content", None)
        if text:
            yield text

