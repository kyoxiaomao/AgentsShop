## 目标

在以下目录按 AgentScope（agentscope）方式落地可扩展的多智能体代码骨架：

- `d:\AgentsShop\agents\base\`：创建一个通用 Agent 基类（封装 Model/Formatter 初始化与通用配置入口）
- `d:\AgentsShop\models\`：创建一个“大语言模型适配器”（统一创建/配置 LLM，避免每个 agent 重复写）
- `d:\AgentsShop\.env`：存放 API Key 等敏感配置（代码从环境变量读取，`.env` 仅作为本地载入来源）
- `d:\AgentsShop\agents\queen\Queen_Sera\`：创建一个具体 Agent：`SeraAgent`（英文名：seraAgent；中文名：塞瑞）
- 参考 `d:\AgentsShop\tests\test_connection.py` 的最小闭环：`OpenAIChatModel + OpenAIChatFormatter + ReActAgent + Msg + await reply`

## 现状调研结论

- 仓库当前没有任何 `agents/` 业务代码与 Python 包结构（需要从零创建目录与 `__init__.py`）。
- 现有可参考代码仅有：
  - `tests/test_connection.py`：演示如何创建 `ReActAgent` 并异步 `reply`
  - `docs/model.py`：演示 OpenAI SDK 调用同一模型端点（含 stream 示例）
  - `docs/name.json`：包含 `sera -> 塞瑞` 等多 agent 名称映射（利于后续扩展）

## 设计原则（面向“多智能体可拓展”）

- **目录即边界**：`agents/base` 只放通用能力与配置；具体角色（Queen_Sera）只放 persona 与默认参数。
- **继承 ReActAgent**：优先用 `agentscope.agent.ReActAgent` 作为可聊天/可工具的默认实现，避免过早自定义底层推理循环。
- **配置可注入**：Model/Formatter 的构建支持显式传参与环境变量两种来源，方便后续 UI/运行时动态加载不同模型。
- **不硬编码密钥**：把 `api_key` 从代码迁移为环境变量读取；本地用 `.env` 管理并配合 `.gitignore` 忽略提交；测试脚本也同步改造。

## 计划实施步骤（按提交粒度）

### 1) 建立可 import 的包结构

创建以下文件（空文件即可）以确保 Python 能按包导入（从仓库根目录运行时可直接 `import agents...`）：

- `d:\AgentsShop\agents\__init__.py`
- `d:\AgentsShop\agents\base\__init__.py`
- `d:\AgentsShop\agents\queen\__init__.py`
- `d:\AgentsShop\agents\queen\Queen_Sera\__init__.py`

同时为模型适配器创建包结构：

- `d:\AgentsShop\models\__init__.py`

### 2) 实现“大语言模型适配器”（`models/`）

新增 `d:\AgentsShop\models\llm_adapter.py`（命名可微调，但保持语义清晰），提供：

- 负责加载 `.env`（使用已安装的 `dotenv.load_dotenv`），让本地无需手动 `setx` 也能运行
- 统一的环境变量约定（建议）：
  - `MODELSCOPE_API_KEY`：ModelScope Token（必填）
  - `MODELSCOPE_BASE_URL`：默认 `https://api-inference.modelscope.cn/v1`
  - `MODELSCOPE_MODEL_NAME`：默认 `ZhipuAI/GLM-5:DashScope`
- `create_openai_chat_model(...) -> OpenAIChatModel`
  - 默认值与 `tests/test_connection.py` 对齐
  - 允许显式传参覆盖（便于未来 UI 切换模型）
- `create_openai_chat_formatter() -> OpenAIChatFormatter`

### 3) 实现 Agent 基类（`agents/base`）

新增 `d:\AgentsShop\agents\base\base_agent.py`，提供：

- `BaseAgent(ReActAgent)`（基类）
  - 构造时可传：`name`、`sys_prompt`、`model_config`、`formatter`
  - 内部默认通过 `models/llm_adapter.py` 创建 `OpenAIChatModel` 与 `OpenAIChatFormatter`
  - 预留可扩展入口：后续可加入 toolkit/tools 注入参数（不在本次实现中强绑定）

### 4) 实现 SeraAgent（`agents/queen/Queen_Sera`）

新增 `d:\AgentsShop\agents\queen\Queen_Sera\sera_agent.py`：

- `class SeraAgent(BaseAgent)`
  - 默认 `name="seraAgent"`
  - 提供 `cn_name="塞瑞"` 作为可选元信息字段（用于 UI 展示；不影响 agentscope 内部协议）
  - 提供适合“塞瑞”角色的默认 `sys_prompt`（可后续调整）

同时在 `d:\AgentsShop\agents\queen\Queen_Sera\__init__.py` 导出 `SeraAgent`，便于外部引用。

### 5) 用新结构改造连通性测试脚本

更新 `d:\AgentsShop\tests\test_connection.py`：

- 替换直接实例化 `ReActAgent` 的代码为：
  - `from agents.queen.Queen_Sera import SeraAgent`
  - `agent = SeraAgent(...)`
- `api_key` 改为从环境变量读取（环境变量来源可为 `.env`）
- 保持原有异步 `await agent.reply(Msg(...))` 的调用形态不变

### 6) 生成 `.env` 与忽略规则（安全）

新增：

- `d:\AgentsShop\.env`：写入配置键（提供占位值，不写入真实 token）
- `d:\AgentsShop\.env.example`：可提交的示例文件（同 `.env` 内容但无敏感值）
- `d:\AgentsShop\.gitignore`：至少忽略 `.env`（避免误提交）

### 7) 本地验证方式（实现后执行）

在已激活 `.venv` 的前提下运行：

- `python -m tests.test_connection`
  - 或 `python d:\AgentsShop\tests\test_connection.py`

运行前准备：

- 在仓库根目录创建/填写 `.env`：
  - `MODELSCOPE_API_KEY=<你的token>`
  - 可选：`MODELSCOPE_MODEL_NAME=ZhipuAI/GLM-5:DashScope`
  - 可选：`MODELSCOPE_BASE_URL=https://api-inference.modelscope.cn/v1`

验收标准：

- `SeraAgent` 能成功被 import
- `test_connection.py` 能正常调用并打印回复
- 代码中不再出现硬编码的 `api_key` 字符串

## 影响范围

- 新增：`agents/` 目录与若干 Python 文件
- 修改：`tests/test_connection.py`（导入与配置方式）
- 不改动：前端/运行时逻辑（本次仅完成 Python 侧 agent 骨架）
