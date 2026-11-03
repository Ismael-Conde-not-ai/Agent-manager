from integrations.execution_service import ToolExecutionService
from integrations.manager import MCPManager
from memory.memory_manager import MemoryManager
from tools.recharge import recharge
from tools.registry import ToolRegistry
from tools.rest import rest
from tools.search_knowledge import search_knowledge
from tools.work import work


class Manager:

    def __init__(self):
        self.agents = {}
        self.memory_manager = MemoryManager()

        # Shared registry for local and MCP tools.
        self.tool_registry = ToolRegistry()

        # Register local tools only once.
        self.tool_registry.register("work", work)
        self.tool_registry.register("recharge", recharge)
        self.tool_registry.register("rest", rest)
        self.tool_registry.register(
            "search_knowledge",
            search_knowledge,
        )

        # Manage external MCP connections.
        self.mcp_manager = MCPManager(
            tool_registry=self.tool_registry
        )

        # Central execution service.
        self.tool_execution_service = ToolExecutionService(
            tool_registry=self.tool_registry,
            mcp_manager=self.mcp_manager,
        )

    def add_agent(self, agent):
        self.agents[agent.name] = agent

    def get_agent(self, name):
        return self.agents.get(name)

    def list_agents(self):
        return list(self.agents.keys())