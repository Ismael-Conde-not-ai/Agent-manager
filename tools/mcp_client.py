class MCPClient:
    def __init__(self):
        self.sessions = {}

    async def connect(self, server_name, command, args=None):
        """
        Connect to an MCP server.

        Args:
            server_name: Unique name for the server.
            command: Executable used to start the server.
            args: Optional command-line arguments.
        """
        raise NotImplementedError

    async def list_tools(self, server_name):
        """Return the tools available on a connected server."""
        raise NotImplementedError

    async def call_tool(self, server_name, tool_name, arguments):
        """Call a tool exposed by a connected MCP server."""
        raise NotImplementedError

    async def disconnect(self, server_name):
        """Close a connection to an MCP server."""
        raise NotImplementedError