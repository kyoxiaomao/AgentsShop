import os
from typing import Any, Optional

from agentscope.formatter import OpenAIChatFormatter
from agentscope.model import OpenAIChatModel
from dotenv import find_dotenv, load_dotenv

DEFAULT_MODELSCOPE_MODEL_NAME = "ZhipuAI/GLM-5:DashScope"
DEFAULT_MODELSCOPE_BASE_URL = "https://api-inference.modelscope.cn/v1"


def load_project_dotenv(*, override: bool = False) -> None:
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, override=override)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"缺少环境变量 {name}（可在仓库根目录 .env 中配置）")
    return value


def create_openai_chat_model(
    *,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    client_kwargs: Optional[dict[str, Any]] = None,
) -> OpenAIChatModel:
    load_project_dotenv()

    resolved_api_key = api_key if api_key is not None else _require_env("MODELSCOPE_API_KEY")
    resolved_model_name = (
        model_name if model_name is not None else os.getenv("MODELSCOPE_MODEL_NAME", DEFAULT_MODELSCOPE_MODEL_NAME)
    )
    resolved_base_url = base_url if base_url is not None else os.getenv("MODELSCOPE_BASE_URL", DEFAULT_MODELSCOPE_BASE_URL)

    resolved_client_kwargs: dict[str, Any] = {"base_url": resolved_base_url}
    if client_kwargs:
        resolved_client_kwargs.update(client_kwargs)

    return OpenAIChatModel(
        model_name=resolved_model_name,
        api_key=resolved_api_key,
        client_kwargs=resolved_client_kwargs,
    )


def create_openai_chat_formatter() -> OpenAIChatFormatter:
    return OpenAIChatFormatter()

