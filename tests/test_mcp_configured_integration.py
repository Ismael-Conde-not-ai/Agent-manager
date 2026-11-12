
import unittest

from integrations.manager import MCPManager
from tools.registry import ToolRegistry
from tests.mcp_http_server_fixture import running_http_server
from unittest.mock import Mock


class TestMCPConfiguredIntegration(unittest.IsolatedAsyncioTestCase):

    async def test_connect_configured_http_server(self):
        async with running_http_server() as url:
            await self._test_connect_configured_http_server(url)

    async def _test_connect_configured_http_server(self, url):
        registry = ToolRegistry()
        manager = MCPManager(tool_registry=registry)
        config_loader = Mock()
        config_loader.load_enabled_servers.return_value = [{
            "name": "http_test_server",
            "transport": {"type": "streamable-http", "url": url},
            "enabled": True,
        }]

        try:
            results = await manager.connect_configured_servers(
                config_loader
            )

            self.assertIn("http_test_server", results)

            tools = registry.list_tools()

            self.assertIn(
                "http_test_server.add_numbers",
                tools
            )

            self.assertIn(
                "http_test_server.greet",
                tools
            )

        finally:
            await manager.close_all()


if __name__ == "__main__":
    unittest.main()
