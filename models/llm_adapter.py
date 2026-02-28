import time
from typing import Any, Iterator, Optional

from agentscope.formatter import OpenAIChatFormatter
from agentscope.model import OpenAIChatModel
from openai import OpenAI

try:
    from agentscope.model import DashScopeChatModel
except Exception:
    DashScopeChatModel = None


# ===== LLM推理模型开始 =====

def create_openai_chat_client(
    *,
    base_url: str,
    api_key: str,
    client_kwargs: Optional[dict[str, Any]] = None,
) -> OpenAI:
    resolved_kwargs: dict[str, Any] = {"base_url": base_url, "api_key": api_key}
    if client_kwargs:
        resolved_kwargs.update(client_kwargs)
    return OpenAI(**resolved_kwargs)


def iter_openai_stream_deltas(
    *,
    client: OpenAI,
    model_name: str,
    messages: list[dict[str, Any]],
    request_kwargs: Optional[dict[str, Any]] = None,
) -> Iterator[str]:
    resolved_kwargs: dict[str, Any] = {"model": model_name, "messages": messages, "stream": True}
    if request_kwargs:
        resolved_kwargs.update(request_kwargs)
    response = client.chat.completions.create(**resolved_kwargs)
    for chunk in response:
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        text = getattr(delta, "content", None)
        if text:
            yield text


def openai_chat_once_with_timing(
    *,
    base_url: str,
    api_key: str,
    model_name: str,
    messages: list[dict[str, Any]],
    client_kwargs: Optional[dict[str, Any]] = None,
    request_kwargs: Optional[dict[str, Any]] = None,
) -> tuple[dict[str, Any], str]:
    start = time.monotonic()
    client = create_openai_chat_client(base_url=base_url, api_key=api_key, client_kwargs=client_kwargs)

    chunks = 0
    first_chunk_ms = None
    first_answer_ms = None
    answer_parts: list[str] = []

    resolved_kwargs: dict[str, Any] = {"model": model_name, "messages": messages, "stream": True}
    if request_kwargs:
        resolved_kwargs.update(request_kwargs)
    response = client.chat.completions.create(**resolved_kwargs)

    for chunk in response:
        chunks += 1
        now_ms = int((time.monotonic() - start) * 1000)
        if first_chunk_ms is None:
            first_chunk_ms = now_ms
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        answer = getattr(delta, "content", None)
        if answer:
            answer_parts.append(answer)
            if first_answer_ms is None:
                first_answer_ms = now_ms

    total_ms = int((time.monotonic() - start) * 1000)
    timing = {
        "chunks": chunks,
        "first_chunk_ms": first_chunk_ms,
        "first_answer_ms": first_answer_ms,
        "total_ms": total_ms,
    }
    return timing, "".join(answer_parts).strip()


# ===== LLM推理模型结束 =====


# ===== LLM对话模型开始 =====

def create_openai_task_model(
    *,
    model_name: str,
    api_key: str,
    base_url: str,
    client_kwargs: Optional[dict[str, Any]] = None,
    generate_kwargs: Optional[dict[str, Any]] = None,
    stream_tool_parsing: bool = True,
) -> OpenAIChatModel:
    resolved_client_kwargs: dict[str, Any] = {"base_url": base_url}
    if client_kwargs:
        resolved_client_kwargs.update(client_kwargs)
    return OpenAIChatModel(
        model_name=model_name,
        api_key=api_key,
        client_kwargs=resolved_client_kwargs,
        generate_kwargs=generate_kwargs,
        stream_tool_parsing=stream_tool_parsing,
    )


def create_dashscope_chat_model(
    *,
    model_name: str,
    api_key: str,
    stream: bool = True,
    enable_thinking: Optional[bool] = None,
    generate_kwargs: Optional[dict[str, Any]] = None,
    base_http_api_url: Optional[str] = None,
    stream_tool_parsing: bool = True,
):
    if DashScopeChatModel is None:
        raise RuntimeError("DashScopeChatModel 不可用：当前 agentscope 版本未包含该模型封装")
    return DashScopeChatModel(
        model_name=model_name,
        api_key=api_key,
        stream=stream,
        enable_thinking=enable_thinking,
        generate_kwargs=generate_kwargs,
        base_http_api_url=base_http_api_url,
        stream_tool_parsing=stream_tool_parsing,
    )


def create_openai_chat_formatter() -> OpenAIChatFormatter:
    return OpenAIChatFormatter()


# ===== LLM对话模型结束 =====


create_openai_client = create_openai_chat_client
create_openai_chat_model = create_openai_task_model

