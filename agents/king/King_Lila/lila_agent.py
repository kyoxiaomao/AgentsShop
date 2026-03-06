import os
from typing import Any, Optional

from agents.base import ReActAgentBase


class LilaAgent(ReActAgentBase):
    def __init__(
        self,
        *,
        name: str = "Lila",
        sys_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        resolved_sys_prompt = (
            sys_prompt
            if sys_prompt is not None
            else "你是莉拉（Lila），一个以 ReAct 为核心、善于调用工具解决任务的智能体。你会先拆解任务、再选择合适工具执行，最后输出可验证结果。"
        )
           model_name = "glm-5"
        api_key = "sk-1c388ebc51da4e9ca6f7993d2d3ad7b1"
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        super().__init__(
            name=name,
            cn_name="莉拉",
            sys_prompt=resolved_sys_prompt,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )
