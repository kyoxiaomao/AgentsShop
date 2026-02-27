# DataCenter（UI 数据层）

`datacenter` 用于承载 UI 侧所需的“可展示数据”，让 UI 不直接依赖 `agents` 的实现细节，从而降低前后端/跨语言耦合。

当前数据以“快照文件”形式提供：`ui_snapshot.json`。UI 只需要读取该文件即可渲染 Agent 列表与状态。新增了轻量 API 服务用于消息收发与状态刷新。

## 目录结构

- `registry.json`：Agent 注册表（展示名、中文名、是否启用）
- `status.json`：Agent 状态表（offline/idle/busy + 更新时间）
- `ui_snapshot.json`：对 UI 友好的聚合快照（由服务生成）
- `service.py`：读取/聚合/生成快照
- `models.py`：数据模型（dataclasses）
- `cli.py`：命令行入口（生成快照）
- `server.py`：轻量 API 服务（消息收发、状态刷新）
- `chat_store.json`：对话消息存档（由服务生成）

## 数据来源与职责边界

- `agents/**`：运行时能力与配置（Agent 本体、LLM 装配等）
- `datacenter/**`：UI 需要的“可展示数据”与聚合快照

UI 不应直接读取/解析 `agents/**` 的 Python 代码或类定义，只依赖 `datacenter/ui_snapshot.json` 或对外只读接口。

## 快照格式（ui_snapshot.json）

```json
{
  "version": 1,
  "agents": [
    { "id": "seraAgent", "name": "seraAgent", "cn_name": "塞瑞", "enabled": true }
  ],
  "status": {
    "seraAgent": { "status": "offline", "updated_at": "1970-01-01T00:00:00Z" }
  }
}
```

字段说明：

- `agents[].id`：Agent 业务 ID（建议与运行时代码中的 `name` 保持一致）
- `agents[].name`：展示用英文名
- `agents[].cn_name`：展示用中文名
- `agents[].enabled`：是否在 UI 中可用/可选
- `status[<id>].status`：`offline | idle | busy`
- `status[<id>].updated_at`：ISO8601 字符串（建议使用 UTC + `Z`）

## 使用方式

### 1）生成/刷新快照

在仓库根目录执行：

```bash
python -m datacenter.cli --build
```

生成输出：`datacenter/ui_snapshot.json`

### 2）启动 API 服务

在仓库根目录执行：

```bash
python -m datacenter.server
```

默认监听：`http://127.0.0.1:8000`

接口：

- `GET /api/agents`：获取 UI 快照
- `GET /api/messages?agent_id=seraAgent&session_id=default`：获取会话消息
- `POST /api/chat`：发送消息并获取回复

`POST /api/chat` 请求示例：

```json
{
  "agent_id": "seraAgent",
  "session_id": "default",
  "content": "你好"
}
```

响应示例：

```json
{
  "agent_id": "seraAgent",
  "session_id": "default",
  "reply": "你好，我是塞瑞。",
  "messages": [
    { "role": "user", "content": "你好", "ts": "2026-01-01T00:00:00Z" },
    { "role": "assistant", "content": "你好，我是塞瑞。", "ts": "2026-01-01T00:00:01Z" }
  ]
}
```

### 3）在代码中调用

```python
from datacenter.service import build_ui_snapshot

path = build_ui_snapshot()
print(path)
```

## 如何新增一个 Agent（仅影响 UI 展示）

编辑 `registry.json`，追加一条记录：

```json
{
  "id": "newAgent",
  "name": "newAgent",
  "cn_name": "新 Agent",
  "enabled": true
}
```

然后重新生成快照：

```bash
python -m datacenter.cli --build
```

## 如何更新状态（由运行时写入）

编辑/写入 `status.json` 中对应 Agent 的状态：

```json
{
  "seraAgent": { "status": "busy", "updated_at": "2026-01-01T00:00:00Z" }
}
```

然后重新生成快照：

```bash
python -m datacenter.cli --build
```

后续如果要实现“实时状态”，建议由运行时模块维护状态并触发快照刷新，UI 仍然只消费快照结构，不关心状态来源细节。

## 对话记录落盘

对话记录以 Markdown 追加写入 Agent 目录：

- `agents/queen/Queen_Sera/message/session-<session_id>.md`

会话记录格式为“角色 + 时间戳 + 内容”，由 `datacenter/server.py` 在消息收发时自动写入。

## 日志与错误处理约定

`service.py` 对缺失文件会输出 warning（例如注册表不存在），对 JSON 读取异常会输出 error，并使用默认值继续生成快照。
如果你希望统一日志格式/级别，可在应用入口统一配置 `logging`。
