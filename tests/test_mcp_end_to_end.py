
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from agents.executor_agent import ExecutorAgent
from integrations.config_loader import MCPConfigLoader
from integrations.execution_service import ToolExecutionService
from integrations.manager import MCPManager
from tools.registry import ToolRegistry
from tests.mcp_http_server_fixture import running_http_server

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

    
    async def test_configured_server_executes_real_mcp_tool(self):
        config = {
            "servers": [
                {
                    "name": "configured_server",
                    "command": sys.executable,
                    "args": [str(SERVER_PATH)],
                    "enabled": True
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mcp_servers.json"

            with config_path.open("w", encoding="utf-8") as file:
                json.dump(config, file)

            config_loader = MCPConfigLoader(config_path)

            try:
                await self.mcp_manager.connect_configured_servers(
                    config_loader
                )

                self.assertIn(
                    "configured_server.add_numbers",
                    self.registry.list_tools()
                )

                result = await self.executor.execute_step(
                    {
                        "action": "configured_server.add_numbers",
                        "arguments": {
                            "a": 10,
                            "b": 20
                        }
                    },
                    self.agent
                )

                self.assertTrue(result["success"])
                self.assertEqual(result["result"], "30")
                self.assertEqual(result["source"], "mcp")

            finally:
                await self.close_server()


    async def test_executor_executes_real_http_mcp_tool(self):
        async with running_http_server() as url:
            await self._test_executor_executes_real_http_mcp_tool(url)

    async def _test_executor_executes_real_http_mcp_tool(self, url):
        config_loader = Mock()
        config_loader.load_enabled_servers.return_value = (
            [{
                "name": "http_test_server",
                "transport": {
                    "type": "streamable-http",
                    "url": url,
                },
                "enabled": True,
            }]
        )

        try:
            await self.mcp_manager.connect_configured_servers(
                config_loader
            )

            result = await self.executor.execute_step(
                {
                    "action": "http_test_server.add_numbers",
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
                "http_test_server.add_numbers"
            )
            self.assertEqual(result["result"], "30")
            self.assertEqual(result["source"], "mcp")

        finally:
            await self.close_server()



if __name__ == "__main__":
    unittest.main()
