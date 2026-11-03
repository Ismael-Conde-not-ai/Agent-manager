import sys
import unittest
from pathlib import Path

from integrations.client import MCPClient

SERVER_PATH = Path(__file__).with_name("mcp_test_server.py")


class TestMCPRealServer(unittest.IsolatedAsyncioTestCase):

    async def connect_client(self):
        client = MCPClient("local_test_server")
        await client.connect(
            command=sys.executable,
            args=[str(SERVER_PATH)],
        )
        return client

    async def test_discover_tools(self):
        client = await self.connect_client()
        try:
            tools = await client.list_tools()
            names = {tool["name"] for tool in tools}

            self.assertIn("add_numbers", names)
            self.assertIn("greet", names)
        finally:
            await client.close()

    async def test_call_add_numbers(self):
        client = await self.connect_client()
        try:
            result = await client.call_tool(
                "add_numbers",
                {"a": 10, "b": 20},
            )

            self.assertFalse(result.is_error)
            self.assertTrue(result.content)
            self.assertEqual(result.content[0].text, "30")
        finally:
            await client.close()

    async def test_call_greet(self):
        client = await self.connect_client()
        try:
            result = await client.call_tool(
                "greet",
                {"name": "Ismael"},
            )

            self.assertFalse(result.is_error)
            self.assertEqual(
                result.content[0].text,
                "Hello, Ismael!",
            )
        finally:
            await client.close()


if __name__ == "__main__":
    unittest.main()