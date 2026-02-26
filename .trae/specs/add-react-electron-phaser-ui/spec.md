# React + Electron + Phaser + Vite UI Spec

## Why
需要一个最小可用的 Web 对话主页与桌面端透明窗口“桌宠”入口，作为后续 AgentsShop 多智能体交互与操作面板的承载。

## What Changes
- 在 `d:\AgentsShop\ui\web` 生成基于 Vite 的 React Web 端工程，并提供 `index` 主页面布局：
  - 顶部导航栏：主页 / 次页1 / 次页2
  - 左侧：agent 角色列表
  - 右侧：从上到下依次包含 agent 角色名称、状态（忙碌/空闲）、对话信息框、对话输入框与发送按钮
- 在 `d:\AgentsShop\ui\desktop` 生成基于 Vite 的 Electron 桌面端工程：
  - 创建透明窗口（透明、无边框）
  - 提供一个 IPC 按钮：点击后弹出“操作列表”（由主进程创建/控制）
  - 在渲染层提供一个 agent 角色桌宠（使用 Phaser.js），从左到右展示（横向排列/朝向）
- 统一约束：所有交互先以本地 mock 数据与前端状态机实现；后续再对接真实 agent/后端接口。

## Impact
- Affected specs: 无（新增 UI 工程）
- Affected code: 新增 `ui/web/**`、`ui/desktop/**` 相关代码与配置；不影响现有 Python 侧逻辑。

## ADDED Requirements

### Requirement: Web 端主页布局
系统 SHALL 在 `ui/web` 中提供可运行的 React 页面，并在主页呈现双栏对话布局与顶部导航。

#### Scenario: 初次打开主页
- **WHEN** 用户启动 Web 开发服务器并打开主页
- **THEN** 顶部出现导航栏（主页/次页1/次页2）
- **AND** 左侧显示 agent 角色列表（至少 3 个 mock 角色）
- **AND** 右侧显示：角色名称、状态（忙碌/空闲）、对话信息框、输入框、发送按钮

#### Scenario: 选择角色与发送消息
- **WHEN** 用户在左侧列表选择某个角色
- **THEN** 右侧角色名称与状态更新为所选角色
- **WHEN** 用户在输入框输入内容并点击发送
- **THEN** 对话信息框新增一条“用户消息”
- **AND**（可选）追加一条 mock 的“agent 回复”

### Requirement: 桌面端透明窗口与 IPC 操作列表
系统 SHALL 在 `ui/desktop` 中提供可运行的 Electron 应用，并创建透明窗口，包含可触发 IPC 的操作按钮。

#### Scenario: 启动桌面端
- **WHEN** 用户启动桌面端应用
- **THEN** 出现透明窗口（无边框），窗口内包含 IPC 按钮与桌宠区域

#### Scenario: 弹出操作列表
- **WHEN** 用户点击 IPC 按钮
- **THEN** 主进程弹出操作列表（例如：置顶/取消置顶、隐藏/显示、退出）
- **AND** 用户点击某个操作后，应用执行对应行为或在渲染层显示结果提示

### Requirement: 桌宠（Phaser）展示
系统 SHALL 在桌面端渲染层提供 Phaser 场景，显示一个 agent 角色桌宠并从左到右展示（面向右侧/横向移动）。

#### Scenario: 桌宠渲染
- **WHEN** 桌面端窗口渲染完成
- **THEN** Phaser 场景初始化成功并渲染桌宠实体
- **AND** 桌宠至少具备一个简单动画或移动效果（可用占位精灵/几何图形实现）

## MODIFIED Requirements
无

## REMOVED Requirements
无

## Assumptions
- Web 与 Desktop UI 作为独立子工程存在，不要求与现有 Python 服务联动；数据均以 mock 驱动。
- 桌面端透明窗口默认启用 alwaysOnTop（可通过操作列表切换），并使用安全的 IPC（preload + contextBridge）。

