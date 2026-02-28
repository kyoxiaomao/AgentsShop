from typing import Any, Literal, Optional

from agents.base import BaseAgent

from models.llm_adapter import (
    create_dashscope_chat_model,
    create_openai_chat_formatter,
    create_openai_chat_model,
    iter_openai_stream_deltas,
    openai_chat_once_with_timing,
)


class SeraAgent(BaseAgent):
    def __init__(
        self,
        *,
        name: str = "seraAgent",
        sys_prompt: Optional[str] = None,
        backend: Literal["agentscope_openai", "direct_openai", "agentscope_dashscope"] = "agentscope_openai",
        dashscope_model_name: Optional[str] = None,
        dashscope_api_key: Optional[str] = None,
        dashscope_base_http_api_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        resolved_sys_prompt = (
            sys_prompt
            if sys_prompt is not None
            else "你是塞瑞（Sera），一个可靠、克制且善于协作的多智能体助手。你会用清晰的结构回答问题，并在不确定时主动补充假设与验证方式。"
        )
        model_name = "ZhipuAI/GLM-5"
        api_key = "ms-def9d31b-9844-493d-8b22-df43857a4c3c"
        base_url = "https://api-inference.modelscope.cn/v1"

        # 采样参数：更小的 temperature/top_p 会更稳定、更快
        generate_kwargs: dict[str, Any] = {}  # 生成参数容器（OpenAI 兼容字段）
        generate_kwargs["temperature"] = 0.8 # 温度：控制随机性，常见默认 0.7~1.0
        generate_kwargs["top_p"] = 0.9  # 核采样：保留概率累积，常见默认 0.9
        generate_kwargs["max_tokens"] = 1024  # 最大输出：常见默认 1024 或 2048

        self._backend = backend
        self._direct_base_url = base_url
        self._direct_api_key = api_key
        self._direct_model_name = model_name
        self._direct_generate_kwargs = generate_kwargs
        self._sys_prompt = resolved_sys_prompt

        if backend == "agentscope_dashscope":
            if not dashscope_model_name or not dashscope_api_key:
                raise ValueError("使用 agentscope_dashscope 时必须传入 dashscope_model_name/dashscope_api_key")
            model = create_dashscope_chat_model(
                model_name=dashscope_model_name,
                api_key=dashscope_api_key,
                stream=True,
                generate_kwargs=generate_kwargs,
                base_http_api_url=dashscope_base_http_api_url,
                stream_tool_parsing=False,
            )
        else:
            model = create_openai_chat_model(
                model_name=model_name,
                api_key=api_key,
                base_url=base_url,
                client_kwargs={"base_url": base_url},
                generate_kwargs=generate_kwargs,
                stream_tool_parsing=False,
            )

        super().__init__(
            name=name,
            cn_name="塞瑞",
            sys_prompt=resolved_sys_prompt,
            model=model,
            formatter=create_openai_chat_formatter(),
            **kwargs,
        )

    @property
    def backend(self) -> str:
        return self._backend

    def chat_once(self, user_content: str) -> tuple[dict[str, Any], str]:
        messages = [
            {"role": "system", "content": self._sys_prompt},
            {"role": "user", "content": user_content},
        ]
        return openai_chat_once_with_timing(
            base_url=self._direct_base_url,
            api_key=self._direct_api_key,
            model_name=self._direct_model_name,
            messages=messages,
            request_kwargs=self._direct_generate_kwargs,
        )

    def iter_stream(self, user_content: str):
        messages = [
            {"role": "system", "content": self._sys_prompt},
            {"role": "user", "content": user_content},
        ]
        from models.llm_adapter import create_openai_client

        client = create_openai_client(base_url=self._direct_base_url, api_key=self._direct_api_key)
        return iter_openai_stream_deltas(
            client=client,
            model_name=self._direct_model_name,
            messages=messages,
            request_kwargs=self._direct_generate_kwargs,
        )
