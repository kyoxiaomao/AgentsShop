import importlib
from typing import Any


AGENT_CLASS_PATHS = {
    "seraAgent": "agents.queen.Queen_Sera.sera_agent:SeraAgent",
}


class AgentRegistry:
    # Agent 注册中心：按配置加载并缓存实例
    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        # Agent 类路径映射
        self._mapping = mapping or AGENT_CLASS_PATHS
        # 已初始化的 Agent 实例缓存
        self._instances: dict[str, Any] = {}

    def _load_class(self, class_path: str):
        # 动态导入 Agent 类
        module_path, class_name = class_path.split(":")
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def get_agent(self, agent_id: str):
        # 获取或初始化 Agent 实例
        if agent_id not in self._mapping:
            raise ValueError("unknown_agent")
        if agent_id not in self._instances:
            agent_cls = self._load_class(self._mapping[agent_id])
            self._instances[agent_id] = agent_cls()
        return self._instances[agent_id]

    def list_agents(self) -> list[dict]:
        # 生成对外可用的 Agent 列表
        agents: list[dict] = []
        for agent_id in self._mapping.keys():
            agent = self.get_agent(agent_id)
            name = getattr(agent, "name", agent_id)
            cn_name = getattr(agent, "cn_name", agent_id)
            agents.append(
                {
                    "id": agent_id,
                    "name": name,
                    "cn_name": cn_name,
                    "enabled": True,
                }
            )
        return agents
