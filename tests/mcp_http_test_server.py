
import argparse
from mcp.server.mcpserver import MCPServer

server = MCPServer(name="agent-manager-http-test-server")


@server.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers and return their sum."""
    return a + b


@server.tool()
def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    server.run(
        "streamable-http",
        host="127.0.0.1",
        port=args.port,
        streamable_http_path="/mcp",
    )
