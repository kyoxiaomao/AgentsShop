from typing import Any, Optional

from agentscope.agent import ReActAgent
from agentscope.formatter import OpenAIChatFormatter
from agentscope.model import OpenAIChatModel

from models.llm_adapter import create_openai_chat_formatter, create_openai_chat_model


class BaseAgent(ReActAgent):
    def __init__(
        self,
        *,
        name: str,
        sys_prompt: str,
        cn_name: Optional[str] = None,
        model: Optional[OpenAIChatModel] = None,
        formatter: Optional[OpenAIChatFormatter] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        client_kwargs: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        resolved_formatter = formatter if formatter is not None else create_openai_chat_formatter()
        resolved_model = (
            model
            if model is not None
            else create_openai_chat_model(
                model_name=model_name,
                api_key=api_key,
                base_url=base_url,
                client_kwargs=client_kwargs,
            )
        )

        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model=resolved_model,
            formatter=resolved_formatter,
            **kwargs,
        )

        self.cn_name = cn_name

