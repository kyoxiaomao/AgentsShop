## 项目结构与目录说明

**仓库根目录**
- `d:\AgentsShop\`

### 目录树（精简）

> 说明：以下目录树刻意不展开 `.venv/`、`node_modules/`、`__pycache__/`、`.git/` 等噪声目录。

```text
AgentsShop/
├─ agents/                      # Agent 实现（基于 agentscope）
├─ datacenter/                  # 轻量后端：Agent 发现/状态/消息存储 + HTTP API
├─ models/                      # 复用模块：LLM 适配层等
├─ ui/
│  ├─ web/index/                # Web：React + Vite + Tailwind
│  └─ desktop/                  # Desktop：Electron + React + Phaser + Vite
├─ docs/                        # 文档与备忘
├─ logs/                        # 运行日志（chat/debug 等）
├─ .trae/                       # Trae 规则与规格文档（IDE/工作流相关）
├─ .env / .env.example          # 环境变量示例（本仓库包含真实 .env，请注意安全）
├─ .gitignore
├─ README.MD
└─ start-dev.ps1                # 顶层开发启动脚本（转到 ui/web/index 执行 dev:all）
```

### 根目录文件（按重要程度）

**文件清单**
- `start-dev.ps1`：开发启动入口（进入 `ui\web\index` 执行 `npm run dev:all`，同时拉起 Web + datacenter）
- `README.MD`：项目说明（本文件）
- `.env`：本地环境变量（包含敏感信息时不要提交/外发）
- `.env.example`：环境变量示例模板（用于复制生成本地 `.env`）
- `.gitignore`：Git 忽略规则

### agents（Agent 实现）

**目录**
- `d:\AgentsShop\agents\`

**模块定位**
- 存放各个 Agent 的实现与运行配置。
- datacenter 会从这里自动发现可用 Agent（通过扫描包含 `BaseAgent` 的 `.py` 文件提取 `name/cn_name`）。

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
- 提供轻量 HTTP API：Agent 列表/状态、消息存取、对话与流式输出。
- 负责从 `agents/` 自动发现 Agent，并生成给前端使用的快照（`ui_snapshot.json`）。

**文件清单（按重要程度）**
- `server.py`：HTTP 服务入口（提供 `/api/*`，并在内部动态加载 Agent 类来处理对话）
- `message.py`：消息处理模块（会话消息存取、markdown 落盘、chat/debug 日志写入等集中在此）
- `service.py`：Agent 发现、状态读取与 UI 快照构建逻辑（生成 `ui_snapshot.json`）
- `models.py`：数据结构定义（AgentProfile / AgentStatus）
- `cli.py`：命令行入口（用于构建 UI 快照）
- `registry.json`：Agent 列表兜底配置（当文件扫描发现不到 Agent 时使用）
- `ui_snapshot.json`：给前端读取的快照输出（agents 列表 + status）
- `chat_store.json`：会话/消息存储（JSON）
- `status.json`：Agent 运行状态存储（JSON）
- `__init__.py`：对外导出 `get_agents/get_status_map/build_ui_snapshot/snapshot_path`

### models（复用能力模块）

**目录**
- `d:\AgentsShop\models\`

**模块定位**
- 放置各个 Agent 可复用的能力模块；目前包含 `llm_adapter` 适配层实现。

**文件清单（按重要程度）**
- `llm_adapter.py`：LLM 适配层实现（聊天：OpenAI SDK Client；任务/工具：agentscope OpenAIChatModel；并提供流式增量解析与简单耗时统计）
- `__init__.py`：包初始化

### ui/web/index（网页端）

**目录**
- `d:\AgentsShop\ui\web\index\`

**模块定位**
- React + Vite + Tailwind 的网页端（包含用户页与管理页）。
- 默认通过 Vite 代理访问 datacenter 的 `/api/*`（`/api` → `http://127.0.0.1:8000`）。

**文件清单（按重要程度）**
- `package.json`：前端脚本入口（`dev:all` 并行启动 datacenter + Vite；`dev:index`/`dev:admin` 分别打开用户页/管理页）
- `vite.config.mjs`：Vite 配置（开发端口、`/api` 代理、多入口构建）
- `src/App.jsx`：用户页主应用（加载 agents/消息；输入框前的下拉框决定 mode：聊天/任务/工具，并随 `/api/chat/stream` 一起发送）
- `src/main.jsx`：用户页挂载入口
- `index.html`：用户页 HTML 入口（加载 `/src/main.jsx`）
- `src/admin/AdminApp.jsx`：管理页主应用（UI 骨架/占位模块）
- `src/admin/main.jsx`：管理页挂载入口
- `admin.html`：管理页 HTML 入口（加载 `/src/admin/main.jsx`）
- `src/index.css`：Tailwind 与页面基础样式
- `tailwind.config.js`：Tailwind 配置
- `postcss.config.js`：PostCSS 配置（Tailwind/Autoprefixer）
- `package-lock.json`：npm 依赖锁定文件

### ui/desktop（桌面端）

**目录**
- `d:\AgentsShop\ui\desktop\`

**模块定位**
- Electron + React + Phaser + Vite 的桌面端工程（透明置顶窗口、鼠标穿透/接管、桌宠渲染与交互）。

**文件清单（按重要程度）**
- `package.json`：桌面端脚本入口（`dev`：Vite + Electron；`dist/pack`：打包发布）
- `src/main/main.js`：Electron 主进程入口（创建透明置顶窗口、托盘菜单、IPC、鼠标穿透控制）
- `src/main/preload.js`：Preload（通过 contextBridge 暴露主进程 API 给渲染进程）
- `src/renderer/main.jsx`：渲染进程入口（挂载 React）
- `src/renderer/App.jsx`：桌面端主组件（协调 UI 与 Phaser，控制鼠标穿透/交互锁）
- `src/renderer/env.js`：读取 preload 暴露的 `window.deskant` 并导出给 React 使用
- `src/renderer/game/PhaserGame.jsx`：Phaser 容器（创建 Phaser.Game，订阅 EventBus 事件）
- `src/renderer/game/scenes/MainScene.js`：核心场景（桌宠移动/边界/悬停/点击交互，向 EventBus 通知交互锁）
- `src/renderer/game/EventBus.js`：React ↔ Phaser 的事件总线（Phaser.Events.EventEmitter）
- `src/renderer/components/ControlButton.jsx`：控制中心入口按钮（打开菜单/状态面板，触发重置/退出）
- `src/renderer/components/MenuPanel.jsx`：控制菜单（速度调节/重置/退出等）
- `src/renderer/components/StatusPanel.jsx`：状态面板（调用 Electron API 获取运行信息并展示）
- `src/renderer/styles/GlobalStyle.js`：全局样式（透明背景、禁滚动等）
- `src/renderer/global.d.ts`：TypeScript 全局类型声明（window.deskant）
- `src/renderer/types.js`：小工具函数（目前仅 `noop`）
- `src/renderer/components/Ant.jsx`：基于 styled-components 的桌宠实现（当前未被主流程引用，可作为备用/实验实现）
- `public/assets/ant-idle.png`：桌宠默认资源（主进程托盘图标与 Phaser 贴图）
- `public/assets/.gitkeep`：占位文件，确保 assets 目录被 Git 跟踪
- `index.html`：渲染进程 HTML 入口（加载 `/src/renderer/main.jsx`）
- `vite.config.mjs`：Vite 配置（桌面端渲染进程构建/开发）
- `readme.md`：桌面端项目说明（架构与开发指南）
- `.gitignore`：桌面端工程的 Git 忽略规则
- `package-lock.json`：npm 依赖锁定文件

### docs（文档与备忘）

**目录**
- `d:\AgentsShop\docs\`

**文件清单（按重要程度）**
- `mingling.md`：开发备忘（虚拟环境激活、依赖安装、常用启动命令）
- `name.json`：名称映射表（英文名 → 中文名）

### logs（运行日志）

**目录**
- `d:\AgentsShop\logs\`

**文件清单（按重要程度）**
- `chat.jsonl`：对话日志（按行 JSON，记录角色/内容/时间等）
- `debug.jsonl`：调试事件日志（前后端上报/状态更新等）

### .trae（IDE/工作流配置）

**目录**
- `d:\AgentsShop\.trae\`

**文件清单（按重要程度）**
- `rules/gz.md`：工作区规则（技术栈、目录约定、编码规范等）
- `specs/document-project-structure/spec.md`：规格文档（本次 README 结构梳理）
- `specs/document-project-structure/tasks.md`：任务拆分记录
- `specs/document-project-structure/checklist.md`：验收检查清单





<!-- ===== 适配器说明开始 ===== -->

# AgentsShop

## llm_adapter（适配器说明）

**文件路径**
- `d:\AgentsShop\README.MD`（本说明入口）
- `d:\AgentsShop\models\llm_adapter.py`（适配器实现）

**模块定位**
- 统一封装 LLM 接入的“创建客户端 / 创建对话模型 / 流式输出解析 / 简单耗时统计”等通用能力，供各个 Agent 复用。
- 当前适配器不再读取任何环境变量：模型配置（base_url / api_key / model_name / 额外参数等）由各个 Agent 在调用时传入。
- datacenter 会根据前端 mode（聊天/任务/工具）选择：聊天走 OpenAI SDK Client，任务/工具走 agentscope OpenAIChatModel。

## LLM 推理（OpenAI SDK 方向）

**作用**
- 创建 OpenAI Client：create_openai_chat_client（支持传入 base_url、api_key 及可选 client_kwargs）。
- 提供流式输出的增量解析（将 stream 返回的 delta 内容按文本片段迭代输出）。
- 提供单次对话调用的耗时/阶段统计（例如首包、首字、总耗时等）并汇总最终回答文本。

**典型使用场景**
- 需要流式输出（stream=True）且希望在上层做打印、拼接或工具解析的 Agent。
- 需要简单观测调用耗时（首包/首字）用于体验或性能对比的 Agent。

## LLM 对话模型（agentscope 方向）

**作用**
- 创建 agentscope 的 OpenAIChatModel：create_openai_task_model（可传 base_url、api_key、generate_kwargs、stream_tool_parsing 等）。
- 创建 agentscope 的 DashScopeChatModel（可传 api_key、stream、enable_thinking、generate_kwargs、base_http_api_url 等）。
- 创建 OpenAIChatFormatter，用于与 agentscope 的消息格式化流程对接。

**典型使用场景**
- 以 agentscope 的 Model/Formatter 体系来驱动对话与工具调用（包含流式 tool parsing）的 Agent。

<!-- ===== 适配器说明结束 ===== -->
