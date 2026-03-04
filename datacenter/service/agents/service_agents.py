import importlib
import json
import os
from typing import Any


DEFAULT_AGENT_CONFIG = {
    "agents": [
        {
            "id": "Sera",
            "name": "Sera",
            "cn_name": "塞瑞",
            "enabled": True,
            "class_path": "agents.queen.Queen_Sera.sera_agent:SeraAgent",
        }
    ]
}


def _load_agent_config() -> list[dict[str, Any]]:
    config_path = os.path.join(os.path.dirname(__file__), "agents_status.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        agents = data.get("agents")
        if isinstance(agents, list):
            return agents
    except Exception:
        pass
    return DEFAULT_AGENT_CONFIG["agents"]


class AgentRegistry:
    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self._mapping: dict[str, str] = {}
        self._meta: dict[str, dict[str, Any]] = {}
        if mapping is not None:
            self._mapping = dict(mapping)
        else:
            for item in _load_agent_config():
                agent_id = str(item.get("id") or "").strip()
                class_path = str(item.get("class_path") or "").strip()
                if not agent_id or not class_path:
                    continue
                self._mapping[agent_id] = class_path
                self._meta[agent_id] = {
                    "id": agent_id,
                    "name": str(item.get("name") or agent_id),
                    "cn_name": str(item.get("cn_name") or agent_id),
                    "enabled": bool(item.get("enabled", True)),
                }
        self._instances: dict[str, Any] = {}

    def _load_class(self, class_path: str):
        module_path, class_name = class_path.split(":")
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def get_agent(self, agent_id: str):
        if agent_id not in self._mapping:
            raise ValueError("unknown_agent")
        if agent_id not in self._instances:
            agent_cls = self._load_class(self._mapping[agent_id])
            self._instances[agent_id] = agent_cls()
        return self._instances[agent_id]

    def list_agents(self) -> list[dict]:
        agents: list[dict] = []
        for agent_id in self._mapping.keys():
            meta = self._meta.get(agent_id)
            if meta:
                agents.append(dict(meta))
                continue
            agent = self.get_agent(agent_id)
            agents.append(
                {
                    "id": agent_id,
                    "name": getattr(agent, "name", agent_id),
                    "cn_name": getattr(agent, "cn_name", agent_id),
                    "enabled": True,
                }
            )
        return agents
