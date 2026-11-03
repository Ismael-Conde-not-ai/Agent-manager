import unittest
from unittest.mock import AsyncMock, Mock

from agents.executor_agent import ExecutorAgent
from integrations.execution_service import ToolExecutionService
from tools.registry import ToolRegistry


class TestToolRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = ToolRegistry()

    def test_register_local_tool(self):
        def sample_tool(agent):
            return "Executed"

        self.registry.register("sample", sample_tool)

        self.assertIn("sample", self.registry.list_tools())
        self.assertEqual(
            self.registry.get_tool("sample")["type"],
            "local",
        )

    def test_execute_local_tool(self):
        def sample_tool(agent):
            return "Executed"

        self.registry.register("sample", sample_tool)

        result = self.registry.execute("sample", Mock())

        self.assertEqual(result, "Executed")

    def test_register_mcp_tool(self):
        self.registry.register_mcp(
            name="external_search",
            server_name="test_server",
            tool_name="search",
            description="Search external information",
        )

        tool = self.registry.get_tool("external_search")

        self.assertEqual(tool["type"], "mcp")
        self.assertEqual(tool["server_name"], "test_server")
        self.assertIn("external_search", self.registry.list_tools())

    def test_mcp_tool_cannot_execute_as_local(self):
        self.registry.register_mcp(
            name="external_search",
            server_name="test_server",
            tool_name="search",
        )

        with self.assertRaises(ValueError):
            self.registry.execute("external_search", Mock())


class TestExecutorAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.registry = ToolRegistry()
        self.mcp_manager = Mock()
        self.mcp_manager.call_tool = AsyncMock()

        self.service = ToolExecutionService(
            tool_registry=self.registry,
            mcp_manager=self.mcp_manager,
        )

        self.executor = ExecutorAgent(
            tool_execution_service=self.service
        )

        self.agent = Mock()
        self.agent.memory_manager = None

    async def test_local_tool_execution(self):
        self.registry.register(
            "work",
            lambda agent: "Work completed successfully",
        )

        result = await self.executor.execute_step(
            {
                "step": 1,
                "action": "work",
                "description": "Perform work",
            },
            self.agent,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "work")
        self.assertEqual(
            result["result"],
            "Work completed successfully",
        )
        self.assertEqual(result["source"], "local")

    async def test_unknown_tool(self):
        result = await self.executor.execute_step(
            {
                "step": 1,
                "action": "unknown_tool",
            },
            self.agent,
        )

        self.assertFalse(result["success"])
        self.assertIn("not registered", result["error"])

    async def test_mcp_tool_execution(self):
        self.registry.register_mcp(
            name="external_search",
            server_name="test_server",
            tool_name="search",
        )

        self.mcp_manager.call_tool.return_value = Mock(
            is_error=False,
            content=[Mock(text="External result")],
            structuredContent=None,
        )

        result = await self.executor.execute_step(
            {
                "step": 1,
                "action": "external_search",
                "arguments": {"query": "MCP"},
            },
            self.agent,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "external_search")
        self.assertEqual(result["result"], "External result")
        self.assertEqual(result["source"], "mcp")

        self.mcp_manager.call_tool.assert_awaited_once_with(
            server_name="test_server",
            tool_name="search",
            arguments={"query": "MCP"},
        )

    
    def test_unregister_tool(self):
        self.registry.register("work", lambda agent: "working")

        result = self.registry.unregister("work")

        self.assertTrue(result)
        self.assertIsNone(self.registry.get_tool("work"))


    def test_unregister_nonexistent_tool(self):
        result = self.registry.unregister("unknown")

        self.assertFalse(result)


    def test_unregister_mcp_server_preserves_other_tools(self):
        self.registry.register("work", lambda agent: "working")

        self.registry.register_mcp(
            name="server_a.read",
            server_name="server_a",
            tool_name="read"
        )

        self.registry.register_mcp(
            name="server_a.write",
            server_name="server_a",
            tool_name="write"
        )

        self.registry.register_mcp(
            name="server_b.query",
            server_name="server_b",
            tool_name="query"
        )

        removed = self.registry.unregister_mcp_server("server_a")

        self.assertEqual(removed, 2)
        self.assertIsNotNone(self.registry.get_tool("work"))
        self.assertIsNone(self.registry.get_tool("server_a.read"))
        self.assertIsNone(self.registry.get_tool("server_a.write"))
        self.assertIsNotNone(self.registry.get_tool("server_b.query"))



if __name__ == "__main__":
    unittest.main()