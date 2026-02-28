# README 项目结构文档 Spec

## Why
当前仓库根 README.MD 只覆盖了 `llm_adapter` 的适配器说明，缺少整体项目结构与各目录职责，影响新同学上手与模块定位。

## What Changes
- 在 `d:\AgentsShop\README.MD` 现有“适配器说明结束”之后追加“项目结构与目录说明”章节
- 以“目录树 + 关键目录职责说明”的形式描述仓库整体结构（排除 `.venv/`、`node_modules/`、`__pycache__/` 等噪声目录）
- 明确关键模块入口与对应目录：
  - `models/llm_adapter.py`（适配器实现）
  - `agents/`（Agent 实现与消息落盘目录）
  - `datacenter/`（HTTP 服务、快照、消息存储与状态）
  - `ui/web/`（Web 前端）
  - `ui/desktop/`（桌面端）
  - `docs/`、`logs/`、`start-dev.ps1`、`.env/.env.example`
- README 的结构与表述风格参考现有 `README.MD#L1-36`（用“文件路径 / 模块定位 / 典型使用场景”或同等粒度的说明）

## Impact
- Affected specs: 文档/上手指引
- Affected code: 仅 `d:\AgentsShop\README.MD`（不修改运行逻辑）

## ADDED Requirements
### Requirement: README 项目结构
README.MD SHALL 在适配器说明之后提供项目结构与目录说明，包含：
- 顶层目录树（至少覆盖 `agents/`、`datacenter/`、`models/`、`ui/`、`docs/`、`logs/`、`start-dev.ps1`）
- 每个关键目录的职责、重要文件入口与相互关系（例如 UI 仅通过 datacenter API/快照与 Agent 间接交互）

#### Scenario: 浏览仓库结构（成功）
- **WHEN** 用户打开 `d:\AgentsShop\README.MD`
- **THEN** 可以在一个页面内完成“目录在哪 / 入口在哪 / 模块之间怎么连”的定位

## MODIFIED Requirements
### Requirement: llm_adapter 说明段落
原有 `llm_adapter（适配器说明）` 内容保持不变，仅在其后追加新章节，不改变既有段落语义与标题层级。

## REMOVED Requirements
无

