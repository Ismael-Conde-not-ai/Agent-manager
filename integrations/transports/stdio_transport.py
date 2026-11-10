from contextlib import AbstractAsyncContextManager
from typing import Any

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client


class StdioTransport:
    def __init__(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
    ):
        self.server = StdioServerParameters(
            command=command,
            args=args or [],
            env=env,
            cwd=cwd,
        )

    def open(self) -> AbstractAsyncContextManager[tuple[Any]]:
        return stdio_client(self.server)