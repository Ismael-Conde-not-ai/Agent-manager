
class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = {
            "type": "local",
            "handler": func
        }

    def register_mcp(
        self,
        name,
        server_name,
        tool_name,
        description="",
        input_schema=None
    ):
        self.tools[name] = {
            "type": "mcp",
            "server_name": server_name,
            "tool_name": tool_name,
            "description": description,
            "input_schema": input_schema or {}
        }

    def get_tool(self, name):
        return self.tools.get(name)

    def execute(self, name, agent):
        tool = self.get_tool(name)

        if tool is None:
            raise ValueError(f"Tool '{name}' not registered")

        if tool["type"] != "local":
            raise ValueError(
                f"Tool '{name}' is not a local tool"
            )

        return tool["handler"](agent)

    def unregister(self, name):
        """Remove a tool from the registry."""
        if name not in self.tools:
            return False

        del self.tools[name]
        return True

    def unregister_mcp_server(self, server_name):
        """Remove all MCP tools belonging to a server."""
        tools_to_remove = [
            name
            for name, tool in self.tools.items()
            if (
                tool["type"] == "mcp"
                and tool["server_name"] == server_name
            )
        ]

        for name in tools_to_remove:
            del self.tools[name]

        return len(tools_to_remove)

    def list_tools(self):
        return list(self.tools.keys())
