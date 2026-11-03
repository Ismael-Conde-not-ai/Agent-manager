
from typing import Any

from integrations.client import MCPClient


class MCPManager:
    def __init__(self, tool_registry=None):
        self.clients: dict[str, MCPClient] = {}
        self.tool_registry = tool_registry

    async def connect_server(
        self,
        server_name,
        command,
        args=None,
        env=None,
        cwd=None
    ):
        if server_name in self.clients:
            raise ValueError(
                f"Server '{server_name}' is already connected"
            )

        client = MCPClient(server_name)
        await client.connect(
            command=command,
            args=args,
            env=env,
            cwd=cwd
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

        for server_name, client in list(self.clients.items()):
            try:
                await client.close()
            except Exception as error:
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
