import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path)

api_key = os.getenv("MODELSCOPE_API_KEY")
if api_key is None or api_key.strip() == "":
    raise RuntimeError("缺少环境变量 MODELSCOPE_API_KEY（可在仓库根目录 .env 中配置）")

client = OpenAI(
    base_url=os.getenv("MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn/v1"),
    api_key=api_key,
)

response = client.chat.completions.create(
    model=os.getenv("MODELSCOPE_MODEL_NAME", "ZhipuAI/GLM-5:DashScope"),
    messages=[
        {
            'role': 'user',
            'content': '你好'
        }
    ],
    stream=True
)
done_reasoning = False
for chunk in response:
    if chunk.choices:
        reasoning_chunk = chunk.choices[0].delta.reasoning_content
        answer_chunk = chunk.choices[0].delta.content
        if reasoning_chunk != '':
            print(reasoning_chunk, end='', flush=True)
        elif answer_chunk != '':
            if not done_reasoning:
                print('\n\n === Final Answer ===\n')
                done_reasoning = True
            print(answer_chunk, end='', flush=True)
