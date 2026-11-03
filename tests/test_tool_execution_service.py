
import unittest
from unittest.mock import AsyncMock, Mock

from integrations.execution_service import ToolExecutionService
from tools.registry import ToolRegistry


class TestToolExecutionService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.registry = ToolRegistry()
        self.mcp_manager = Mock()
        self.service = ToolExecutionService(
            self.registry,
            self.mcp_manager,
        )

    async def test_execute_local_tool(self):
        handler = Mock(return_value={"success": True})

        self.registry.register("work", handler)

        result = await self.service.execute(
            "work",
            agent="test-agent",
        )

        handler.assert_called_once_with("test-agent")
        self.assertEqual(result, {"success": True})

    async def test_execute_mcp_tool(self):
        self.registry.register_mcp(
            name="calculator.add_numbers",
            server_name="calculator",
            tool_name="add_numbers",
            description="Add two numbers",
        )

        self.mcp_manager.call_tool = AsyncMock(
            return_value=Mock(
                is_error=False,
                content=[Mock(text="30")],
                structuredContent=None,
            )
        )

        result = await self.service.execute(
            "calculator.add_numbers",
            arguments={"a": 10, "b": 20},
        )

        self.mcp_manager.call_tool.assert_awaited_once_with(
            server_name="calculator",
            tool_name="add_numbers",
            arguments={"a": 10, "b": 20},
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "30")
        self.assertEqual(result["source"], "mcp")

    async def test_execute_mcp_tool_with_error(self):
        self.registry.register_mcp(
            name="calculator.divide",
            server_name="calculator",
            tool_name="divide",
        )

        self.mcp_manager.call_tool = AsyncMock(
            return_value=Mock(
                is_error=True,
                content=[Mock(text="Division error")],
                structuredContent=None,
            )
        )

        result = await self.service.execute(
            "calculator.divide",
            arguments={"a": 10, "b": 0},
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["result"],
            ["Division error"],
        )

    async def test_unknown_tool_raises_error(self):
        with self.assertRaises(ValueError):
            await self.service.execute("unknown_tool")


if __name__ == "__main__":
    unittest.main()
