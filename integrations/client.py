
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Generic asynchronous client for a single MCP server."""

    def __init__(self, server_name: str):
        if not server_name or not server_name.strip():
            raise ValueError("Server name cannot be empty.")

        self.server_name = server_name
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._connected = False

    async def connect(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
    ) -> None:
        if self._connected:
            raise RuntimeError(
                f"Server '{self.server_name}' is already connected."
            )

        server_params = StdioServerParameters(
            command=command,
            args=args or [],
            env=env,
            cwd=cwd,
        )

        try:
            read_stream, write_stream = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            await self.session.initialize()
            self._connected = True

        except Exception:
            await self.exit_stack.aclose()
            self.exit_stack = AsyncExitStack()
            self.session = None
            raise

    async def list_tools(self) -> list[dict[str, Any]]:
        self._ensure_connected()

        response = await self.session.list_tools()

        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.input_schema,
            }
            for tool in response.tools
        ]

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        self._ensure_connected()

        if not tool_name or not tool_name.strip():
            raise ValueError("Tool name cannot be empty.")

        return await self.session.call_tool(
            tool_name,
            arguments=arguments or {},
        )

    def _ensure_connected(self) -> None:
        if not self._connected or self.session is None:
            raise RuntimeError(
                f"Server '{self.server_name}' is not connected."
            )

    async def close(self) -> None:
        await self.exit_stack.aclose()
        self.session = None
        self._connected = False
        self.exit_stack = AsyncExitStack()
