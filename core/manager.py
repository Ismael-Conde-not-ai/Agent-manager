from knowledge.knowledge_base import KnowledgeBase
from integrations.execution_service import ToolExecutionService
from integrations.manager import MCPManager
from memory.memory_manager import MemoryManager
from tools.recharge import recharge
from tools.registry import ToolRegistry
from tools.rest import rest
from tools.search_knowledge import search_knowledge
from tools.work import work


class Manager:

    def __init__(
        self,
        memory_manager=None,
        knowledge_base=None,
        tool_registry=None,
        mcp_manager=None,
        tool_execution_service=None,
    ):
        self.agents = {}
        self.memory_manager = (
            memory_manager
            if memory_manager is not None
            else MemoryManager()
        )
        self.knowledge_base = (
            knowledge_base
            if knowledge_base is not None
            else KnowledgeBase()
        )

        # Shared registry for local and MCP tools.
        self.tool_registry = (
            tool_registry
            if tool_registry is not None
            else ToolRegistry()
        )

        # Register local tools only once.
        self.tool_registry.register("work", work)
        self.tool_registry.register("recharge", recharge)
        self.tool_registry.register("rest", rest)
        self.tool_registry.register(
            "search_knowledge",
            search_knowledge,
        )

        # Manage external MCP connections.
        self.mcp_manager = (
            mcp_manager
            if mcp_manager is not None
            else MCPManager(tool_registry=self.tool_registry)
        )

        # Central execution service.
        self.tool_execution_service = (
            tool_execution_service
            if tool_execution_service is not None
            else ToolExecutionService(
                tool_registry=self.tool_registry,
                mcp_manager=self.mcp_manager,
            )
        )

    def add_agent(self, agent):
        self.agents[agent.name] = agent

    def get_agent(self, name):
        return self.agents.get(name)

    def list_agents(self):
        return list(self.agents.keys())