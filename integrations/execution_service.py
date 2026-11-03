
from typing import Any

from integrations.argument_validator import MCPArgumentValidator, MCPToolExecutionError
from integrations.manager import MCPManager
from tools.registry import ToolRegistry


class ToolExecutionService:
    """
    Centraliza la ejecución de herramientas locales y MCP.
    Los agentes no necesitan conocer el tipo de herramienta.
    """

    def __init__(
        self,
        tool_registry: ToolRegistry,
        mcp_manager: MCPManager,
    ):
        self.tool_registry = tool_registry
        self.mcp_manager = mcp_manager
        self.argument_validator = MCPArgumentValidator()

    async def execute(
        self,
        tool_name: str,
        agent: Any = None,
        arguments: dict | None = None,
    ) -> Any:
        """
        Ejecuta una herramienta según su tipo.

        Las herramientas locales conservan su interfaz actual:
            handler(agent)

        Las herramientas MCP reciben:
            arguments
        """

        tool = self.tool_registry.get_tool(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool '{tool_name}' is not registered."
            )

        tool_type = tool.get("type")

        if tool_type == "local":
            return self.tool_registry.execute(
                tool_name,
                agent,
            )

        if tool_type == "mcp":
            tool_arguments = {} if arguments is None else arguments

            self.argument_validator.validate(
                arguments=tool_arguments,
                input_schema=tool.get("input_schema", {})
            )
            try:
                result = await self.mcp_manager.call_tool(
                    server_name=tool["server_name"],
                    tool_name=tool["tool_name"],
                    arguments=tool_arguments,
                )
            except Exception as error:
                raise MCPToolExecutionError(
                    f"Failed to execute MCP tool '{tool_name}': {error}"
                ) from error

            return self._normalize_mcp_result(result)

        raise ValueError(
            f"Unsupported tool type: {tool_type}"
        )

    @staticmethod
    def _normalize_mcp_result(result):
        if result.is_error:
            return {
                "success": False,
                "result": [
                    getattr(item, "text", str(item))
                    for item in result.content
                ],
                "source": "mcp",
            }

        structured_content = getattr(
            result,
            "structuredContent",
            None
        )

        if structured_content is not None:
            return {
                "success": True,
                "result": structured_content,
                "source": "mcp",
            }

        text_content = [
            item.text
            for item in result.content
            if getattr(item, "text", None) is not None
        ]

        if len(text_content) == 1:
            normalized_result = text_content[0]
        else:
            normalized_result = text_content

        return {
            "success": True,
            "result": normalized_result,
            "source": "mcp",
        }