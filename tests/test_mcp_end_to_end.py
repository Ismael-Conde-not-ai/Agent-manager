
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from agents.executor_agent import ExecutorAgent
from integrations.execution_service import ToolExecutionService
from integrations.manager import MCPManager
from tools.registry import ToolRegistry


SERVER_PATH = Path(__file__).with_name("mcp_test_server.py")


class TestMCPEndToEnd(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.registry = ToolRegistry()

        self.mcp_manager = MCPManager(
            tool_registry=self.registry
        )

        self.execution_service = ToolExecutionService(
            tool_registry=self.registry,
            mcp_manager=self.mcp_manager
        )

        self.executor = ExecutorAgent(
            tool_execution_service=self.execution_service
        )

        self.agent = Mock()
        self.agent.memory_manager = None

    async def connect_server(self):
        await self.mcp_manager.connect_server(
            server_name="local_test_server",
            command=sys.executable,
            args=[str(SERVER_PATH)]
        )

    async def close_server(self):
        await self.mcp_manager.close_all()

    async def test_tools_are_registered_dynamically(self):
        await self.connect_server()

        try:
            tools = self.registry.list_tools()

            self.assertIn(
                "local_test_server.add_numbers",
                tools
            )

            self.assertIn(
                "local_test_server.greet",
                tools
            )
        finally:
            await self.close_server()

    async def test_executor_executes_real_mcp_tool(self):
        await self.connect_server()

        try:
            result = await self.executor.execute_step(
                {
                    "action": "local_test_server.add_numbers",
                    "arguments": {
                        "a": 10,
                        "b": 20
                    }
                },
                self.agent
            )

            self.assertTrue(result["success"])
            self.assertEqual(
                result["action"],
                "local_test_server.add_numbers"
            )
            self.assertEqual(result["result"], "30")
            self.assertEqual(result["source"], "mcp")

        finally:
            await self.close_server()

    async def test_executor_executes_greeting_tool(self):
        await self.connect_server()

        try:
            result = await self.executor.execute_step(
                {
                    "action": "local_test_server.greet",
                    "arguments": {
                        "name": "Ismael"
                    }
                },
                self.agent
            )

            self.assertTrue(result["success"])
            self.assertEqual(
                result["result"],
                "Hello, Ismael!"
            )
            self.assertEqual(result["source"], "mcp")

        finally:
            await self.close_server()

    async def test_disconnected_server_tools_are_removed(self):
        await self.connect_server()

        await self.mcp_manager.disconnect_server(
            "local_test_server"
        )

        self.assertNotIn(
            "local_test_server.add_numbers",
            self.registry.list_tools()
        )

        self.assertNotIn(
            "local_test_server.greet",
            self.registry.list_tools()
        )


if __name__ == "__main__":
    unittest.main()
