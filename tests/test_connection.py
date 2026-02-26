import asyncio
from agentscope.message import Msg

from agents.queen.Queen_Sera import SeraAgent


async def main():
    agent = SeraAgent()
    msg = Msg(name="User", content="你好，请介绍一下你自己。", role="user")
    response = await agent.reply(msg)
    print(f"\nAgent Response:\n{response.content}")

if __name__ == "__main__":
    asyncio.run(main())
