import importlib
import unittest


class TestLilaAgent(unittest.TestCase):
    def test_lila_agent_can_instantiate(self) -> None:
        module = importlib.import_module("agents.king.King_Lila.lila_agent")
        agent_cls = getattr(module, "LilaAgent")
        agent = agent_cls()
        self.assertEqual(getattr(agent, "name", ""), "Lila")

    def test_lila_agent_chat_stream_fallback_without_env(self) -> None:
        module = importlib.import_module("agents.king.King_Lila.lila_agent")
        agent_cls = getattr(module, "LilaAgent")
        agent = agent_cls()
        chunks = list(agent.chat_stream("你好"))
        self.assertGreaterEqual(len(chunks), 1)
        self.assertTrue(isinstance(chunks[0], str))
