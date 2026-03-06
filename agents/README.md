# Agents 说明

`agents` 存放各个 Agent 的实现与运行配置。UI 与 datacenter 不直接依赖 Agent 代码，只通过 datacenter API 或快照读取。

## 目录结构

- `base/`：基础 Agent 能力封装
  - `base_agent.py`：轻量协议层基类（name/sys_prompt/cn_name 等）
  - `reactagent_base.py`：以 AgentScope ReActAgent 为核心的基座封装
- `queen/Queen_Sera/`：现有 Agent 实现（保持不改动）
- `king/King_Lila/`：新增 Agent 实现（继承 ReActAgentBase）

## 消息落盘

datacenter 在消息收发时会将对话记录落盘为 jsonl，路径位于：

- `datacenter/service/message/msgdata/<agent>_chat.jsonl`

每条记录包含角色、时间戳、agent_id、session_id 与内容，便于审计与复盘。

部分 Agent 目录内也可能存在历史 md 会话文件（用于本地复盘），例如：

- `agents/queen/Queen_Sera/message/session-<session_id>.md`

以上 md 文件不作为当前 datacenter 的主落盘格式。

## 任务落盘（OKRAS）

当 `mode=任务` 时，datacenter 会把任务拆解结果按 jsonl 落盘到：

- `tasks/okras/okras-YYYY-MM-DD.jsonl`

## 新增 Agent 建议

1. 在 `agents/**` 下新增 Agent 实现目录，并提供 `<agent>_agent.py`
2. 建议继承 `agents.base.ReActAgentBase`，把 `model_name/api_key/base_url` 放在 Agent 内部配置
3. 在 `datacenter/service/agents/agents_status.json` 中新增条目（id/name/cn_name/enabled/class_path）
4. 为 Agent 准备 `chat_stream()`（必需）与 `decompose_task()`（任务模式可选）
