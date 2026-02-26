# Tasks
- [x] Task 1: 初始化 Web 端 Vite+React 工程并实现主页布局
  - [x] 在 `ui/web` 生成可运行工程与基础脚本
  - [x] 实现顶部导航（主页/次页1/次页2）与路由或页面切换
  - [x] 实现左侧 agent 列表与右侧对话区域布局（名称/状态/消息区/输入区/发送）
  - [x] 使用 mock 数据与本地 state 完成“选择角色、发送消息”交互

- [x] Task 2: 初始化 Desktop 端 Electron+Vite 工程并创建透明窗口
  - [x] 在 `ui/desktop` 生成可运行工程（主进程、preload、渲染进程）
  - [x] 创建透明无边框窗口并设置合理默认尺寸/位置
  - [x] 通过 preload 暴露最小 IPC API（避免直接暴露 Node 能力）

- [x] Task 3: 实现 IPC 按钮与主进程操作列表
  - [x] 渲染层提供 IPC 按钮
  - [x] 点击按钮触发 IPC 到主进程
  - [x] 主进程弹出操作列表并处理选择项（置顶/取消置顶、隐藏/显示、退出等）
  - [x] 选择结果可回传渲染层用于提示/状态更新

- [x] Task 4: 在桌面端集成 Phaser 并实现桌宠展示
  - [x] 渲染层初始化 Phaser 场景
  - [x] 渲染一个桌宠实体（占位图形或精灵）并从左到右展示/移动
  - [x] 与窗口布局并存（IPC 按钮与桌宠从左到右排列）

- [x] Task 5: 增加最小验证与运行说明
  - [x] 添加/更新各子工程的基本启动与构建脚本
  - [x] 添加最小自检（例如 lint 或基础单测，如工程已有则复用）

# Task Dependencies
- Task 3 depends on Task 2
- Task 4 depends on Task 2
- Task 5 depends on Task 1, Task 2, Task 3, Task 4

