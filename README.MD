## 项目结构与目录说明

**仓库根目录**
- `d:\AgentsShop\`

### 目录树（精简）

> 说明：以下目录树刻意不展开 `.venv/`、`node_modules/`、`__pycache__/`、`.git/` 等噪声目录。

```text
AgentsShop/
├─ agents/                      # Agent 实现
├─ datacenter/                  # 轻量后端：Agent 注册/状态/消息存储 + HTTP/WS
├─ models/                      # 复用模块：LLM 适配层
├─ ui/
│  └─ desktop/                  # Electron + React + Phaser + Vite
├─ docs/                        # 文档与备忘
├─ .trae/                       # Trae 规则与规格文档（IDE/工作流相关）
├─ .env / .env.example          # 环境变量示例（本仓库包含真实 .env，请注意安全）
├─ .gitignore
├─ README.MD
├─ clean-runtime-data.ps1       # 统一清理脚本（日志/消息/旧目录）
├─ kill-electron.ps1            # 清理残留进程与占用端口
├─ mingling.md                  # 开发备忘
└─ start-dev.ps1                # 顶层开发启动脚本（datacenter + desktop）
```

### 根目录文件（按重要程度）

**文件清单**
- `start-dev.ps1`：开发启动入口（先清理运行数据，再拉起 datacenter + desktop）
- `clean-runtime-data.ps1`：统一清理入口（`ui/logs/ui_debug.jsonl`、`datacenter/logs/server_debug.jsonl`、消息 jsonl）
- `kill-electron.ps1`：清理残留 Electron 及占用 5173/8000 端口的相关进程
- `README.MD`：项目说明（本文件）
- `.env`：本地环境变量（包含敏感信息时不要提交/外发）
- `.env.example`：环境变量示例模板（用于复制生成本地 `.env`）
- `.gitignore`：Git 忽略规则
- `mingling.md`：开发命令备忘

### agents（Agent 实现）

**目录**
- `d:\AgentsShop\agents\`

**模块定位**
- 存放各个 Agent 的实现与运行配置。
- datacenter 根据 `datacenter/service/agents/agents_status.json` 中的 `class_path` 注册可用 Agent。

**文件清单（按重要程度）**
- `queen/Queen_Sera/sera_agent.py`：现有 Agent 实现（SeraAgent），负责模型/参数选择与对话方法封装
- `base/base_agent.py`：BaseAgent（对 agentscope `ReActAgent` 的薄封装），强制 Agent 显式传入模型配置
- `README.md`：agents 目录说明（消息落盘规则、新增 Agent 建议等）
- `queen/Queen_Sera/message/.gitkeep`：占位文件，确保 message 目录被 Git 跟踪
- `queen/Queen_Sera/__init__.py`：包初始化
- `queen/__init__.py`：包初始化
- `base/__init__.py`：包初始化
- `__init__.py`：包初始化

### datacenter（后端中枢）

**目录**
- `d:\AgentsShop\datacenter\`

**模块定位**
- 混合模式后端：HTTP 提供 Agent 列表/状态与消息历史；WebSocket 提供对话流式输出。
- Agent 注册信息来自 `service/agents/agents_status.json` 静态配置。

**文件清单（按重要程度）**
- `server.py`：HTTP + WebSocket 服务入口（路由请求并调用 service 层处理）
- `service/agents/service_agents.py`：从 JSON 加载 Agent 注册映射并懒加载实例
- `service/message/message.py`：聊天消息转发、流式回复与消息落盘
- `service/agents/agents_status.json`：Agent 静态配置（`id/name/cn_name/enabled/class_path`）
- `logs/server_debug.jsonl`：后端核心运行日志

### models（复用能力模块）

**目录**
- `d:\AgentsShop\models\`

**模块定位**
- 放置各个 Agent 可复用的能力模块；目前包含 `llm_adapter` 适配层实现。

**文件清单（按重要程度）**
- `llm_adapter.py`：LLM 适配层实现（仅保留直连 OpenAI 的流式增量解析）
- `__init__.py`：包初始化

### ui/desktop（桌面端）

**目录**
- `d:\AgentsShop\ui\desktop\`

**模块定位**
- Electron + React + Phaser + Vite 的桌面端工程（桌宠透明置顶、独立状态窗口、应用主窗口、鼠标穿透/交互切换）。

**当前 UI 逻辑**
- **窗口体系**：`petWindow` 全屏透明置顶；`appWindow` 为普通应用窗口；`statusWindow` 为独立状态面板窗口
- **状态联动**：打开 `appWindow` 时临时降低 `petWindow` 置顶，隐藏时恢复
- **鼠标穿透**：默认穿透，角色悬停/拖拽与菜单命中时关闭穿透

**文件清单（按重要程度）**
- `package.json`：桌面端脚本入口（`dev`：Vite + Electron；`dist/pack`：打包发布）
- `src/main/main.js`：Electron 主进程入口（窗口创建、托盘菜单、IPC、鼠标穿透控制）
- `src/main/preload.js`：Preload（通过 contextBridge 暴露主进程 API 给渲染进程）
- `src/renderer/pet/App.jsx`：桌宠主组件（协调 UI 与 Phaser，控制鼠标穿透/交互锁）
- `src/renderer/pet/game/PhaserGame.jsx`：Phaser 容器（创建 Phaser.Game，订阅 EventBus 事件）
- `src/renderer/pet/game/scenes/MainScene.js`：核心场景（桌宠移动/边界/悬停/拖拽，向 EventBus 通知交互锁）
- `src/renderer/pet/game/EventBus.js`：React ↔ Phaser 的事件总线（Phaser.Events.EventEmitter）
- `src/renderer/pet/components/ControlButton.jsx`：控制中心入口按钮（打开菜单/状态面板，打开/隐藏应用）
- `src/renderer/pet/components/MenuPanel.jsx`：控制菜单（速度调节、桌宠显示、应用/状态面板、退出）
- `src/renderer/pet/components/StatusPanel.jsx`：状态面板（Tab 视图）
- `src/renderer/pet/index.css`：桌宠基础样式
- `src/renderer/app/App.jsx`：应用窗口入口
- `src/renderer/app/components`：应用窗口布局、导航与 Sidebar 组件
- `src/renderer/app/pages`：应用窗口页面（管理页与 Agent 页）
- `src/renderer/app/store`：Redux store 与切片
- `public/assets/ant-idle.png`：桌宠默认资源（主进程托盘图标与 Phaser 贴图）
- `public/assets/.gitkeep`：占位文件，确保 assets 目录被 Git 跟踪
- `index.html`：桌宠窗口 HTML 入口（加载 `/src/renderer/pet/main.jsx`）
- `app.html`：应用窗口 HTML 入口（加载 `/src/renderer/app/main.jsx`）
- `vite.config.mjs`：Vite 配置（桌面端渲染进程构建/开发）
- `readme.md`：桌面端项目说明（架构与开发指南）
- `.gitignore`：桌面端工程的 Git 忽略规则
- `package-lock.json`：npm 依赖锁定文件

### docs（文档与备忘）

**目录**
- `d:\AgentsShop\docs\`

**文件清单（按重要程度）**
- `name.json`：名称映射表（英文名 → 中文名）

### 运行日志与消息

**日志路径**
- `d:\AgentsShop\ui\logs\ui_debug.jsonl`：桌面端主进程 + 渲染端 chat 关键日志
- `d:\AgentsShop\datacenter\logs\server_debug.jsonl`：后端核心日志（server/ws/chat/error）
- `d:\AgentsShop\datacenter\service\message\msgdata\*.jsonl`：会话消息落盘

### .trae（IDE/工作流配置）

**目录**
- `d:\AgentsShop\.trae\`

**文件清单（按重要程度）**
- `rules/gz.md`：工作区规则（技术栈、目录约定、编码规范等）
- `specs/document-project-structure/spec.md`：规格文档（本次 README 结构梳理）
- `specs/document-project-structure/tasks.md`：任务拆分记录
- `specs/document-project-structure/checklist.md`：验收检查清单

