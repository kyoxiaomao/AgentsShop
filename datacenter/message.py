import datetime
import json
import os
from typing import Any, Callable, Optional


# 消息服务：集中处理会话消息的读写、日志落盘与内容清洗
class MessageService:
    def __init__(
        self,
        *,
        chat_store_file: str,
        logs_dir: str,
        chat_log_file: str,
        debug_log_file: str,
        agent_message_dirs: dict[str, str],
        debug_logger: Optional[Callable[[str, dict[str, Any]], None]] = None,
    ) -> None:
        # 会话存储文件路径
        self._chat_store_file = chat_store_file
        # 日志目录
        self._logs_dir = logs_dir
        # 对话日志文件路径
        self._chat_log_file = chat_log_file
        # 调试日志文件路径
        self._debug_log_file = debug_log_file
        # Agent 对应的 markdown 消息目录
        self._agent_message_dirs = agent_message_dirs
        # 外部注入的调试日志记录器
        self._debug_logger = debug_logger

    def _now_iso(self) -> str:
        # 统一输出 UTC ISO 时间戳
        return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

    def _debug(self, event: str, payload: dict[str, Any]) -> None:
        # 若注入了调试记录器，则输出事件
        if self._debug_logger is not None:
            self._debug_logger(event, payload)

    def _ensure_dir(self, path: str) -> None:
        # 确保目录存在
        os.makedirs(path, exist_ok=True)

    def _read_json(self, path: str, default):
        # 读取 JSON 文件，不存在时返回默认值
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return default
        except Exception as e:
            # 读取异常时记录调试信息
            self._debug("read_json_failed", {"path": path, "error": str(e)})
            return default

    def _write_json(self, path: str, data) -> None:
        # 写入 JSON 文件
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _strip_thinking_prefix(self, text: str) -> str:
        # 清理以 thinking JSON 开头的前缀，保留可见正文
        trimmed = text.lstrip()
        if not trimmed.startswith("{") or '"thinking"' not in trimmed:
            return text
        depth = 0
        end_index = None
        for i, ch in enumerate(trimmed):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end_index = i
                    break
        if end_index is None:
            return text
        remainder = trimmed[end_index + 1 :].strip()
        return remainder if remainder else text

    def extract_text(self, value) -> str:
        # 将 agentscope/openai 的多模态内容统一提取为纯文本
        if isinstance(value, str):
            return self._strip_thinking_prefix(value)
        if value is None:
            return ""
        if isinstance(value, list):
            # 列表场景：拼接文本片段，过滤工具/思考等不可见内容
            parts: list[str] = []
            for item in value:
                if isinstance(item, dict):
                    item_type = item.get("type")
                    if item_type in {"thinking", "tool_use", "tool_result", "audio", "image", "video"}:
                        continue
                    if item_type == "text" and "text" in item:
                        parts.append(str(item.get("text", "")))
                    elif "text" in item:
                        parts.append(str(item.get("text", "")))
                    elif "content" in item:
                        parts.append(self.extract_text(item.get("content")))
                    elif "thinking" in item:
                        continue
                else:
                    parts.append(self.extract_text(item))
            return "\n\n".join([p for p in parts if p is not None])
        if isinstance(value, dict):
            # 单个对象：优先读 text/content，过滤 thinking/tool
            if value.get("type") in {"thinking", "tool_use", "tool_result", "audio", "image", "video"}:
                return ""
            if "text" in value:
                return str(value.get("text", ""))
            if "content" in value:
                return self.extract_text(value.get("content"))
            if "thinking" in value:
                return ""
            return ""
        return str(value)

    def clear_chat_log(self) -> None:
        # 清空对话日志与调试日志
        self._ensure_dir(self._logs_dir)
        with open(self._chat_log_file, "w", encoding="utf-8") as f:
            f.write("")
        with open(self._debug_log_file, "w", encoding="utf-8") as f:
            f.write("")

    def clear_chat_store(self) -> None:
        # 清空会话存储
        self._write_json(self._chat_store_file, {"version": 1, "sessions": {}})

    def clear_agent_messages(self) -> None:
        # 清空每个 Agent 的 markdown 消息文件
        for _agent_id, message_dir in self._agent_message_dirs.items():
            if not os.path.isdir(message_dir):
                continue
            for name in os.listdir(message_dir):
                if name.endswith(".md"):
                    try:
                        os.remove(os.path.join(message_dir, name))
                    except Exception:
                        continue

    def _load_messages(self) -> dict:
        # 载入会话存储
        return self._read_json(self._chat_store_file, {"version": 1, "sessions": {}})

    def _save_messages(self, store: dict) -> None:
        # 保存会话存储
        self._write_json(self._chat_store_file, store)

    def append_message(self, agent_id: str, session_id: str, role: str, content: str) -> list[dict]:
        # 写入单条会话消息并返回最新会话列表
        store = self._load_messages()
        sessions = store.setdefault("sessions", {})
        key = f"{agent_id}:{session_id}"
        items = sessions.setdefault(key, [])
        normalized = self.extract_text(content)
        item = {"role": role, "content": normalized, "ts": self._now_iso()}
        items.append(item)
        self._save_messages(store)
        # 记录调试事件
        self._debug(
            "message_stored",
            {"agent_id": agent_id, "session_id": session_id, "role": role, "length": len(normalized)},
        )
        return items

    def get_messages(self, agent_id: str, session_id: str) -> list[dict]:
        # 读取会话消息，并对历史内容做二次清洗
        store = self._load_messages()
        raw_messages = store.get("sessions", {}).get(f"{agent_id}:{session_id}", [])
        messages = [
            {**item, "content": self.extract_text(item.get("content"))}
            if isinstance(item, dict)
            else {"role": "assistant", "content": self.extract_text(item), "ts": self._now_iso()}
            for item in raw_messages
        ]
        # 记录调试事件
        self._debug(
            "messages_loaded",
            {"agent_id": agent_id, "session_id": session_id, "count": len(messages)},
        )
        return messages

    def append_markdown(self, agent_id: str, session_id: str, role: str, content: str) -> None:
        # 将消息以 markdown 形式追加到对应 Agent 的会话文件
        message_dir = self._agent_message_dirs.get(agent_id)
        if not message_dir:
            return
        self._ensure_dir(message_dir)
        filename = f"session-{session_id}.md"
        path = os.path.join(message_dir, filename)
        role_label = "用户" if role == "user" else "Agent"
        normalized = self.extract_text(content)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"### {role_label} {self._now_iso()}\n\n{normalized}\n\n")
        # 记录调试事件
        self._debug(
            "markdown_written",
            {"agent_id": agent_id, "session_id": session_id, "role": role, "path": path},
        )

    def append_chat_log(self, agent_id: str, session_id: str, role: str, content: str) -> None:
        # 将消息追加到统一的聊天日志（jsonl）
        self._ensure_dir(self._logs_dir)
        normalized = self.extract_text(content)
        item = {
            "ts": self._now_iso(),
            "agent_id": agent_id,
            "session_id": session_id,
            "role": role,
            "content": normalized,
        }
        with open(self._chat_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
