
from typing import Any  # noqa: F401

from integrations.client import MCPClient
from integrations.transport_factory import MCPTransportFactory


class MCPManager:
    def __init__(self, tool_registry=None):
        self.clients: dict[str, MCPClient] = {}
        self.tool_registry = tool_registry

    async def connect_server(
        self,
        server_name,
        command=None,
        args=None,
        env=None,
        cwd=None,
        transport=None,
    ):
        if server_name in self.clients:
            raise ValueError(
                f"Server '{server_name}' is already connected"
            )

        client = MCPClient(server_name)

        if transport is not None:
            await client.connect(transport=transport)
        else:
            await client.connect(
                command=command,
                args=args,
                env=env,
                cwd=cwd,
            )

        self.clients[server_name] = client

        try:
            tools = await client.list_tools()
            self._register_tools(server_name, tools)
            return tools

        except Exception:
            try:
                await client.close()
            finally:
                self.clients.pop(server_name, None)
                self._unregister_tools(server_name)
            raise

    
    async def connect_configured_servers(self, config_loader):
        servers = config_loader.load_enabled_servers()

        connected_servers = []
        results = {}

        try:
            for server_config in servers:
                server_name = server_config["name"]

                transport = MCPTransportFactory.create(
                    server_config
                )

                tools = await self.connect_server(
                    server_name=server_name,
                    transport=transport,
                )

                connected_servers.append(server_name)
                results[server_name] = tools

        except Exception as connection_error:
            cleanup_errors = []

            for server_name in reversed(connected_servers):
                try:
                    await self.disconnect_server(server_name)
                except Exception as cleanup_error:  # noqa: BLE001
                    cleanup_errors.append(cleanup_error)

            if cleanup_errors:
                raise ExceptionGroup(
                    "MCP startup failed and some connections "
                    "could not be cleaned up",
                    [connection_error, *cleanup_errors],
                ) from connection_error

            raise

        return results


    def _register_tools(self, server_name, tools):
        if self.tool_registry is None:
            return

        for tool in tools:
            self.tool_registry.register_mcp(
                name=f"{server_name}.{tool['name']}",
                server_name=server_name,
                tool_name=tool["name"],
                description=tool.get("description", ""),
                input_schema=tool.get("input_schema", {})
            )

    def _unregister_tools(self, server_name):
        if self.tool_registry is None:
            return 0

        return self.tool_registry.unregister_mcp_server(server_name)

    async def list_servers(self):
        return list(self.clients.keys())

    async def list_tools(self, server_name):
        client = self._get_client(server_name)
        return await client.list_tools()

    async def call_tool(
        self,
        server_name,
        tool_name,
        arguments=None
    ):
        client = self._get_client(server_name)

        return await client.call_tool(
            tool_name,
            arguments or {}
        )

    async def disconnect_server(self, server_name):
        client = self._get_client(server_name)

        try:
            await client.close()
        finally:
            self.clients.pop(server_name, None)
            self._unregister_tools(server_name)

    async def close_all(self):
        errors = []

        for server_name, client in reversed(list(self.clients.items())):
            try:
                await client.close()
            except Exception as error:  # noqa: BLE001
                errors.append(error)
            finally:
                self.clients.pop(server_name, None)
                self._unregister_tools(server_name)

        if errors:
            raise ExceptionGroup(
                "One or more MCP servers could not close cleanly",
                errors
            )

    def _get_client(self, server_name):
        client = self.clients.get(server_name)

        if client is None:
            raise ValueError(
                f"Server '{server_name}' is not connected"
            )

        return client
