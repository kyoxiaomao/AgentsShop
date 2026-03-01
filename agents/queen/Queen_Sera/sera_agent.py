import time
from typing import Any, Optional

from agents.base import BaseAgent

from models.llm_adapter import iter_openai_stream_deltas


class SeraAgent(BaseAgent):
    def __init__(
        self,
        *,
        name: str = "Sera",
        sys_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        resolved_sys_prompt = (
            sys_prompt
            if sys_prompt is not None
            else "你是塞瑞（Sera），一个可靠、克制且善于协作的多智能体助手。你会用清晰的结构回答问题，并在不确定时主动补充假设与验证方式。"
        )
        model_name = "glm-5"
        api_key = "sk-1c388ebc51da4e9ca6f7993d2d3ad7b1"
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        self._direct_base_url = base_url
        self._direct_api_key = api_key
        self._direct_model_name = model_name
        self._sys_prompt = resolved_sys_prompt

        super().__init__(
            name=name,
            cn_name="塞瑞",
            sys_prompt=resolved_sys_prompt,
            **kwargs,
        )

    def chat_stream(self, user_content: str):
        messages = [
            {"role": "system", "content": self._sys_prompt},
            {"role": "user", "content": user_content},
        ]
        return iter_openai_stream_deltas(
            base_url=self._direct_base_url,
            api_key=self._direct_api_key,
            model_name=self._direct_model_name,
            messages=messages,
            generate_kwargs={"extra_body": {"enable_thinking": False}},
        )
