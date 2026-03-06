from typing import Any, Optional


class BaseAgent:
    def __init__(
        self,
        *,
        name: str,
        sys_prompt: str,
        cn_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.sys_prompt = sys_prompt
        self.cn_name = cn_name

    def decompose_task(self, user_content: str) -> dict[str, Any]:
        raise NotImplementedError("decompose_task_not_implemented")
