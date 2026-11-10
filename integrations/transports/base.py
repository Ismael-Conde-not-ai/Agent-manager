from contextlib import AbstractAsyncContextManager
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MCPTransport(Protocol):
    """
    Common interface for MCP transports.
    """

    def open(self) -> AbstractAsyncContextManager[tuple[Any]]:
        """
        Open the transport and provide MCP communication streams.
        """
        ...