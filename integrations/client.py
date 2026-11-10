
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession

from integrations.transports.base import MCPTransport
from integrations.transports.stdio_transport import StdioTransport


class MCPClient:
    """Generic asynchronous client for a single MCP server."""

    def __init__(
        self,
        server_name: str,
        transport: MCPTransport | None = None,
    ):
        if not server_name or not server_name.strip():
            raise ValueError("Server name cannot be empty.")

        self.server_name = server_name
        self.transport = transport
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._connected = False

    async def connect(
        self,
        command: str | None = None,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
        transport: MCPTransport | None = None,
    ) -> None:
        if self._connected:
            raise RuntimeError(
                f"Server '{self.server_name}' is already connected."
            )

        selected_transport = transport or self.transport

        # Backward compatibility with the previous STDIO connection.
        if selected_transport is None and command is not None:
            selected_transport = StdioTransport(
                command=command,
                args=args,
                env=env,
                cwd=cwd,
            )

        if selected_transport is None:
            raise ValueError(
                "An MCP transport or STDIO command must be provided."
            )

        if not callable(getattr(selected_transport, "open", None)):
            raise TypeError("Invalid MCP transport.")

        self.transport = selected_transport

        try:
            read_stream, write_stream = (
                await self.exit_stack.enter_async_context(
                    selected_transport.open()
                )
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
            self._connected = False
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
