

from integrations.transports.http_transport import (
    StreamableHTTPTransport,
)
from integrations.transports.stdio_transport import StdioTransport


class MCPTransportFactory:

    @staticmethod
    def create(server_config):
        transport_config = server_config.get("transport")

        # Backward compatibility with the old STDIO format.
        if transport_config is None:
            transport_config = server_config
            transport_type = "stdio"
        else:
            if not isinstance(transport_config, dict):
                raise ValueError("Transport configuration must be an object")

            transport_type = transport_config.get("type")

        if transport_type == "stdio":
            return StdioTransport(
                command=transport_config.get("command"),
                args=transport_config.get("args"),
                env=transport_config.get("env"),
                cwd=transport_config.get("cwd"),
            )

        if transport_type == "streamable-http":
            return StreamableHTTPTransport(
                url=transport_config.get("url")
            )

        raise ValueError(
            f"Unsupported MCP transport: {transport_type}"
        )
