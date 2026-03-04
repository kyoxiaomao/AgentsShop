import datetime
import json
import os
from typing import Iterable

from datacenter.service.agents.service_agents import AgentRegistry


class MessageService:
    # 消息服务：负责转发、落盘与消息读取
    def __init__(self, *, agent_registry: AgentRegistry, msgdata_dir: str) -> None:
        # Agent 注册中心
        self._agent_registry = agent_registry
        # 消息落盘目录
        self._msgdata_dir = msgdata_dir

    def _now_iso(self) -> str:
        # 统一使用 UTC ISO 时间戳
        return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

    def _ensure_dir(self) -> None:
        # 确保消息目录存在
        os.makedirs(self._msgdata_dir, exist_ok=True)

    def _agent_log_name(self, agent_id: str) -> str:
        # 将 agent_id 映射为落盘文件名
        base = agent_id
        if base.lower().endswith("agent"):
            base = base[:-5]
        base = base.lower() or "agent"
        return f"{base}_chat.jsonl"

    def _log_path(self, agent_id: str) -> str:
        # 获取单个 Agent 的日志路径
        return os.path.join(self._msgdata_dir, self._agent_log_name(agent_id))

    def append_message(self, agent_id: str, session_id: str, role: str, content: str) -> None:
        # 追加单条消息到 jsonl
        self._ensure_dir()
        item = {
            "ts": self._now_iso(),
            "agent_id": agent_id,
            "session_id": session_id,
            "role": role,
            "content": content,
        }
        with open(self._log_path(agent_id), "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def get_messages(self, agent_id: str, session_id: str) -> list[dict]:
        # 读取指定会话的消息列表
        path = self._log_path(agent_id)
        if not os.path.isfile(path):
            return []
        messages: list[dict] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    item = json.loads(raw)
                except Exception:
                    continue
                if item.get("agent_id") != agent_id:
                    continue
                if item.get("session_id") != session_id:
                    continue
                messages.append(item)
        return messages

    def stream_chat(self, agent_id: str, content: str) -> Iterable[str]:
        # 调用 Agent 的流式对话接口
        agent = self._agent_registry.get_agent(agent_id)
        if hasattr(agent, "chat_stream"):
            return agent.chat_stream(content)
        if hasattr(agent, "reply"):
            reply = agent.reply(content)
            return [str(reply)]
        raise ValueError("agent_missing_chat_method")
