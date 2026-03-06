import unittest


class TestToolkitRegistry(unittest.TestCase):
    def test_toolkit_registry_idempotent(self) -> None:
        from utils.toolkit_registry import ensure_toolkit_initialized

        a = ensure_toolkit_initialized()
        b = ensure_toolkit_initialized()
        self.assertIs(a, b)
        self.assertTrue(hasattr(a, "tools"))
