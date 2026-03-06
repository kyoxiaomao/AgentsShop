import json
import threading


_lock = threading.Lock()
_toolkit = None


def ensure_toolkit_initialized():
    global _toolkit
    with _lock:
        if _toolkit is not None:
            return _toolkit
        from agentscope.tool import Toolkit

        toolkit = Toolkit()
        register_default_tools(toolkit)
        _toolkit = toolkit
        return toolkit


def register_default_tools(toolkit) -> None:
    from agentscope.tool import ToolResponse
    from utils.skills.task_breakdown import decompose_task_text

    def decompose_task(*, task: str) -> ToolResponse:
        data = decompose_task_text(task)
        text = json.dumps(data, ensure_ascii=False)
        return ToolResponse(content=[{"type": "text", "text": text}], metadata=data)

    toolkit.register_tool_function(decompose_task, namesake_strategy="skip")
