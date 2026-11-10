
import unittest

from integrations.config_loader import MCPConfigLoader
from integrations.manager import MCPManager
from tools.registry import ToolRegistry


class TestMCPConfiguredIntegration(unittest.IsolatedAsyncioTestCase):

    async def test_connect_configured_http_server(self):
        registry = ToolRegistry()
        manager = MCPManager(tool_registry=registry)

        config_loader = MCPConfigLoader()

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
