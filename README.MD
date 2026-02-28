<!-- ===== 适配器说明开始 ===== -->

# AgentsShop

## llm_adapter（适配器说明）

**文件路径**
- `d:\AgentsShop\README.MD`（本说明入口）

**模块定位**
- 统一封装 LLM 接入的“创建客户端 / 创建对话模型 / 流式输出解析 / 简单耗时统计”等通用能力，供各个 Agent 复用。
- 当前适配器不再读取任何环境变量：模型配置（base_url / api_key / model_name / 额外参数等）由各个 Agent 在调用时传入。

## LLM 推理（OpenAI SDK 方向）

**作用**
- 创建 OpenAI Client（支持传入 base_url、api_key 及可选 client_kwargs）。
- 提供流式输出的增量解析（将 stream 返回的 delta 内容按文本片段迭代输出）。
- 提供单次对话调用的耗时/阶段统计（例如首包、首字、总耗时等）并汇总最终回答文本。

**典型使用场景**
- 需要流式输出（stream=True）且希望在上层做打印、拼接或工具解析的 Agent。
- 需要简单观测调用耗时（首包/首字）用于体验或性能对比的 Agent。

## LLM 对话模型（agentscope 方向）

**作用**
- 创建 agentscope 的 OpenAIChatModel（可传 base_url、api_key、generate_kwargs、stream_tool_parsing 等）。
- 创建 agentscope 的 DashScopeChatModel（可传 api_key、stream、enable_thinking、generate_kwargs、base_http_api_url 等）。
- 创建 OpenAIChatFormatter，用于与 agentscope 的消息格式化流程对接。

**典型使用场景**
- 以 agentscope 的 Model/Formatter 体系来驱动对话与工具调用（包含流式 tool parsing）的 Agent。

<!-- ===== 适配器说明结束 ===== -->
