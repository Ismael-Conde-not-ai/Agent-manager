import unittest
from unittest.mock import AsyncMock, Mock

from integrations.manager import MCPManager


class FakeMCPClient:
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.connect = AsyncMock()
        self.list_tools = AsyncMock(
            return_value=[
                {
                    "name": "add_numbers",
                    "description": "Add two numbers.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "integer"},
                            "b": {"type": "integer"},
                        },
                    },
                }
            ]
        )
        self.call_tool = AsyncMock(return_value="30")
        self.close = AsyncMock()


class TestMCPManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.registry = Mock()
        self.manager = MCPManager(tool_registry=self.registry)

    async def test_connect_server_discovers_tools(self):
        with unittest.mock.patch(
            "integrations.manager.MCPClient",
            FakeMCPClient,
        ):
            tools = await self.manager.connect_server(
                server_name="calculator",
                command="python",
                args=["server.py"],
            )

        self.assertEqual(tools[0]["name"], "add_numbers")
        self.assertEqual(await self.manager.list_servers(), ["calculator"])

    async def test_connect_server_registers_namespaced_tool(self):
        with unittest.mock.patch(
            "integrations.manager.MCPClient",
            FakeMCPClient,
        ):
            await self.manager.connect_server(
                server_name="calculator",
                command="python",
            )

        self.registry.register_mcp.assert_called_once_with(
            name="calculator.add_numbers",
            server_name="calculator",
            tool_name="add_numbers",
            description="Add two numbers.",
            input_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
            },
        )

    async def test_duplicate_server_is_rejected(self):
        with unittest.mock.patch(
            "integrations.manager.MCPClient",
            FakeMCPClient,
        ):
            await self.manager.connect_server(
                server_name="calculator",
                command="python",
            )

            with self.assertRaises(ValueError):
                await self.manager.connect_server(
                    server_name="calculator",
                    command="python",
                )

    async def test_call_tool_forwards_arguments(self):
        with unittest.mock.patch(
            "integrations.manager.MCPClient",
            FakeMCPClient,
        ):
            await self.manager.connect_server(
                server_name="calculator",
                command="python",
            )

            result = await self.manager.call_tool(
                "calculator",
                "add_numbers",
                {"a": 10, "b": 20},
            )

        self.assertEqual(result, "30")
        client = self.manager.clients["calculator"]
        client.call_tool.assert_awaited_once_with(
            "add_numbers",
            {"a": 10, "b": 20},
        )

    async def test_disconnect_closes_and_removes_server(self):
        with unittest.mock.patch(
            "integrations.manager.MCPClient",
            FakeMCPClient,
        ):
            await self.manager.connect_server(
                server_name="calculator",
                command="python",
            )
            client = self.manager.clients["calculator"]

            await self.manager.disconnect_server("calculator")

        client.close.assert_awaited_once()
        self.assertEqual(await self.manager.list_servers(), [])

    async def test_missing_server_raises_error(self):
        with self.assertRaises(ValueError):
            await self.manager.call_tool(
                "missing",
                "some_tool",
                {},
            )

    async def test_discovery_failure_closes_client_and_removes_server(self):
        class FailingClient(FakeMCPClient):
            def __init__(self, server_name):
                super().__init__(server_name)
                self.list_tools.side_effect = RuntimeError(
                    "Discovery failed"
                )

        with unittest.mock.patch(  # noqa: SIM117
            "integrations.manager.MCPClient",
            FailingClient,
        ):
            with self.assertRaisesRegex(RuntimeError, "Discovery failed"):
                await self.manager.connect_server(
                    server_name="broken",
                    command="python",
                )

        self.assertEqual(await self.manager.list_servers(), [])

    async def test_disconnect_removes_server_tools(self):
        registry = Mock()
        registry.unregister_mcp_server.return_value = 2

        manager = MCPManager(tool_registry=registry)

        client = Mock()
        client.close = AsyncMock()

        manager.clients["server_a"] = client

        await manager.disconnect_server("server_a")

        client.close.assert_awaited_once()
        registry.unregister_mcp_server.assert_called_once_with("server_a")

        self.assertNotIn("server_a", manager.clients)


    async def test_close_all_removes_tools_from_all_servers(self):
        registry = Mock()
        manager = MCPManager(tool_registry=registry)

        client_a = Mock()
        client_a.close = AsyncMock()

        client_b = Mock()
        client_b.close = AsyncMock()

        manager.clients["server_a"] = client_a
        manager.clients["server_b"] = client_b

        await manager.close_all()

        client_a.close.assert_awaited_once()
        client_b.close.assert_awaited_once()

        self.assertEqual(manager.clients, {})

        self.assertEqual(
            registry.unregister_mcp_server.call_count,
            2
        )


    async def test_close_all_continues_if_server_fails(self):
        registry = Mock()
        manager = MCPManager(tool_registry=registry)

        client_a = Mock()
        client_a.close = AsyncMock(
            side_effect=RuntimeError("Connection error")
        )

        client_b = Mock()
        client_b.close = AsyncMock()

        manager.clients["server_a"] = client_a
        manager.clients["server_b"] = client_b

        with self.assertRaises(ExceptionGroup):
            await manager.close_all()

        client_a.close.assert_awaited_once()
        client_b.close.assert_awaited_once()

        self.assertEqual(manager.clients, {})

        self.assertEqual(
            registry.unregister_mcp_server.call_count,
            2
        )

    
    async def test_connect_configured_servers(self):
        from integrations.manager import MCPManager

        config_loader = Mock()
        config_loader.load_enabled_servers.return_value = [
            {"name": "server_stdio"},
            {"name": "server_http"},
        ]

        stdio_transport = Mock()
        http_transport = Mock()

        with unittest.mock.patch(
            "integrations.manager.MCPClient",
            FakeMCPClient,
        ), unittest.mock.patch(
            "integrations.manager.MCPTransportFactory.create",
            side_effect=[stdio_transport, http_transport],
        ) as factory:

            results = await self.manager.connect_configured_servers(
                config_loader
            )

        self.assertEqual(
            set(results.keys()),
            {"server_stdio", "server_http"}
        )

        self.assertEqual(
            set(await self.manager.list_servers()),
            {"server_stdio", "server_http"}
        )

        self.assertEqual(factory.call_count, 2)

        self.manager.clients["server_stdio"].connect.assert_awaited_once_with(
            transport=stdio_transport
        )

        self.manager.clients["server_http"].connect.assert_awaited_once_with(
            transport=http_transport
        )


    async def test_disabled_servers_are_not_connected(self):
        config_loader = Mock()
        config_loader.load_enabled_servers.return_value = [
            {"name": "enabled_server"}
        ]

        with unittest.mock.patch(
            "integrations.manager.MCPClient",
            FakeMCPClient,
        ), unittest.mock.patch(
            "integrations.manager.MCPTransportFactory.create",
            return_value=Mock(),
        ) as factory:

            await self.manager.connect_configured_servers(
                config_loader
            )

        self.assertEqual(
            await self.manager.list_servers(),
            ["enabled_server"]
        )

        factory.assert_called_once()


    async def test_configured_connection_failure_rolls_back(self):
        config_loader = Mock()
        config_loader.load_enabled_servers.return_value = [
            {"name": "server_a"},
            {"name": "server_b"},
        ]

        clients = {}

        def create_client(server_name):
            client = FakeMCPClient(server_name)
            clients[server_name] = client

            if server_name == "server_b":
                client.connect.side_effect = RuntimeError(
                    "Connection failed"
                )

            return client

        with unittest.mock.patch(  # noqa: SIM117
            "integrations.manager.MCPClient",
            side_effect=create_client,
        ), unittest.mock.patch(
            "integrations.manager.MCPTransportFactory.create",
            return_value=Mock(),
        ):

            with self.assertRaisesRegex(
                RuntimeError,
                "Connection failed"
            ):
                await self.manager.connect_configured_servers(
                    config_loader
                )

        clients["server_a"].close.assert_awaited_once()

        self.assertEqual(
            await self.manager.list_servers(),
            []
        )


    async def test_rollback_preserves_previously_connected_servers(self):
        existing_client = FakeMCPClient("existing_server")

        self.manager.clients["existing_server"] = existing_client

        config_loader = Mock()
        config_loader.load_enabled_servers.return_value = [
            {"name": "new_server"},
            {"name": "existing_server"},
        ]

        clients = {}

        def create_client(server_name):
            client = FakeMCPClient(server_name)
            clients[server_name] = client
            return client

        with unittest.mock.patch(  # noqa: SIM117
            "integrations.manager.MCPClient",
            side_effect=create_client,
        ), unittest.mock.patch(
            "integrations.manager.MCPTransportFactory.create",
            return_value=Mock(),
        ):

            with self.assertRaisesRegex(ValueError, "already connected"):
                await self.manager.connect_configured_servers(
                    config_loader
                )

        clients["new_server"].close.assert_awaited_once()

        existing_client.close.assert_not_awaited()

        self.assertEqual(
            await self.manager.list_servers(),
            ["existing_server"]
        )




if __name__ == "__main__":
    unittest.main()