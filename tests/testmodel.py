from openai import OpenAI
import os
import time

# 初始化OpenAI客户端
client = OpenAI(
    # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
    api_key="sk-1c388ebc51da4e9ca6f7993d2d3ad7b1",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

messages = [{"role": "user", "content": "你好你是谁"}]
start_ts = time.monotonic()
completion = client.chat.completions.create(
    model="glm-5",
    messages=messages,
    # 通过 extra_body 设置 enable_thinking 开启思考模式
    extra_body={"enable_thinking": False},
    stream=True,
    stream_options={
        "include_usage": True
    },
)

reasoning_content = ""
answer_content = ""
is_answering = False
first_delta_ts = None
done_ts = None
print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

for chunk in completion:
    if not chunk.choices:
        print("\n" + "=" * 20 + "Token 消耗" + "=" * 20 + "\n")
        print(chunk.usage)
        continue

    delta = chunk.choices[0].delta

    if first_delta_ts is None:
        first_delta_ts = time.monotonic()
        print(f"\n首片段耗时: {(first_delta_ts - start_ts) * 1000:.1f} ms\n")

    if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
        if not is_answering:
            print(delta.reasoning_content, end="", flush=True)
        reasoning_content += delta.reasoning_content

    # 收到content，开始进行回复
    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
            is_answering = True
        print(delta.content, end="", flush=True)
        answer_content += delta.content

done_ts = time.monotonic()
if done_ts is not None:
    print(f"\n完整回复耗时: {(done_ts - start_ts) * 1000:.1f} ms")
