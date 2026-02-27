# Agents 说明

`agents` 存放各个 Agent 的实现与运行配置。UI 与 datacenter 不直接依赖 Agent 代码，只通过 datacenter API 或快照读取。

## 目录结构

- `base/`：基础 Agent 能力封装
- `queen/Queen_Sera/`：现有 Agent 实现

## 消息落盘

datacenter 在消息收发时会将对话记录追加到对应 Agent 的目录中：

- `agents/queen/Queen_Sera/message/session-<session_id>.md`

每条记录包含角色、时间戳与内容，便于审计与复盘。

## 新增 Agent 建议

1. 在 `agents/**` 下新增 Agent 实现
2. 保持 `name` 与 `cn_name` 可被识别
3. datacenter 将自动发现并写入快照
