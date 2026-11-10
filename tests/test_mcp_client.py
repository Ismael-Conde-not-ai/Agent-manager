
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from integrations.client import MCPClient


class TestMCPClient(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = MCPClient("test_server")

        # Simulate the STDIO transport adapter.
        self.stdio_context = MagicMock()
        self.stdio_context.__aenter__ = AsyncMock(
            return_value=("read_stream", "write_stream")
        )
        self.stdio_context.__aexit__ = AsyncMock(return_value=False)

        self.stdio_transport = MagicMock(spec=["open"])
        self.stdio_transport.open.return_value = self.stdio_context

        # Simulate the MCP session.
        self.session = MagicMock()
        self.session.initialize = AsyncMock()
        self.session.list_tools = AsyncMock()
        self.session.call_tool = AsyncMock()

        self.session_context = MagicMock()
        self.session_context.__aenter__ = AsyncMock(
            return_value=self.session
        )
        self.session_context.__aexit__ = AsyncMock(return_value=False)

        self.transport_patch = patch(
            "integrations.client.StdioTransport",
            return_value=self.stdio_transport,
        )

        self.session_patch = patch(
            "integrations.client.ClientSession",
            return_value=self.session_context,
        )

        self.mock_transport = self.transport_patch.start()
        self.mock_session = self.session_patch.start()

    def tearDown(self):
        self.transport_patch.stop()
        self.session_patch.stop()

    async def test_client_initialization(self):
        self.assertEqual(self.client.server_name, "test_server")
        self.assertIsNone(self.client.session)
        self.assertFalse(self.client._connected)

    async def test_connect_to_server(self):
        await self.client.connect(
            command="python",
            args=["server.py"],
        )

        self.assertTrue(self.client._connected)
        self.assertIs(self.client.session, self.session)
        self.session.initialize.assert_awaited_once()

        self.mock_transport.assert_called_once_with(
            command="python",
            args=["server.py"],
            env=None,
            cwd=None,
        )

    async def test_discover_tools(self):
        self.session.list_tools.return_value = SimpleNamespace(
            tools=[
                SimpleNamespace(
                    name="search",
                    description="Search information",
                    input_schema={"type": "object"},
                )
            ]
        )

        await self.client.connect(command="python")
        tools = await self.client.list_tools()

        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["name"], "search")
        self.assertEqual(
            tools[0]["description"],
            "Search information",
        )
        self.assertEqual(
            tools[0]["input_schema"],
            {"type": "object"},
        )

    async def test_call_tool(self):
        expected_result = {"content": "Search completed"}
        self.session.call_tool.return_value = expected_result

        await self.client.connect(command="python")

        result = await self.client.call_tool(
            "search",
            {"query": "MCP"},
        )

        self.assertEqual(result, expected_result)
        self.session.call_tool.assert_awaited_once_with(
            "search",
            arguments={"query": "MCP"},
        )

    async def test_operations_require_connection(self):
        with self.assertRaises(RuntimeError):
            await self.client.list_tools()

        with self.assertRaises(RuntimeError):
            await self.client.call_tool("search")

    async def test_empty_tool_name(self):
        await self.client.connect(command="python")

        with self.assertRaises(ValueError):
            await self.client.call_tool(" ")

    async def test_duplicate_connection_is_rejected(self):
        await self.client.connect(command="python")

        with self.assertRaises(RuntimeError):
            await self.client.connect(command="python")

    async def test_close_connection(self):
        await self.client.connect(command="python")
        await self.client.close()

        self.assertFalse(self.client._connected)
        self.assertIsNone(self.client.session)
        self.stdio_context.__aexit__.assert_awaited_once()
        self.session_context.__aexit__.assert_awaited_once()

    async def test_initialization_failure_cleans_resources(self):
        self.session.initialize.side_effect = RuntimeError(
            "Initialization failed"
        )

        with self.assertRaises(RuntimeError):
            await self.client.connect(command="python")

        self.assertFalse(self.client._connected)
        self.assertIsNone(self.client.session)
        self.stdio_context.__aexit__.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
