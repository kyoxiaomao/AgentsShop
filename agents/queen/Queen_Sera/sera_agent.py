from typing import Any, Optional

from agents.base import BaseAgent


class SeraAgent(BaseAgent):
    def __init__(
        self,
        *,
        name: str = "seraAgent",
        sys_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        resolved_sys_prompt = (
            sys_prompt
            if sys_prompt is not None
            else "你是塞瑞（Sera），一个可靠、克制且善于协作的多智能体助手。你会用清晰的结构回答问题，并在不确定时主动补充假设与验证方式。"
        )
        super().__init__(
            name=name,
            cn_name="塞瑞",
            sys_prompt=resolved_sys_prompt,
            **kwargs,
        )

