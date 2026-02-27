# DataCenter（UI 数据层）

`datacenter` 用于承载 UI 侧所需的“可展示数据”，让 UI 不直接依赖 `agents` 的实现细节，从而降低前后端/跨语言耦合。

当前数据以“快照文件”形式提供：`ui_snapshot.json`。UI 只需要读取该文件即可渲染 Agent 列表与状态。

## 目录结构

- `registry.json`：Agent 注册表（展示名、中文名、是否启用）
- `status.json`：Agent 状态表（offline/idle/busy + 更新时间）
- `ui_snapshot.json`：对 UI 友好的聚合快照（由服务生成）
- `service.py`：读取/聚合/生成快照
- `models.py`：数据模型（dataclasses）
- `cli.py`：命令行入口（生成快照）

## 数据来源与职责边界

- `agents/**`：运行时能力与配置（Agent 本体、LLM 装配等）
- `datacenter/**`：UI 需要的“可展示数据”与聚合快照

UI 不应直接读取/解析 `agents/**` 的 Python 代码或类定义，只依赖 `datacenter/ui_snapshot.json` 或未来暴露的只读接口。

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

### 2）在代码中调用

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

## 日志与错误处理约定

`service.py` 对缺失文件会输出 warning（例如注册表不存在），对 JSON 读取异常会输出 error，并使用默认值继续生成快照。
如果你希望统一日志格式/级别，可在应用入口统一配置 `logging`。
