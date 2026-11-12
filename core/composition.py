from dataclasses import dataclass

from agents.agent import AIagent
from agents.evaluator_agent import EvaluatorAgent
from agents.executor_agent import ExecutorAgent
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from core.manager import Manager
from core.orchestrator import Orchestrator
from integrations.execution_service import ToolExecutionService
from integrations.manager import MCPManager
from knowledge.knowledge_base import KnowledgeBase
from memory.memory_manager import MemoryManager
from tools.registry import ToolRegistry


@dataclass
class ApplicationComposition:
    manager: Manager
    orchestrator: Orchestrator
    research_agent: ResearchAgent
    planner_agent: PlannerAgent
    executor_agent: ExecutorAgent
    evaluator_agent: EvaluatorAgent

    @property
    def memory_manager(self) -> MemoryManager:
        return self.manager.memory_manager

    @property
    def knowledge_base(self) -> KnowledgeBase:
        return self.manager.knowledge_base

    @property
    def tool_registry(self) -> ToolRegistry:
        return self.manager.tool_registry

    @property
    def mcp_manager(self) -> MCPManager:
        return self.manager.mcp_manager

    @property
    def tool_execution_service(self) -> ToolExecutionService:
        return self.manager.tool_execution_service


def create_application() -> ApplicationComposition:
    memory_manager = MemoryManager()
    knowledge_base = KnowledgeBase()
    tool_registry = ToolRegistry()
    mcp_manager = MCPManager(tool_registry=tool_registry)
    tool_execution_service = ToolExecutionService(
        tool_registry=tool_registry,
        mcp_manager=mcp_manager,
    )

    manager = Manager(
        memory_manager=memory_manager,
        knowledge_base=knowledge_base,
        tool_registry=tool_registry,
        mcp_manager=mcp_manager,
        tool_execution_service=tool_execution_service,
    )

    research_agent = ResearchAgent(
        knowledge_base=knowledge_base,
    )
    planner_agent = PlannerAgent(
        memory_manager=memory_manager,
    )
    executor_agent = ExecutorAgent(
        tool_execution_service=tool_execution_service,
    )
    evaluator_agent = EvaluatorAgent()

    agents = (
        research_agent,
        planner_agent,
        executor_agent,
        evaluator_agent,
    )
    for application_agent in agents:
        manager.add_agent(application_agent)

    orchestrator = Orchestrator(
        manager=manager,
        research_agent=research_agent,
        planner_agent=planner_agent,
        executor_agent=executor_agent,
        evaluator_agent=evaluator_agent,
    )

    return ApplicationComposition(
        manager=manager,
        orchestrator=orchestrator,
        research_agent=research_agent,
        planner_agent=planner_agent,
        executor_agent=executor_agent,
        evaluator_agent=evaluator_agent,
    )
