import asyncio
from typing import Any, Iterator, Optional

from agents.base.base_agent import BaseAgent
from utils.skills.task_breakdown import decompose_task_text
from utils.toolkit_registry import ensure_toolkit_initialized


class ReActAgentBase(BaseAgent):
    def __init__(
        self,
        *,
        name: str,
        sys_prompt: str,
        cn_name: Optional[str] = None,
        model_name: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        max_iters: int = 10,
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, sys_prompt=sys_prompt, cn_name=cn_name, **kwargs)
        self._model_name = str(model_name or "").strip()
        self._api_key = str(api_key or "").strip()
        self._base_url = str(base_url or "").strip()
        self._max_iters = int(max_iters)
        self._react_agent = None

    def _ensure_react_agent(self):
        if self._react_agent is not None:
            return self._react_agent
        if not (self._model_name and self._api_key and self._base_url):
            return None
        from agentscope.agent import ReActAgent
        from agentscope.formatter import OpenAIChatFormatter
        from agentscope.model import OpenAIChatModel

        toolkit = ensure_toolkit_initialized()
        model = OpenAIChatModel(
            model_name=self._model_name,
            api_key=self._api_key,
            client_kwargs={"base_url": self._base_url},
        )
        formatter = OpenAIChatFormatter()
        self._react_agent = ReActAgent(
            name=str(self.name or "agent"),
            sys_prompt=str(self.sys_prompt or ""),
            model=model,
            formatter=formatter,
            toolkit=toolkit,
            max_iters=self._max_iters,
        )
        return self._react_agent

    def _run_async(self, coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def chat_stream(self, user_content: str) -> Iterator[str]:
        agent = self._ensure_react_agent()
        if agent is None:
            yield "Agent 未配置 AGENTSCOPE_MODEL_NAME/AGENTSCOPE_BASE_URL/AGENTSCOPE_API_KEY，无法启动 ReAct。"
            return
        from agentscope.message import Msg

        msg = Msg(name="user", content=str(user_content or ""), role="user")
        reply_msg = self._run_async(agent.reply(msg=msg))
        text = ""
        if reply_msg is not None and hasattr(reply_msg, "get_text_content"):
            text = reply_msg.get_text_content() or ""
        if not text:
            text = str(getattr(reply_msg, "content", "") or "")
        if not text:
            text = "（空响应）"
        yield text

    def decompose_task(self, user_content: str) -> dict[str, Any]:
        return decompose_task_text(user_content)
