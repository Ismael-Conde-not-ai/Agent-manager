
import asyncio

from integrations.client import MCPClient
from integrations.transports.http_transport import StreamableHTTPTransport


async def main():
    transport = StreamableHTTPTransport(
        url="http://127.0.0.1:8080/mcp"
    )

    client = MCPClient(
        server_name="http_test_server",
        transport=transport,
    )

    try:
        print("\n1. Connecting to HTTP MCP server...")
        await client.connect()
        print("Connection successful!")

        print("\n2. Discovering tools...")
        tools = await client.list_tools()

        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")

        print("\n3. Testing add_numbers...")
        result = await client.call_tool(
            "add_numbers",
            {"a": 10, "b": 20},
        )
        print("Result:", result)

        print("\n4. Testing greet...")
        result = await client.call_tool(
            "greet",
            {"name": "Ismael"},
        )
        print("Result:", result)

    except Exception as error:  # noqa: BLE001
        print(f"\nERROR: {type(error).__name__}: {error}")

    finally:
        await client.close()
        print("\nClient connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
