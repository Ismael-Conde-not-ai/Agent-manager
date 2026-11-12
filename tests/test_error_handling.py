import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient
from pydantic import ValidationError as PydanticValidationError

from agents.evaluator_agent import EvaluatorAgent
from agents.executor_agent import ExecutorAgent
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from api.server import app
from core.contracts import (
    ErrorCategory,
    ErrorInfo,
    ExecutionResult,
    Plan,
    PlanStep,
    ToolResult,
)
from core.exceptions import (
    EvaluationError,
    InternalAgentError,
    MCPCommunicationError,
    PlanningError,
    ToolExecutionError,
    ValidationError,
)
from core.orchestrator import Orchestrator
from integrations.execution_service import ToolExecutionService
from tools.registry import ToolRegistry


class TestDomainErrors(unittest.TestCase):

    def test_errors_keep_category_details_and_cause(self):
        cause = RuntimeError("private implementation detail")
        error = ToolExecutionError(
            "Tool failed.",
            code="tool_failed",
            details={"tool_name": "work"},
            cause=cause,
        )

        info = error.to_error_info()

        self.assertIs(error.__cause__, cause)
        self.assertEqual(info.category, ErrorCategory.TOOL)
        self.assertEqual(info.details, {"tool_name": "work"})
        self.assertEqual(info.code, "tool_failed")

    def test_failed_tool_result_requires_error(self):
        with self.assertRaises(PydanticValidationError):
            ToolResult(
                success=False,
                action="work",
                source="local",
            )

    def test_invalid_execution_object_is_explicit_failure(self):
        result = ExecutionResult.from_legacy("invalid")

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_execution_result")


class TestAgentErrors(unittest.IsolatedAsyncioTestCase):

    def test_research_retrieval_error_is_classified(self):
        knowledge = Mock()
        knowledge.get_context.side_effect = RuntimeError("database detail")

        with self.assertRaises(InternalAgentError) as raised:
            ResearchAgent(knowledge_base=knowledge).research("question")

        self.assertEqual(raised.exception.code, "research_retrieval_failed")
        self.assertIsInstance(raised.exception.__cause__, RuntimeError)

    def test_planner_model_error_is_classified(self):
        planner = PlannerAgent()
        with patch(
            "agents.planner_agent.geminiAI",
            side_effect=RuntimeError("provider detail"),
        ):
            with self.assertRaises(PlanningError):
                planner.create_plan("goal")

    def test_evaluator_model_error_is_classified(self):
        with patch(
            "agents.evaluator_agent.geminiAI",
            side_effect=RuntimeError("provider detail"),
        ):
            with self.assertRaises(EvaluationError):
                EvaluatorAgent().evaluate("goal", "research", "plan", "execution")

    async def test_executor_tool_error_is_structured(self):
        registry = ToolRegistry()
        registry.register("work", lambda agent: (_ for _ in ()).throw(
            RuntimeError("tool detail")
        ))
        service = ToolExecutionService(registry, Mock())
        executor = ExecutorAgent(service)

        result = await executor.execute_step(
            {"step": 1, "action": "work", "description": "work"},
            Mock(memory_manager=None),
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.category, ErrorCategory.TOOL)
        self.assertEqual(result.error.code, "local_tool_failed")


class TestOrchestratorErrors(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.research = Mock()
        self.planner = Mock()
        self.executor = Mock()
        self.executor.execute_plan = AsyncMock()
        self.evaluator = Mock()
        self.orchestrator = Orchestrator(
            research_agent=self.research,
            planner_agent=self.planner,
            executor_agent=self.executor,
            evaluator_agent=self.evaluator,
        )

        self.plan = Plan(
            steps=[
                PlanStep(
                    step=1,
                    action="work",
                    description="Complete work",
                )
            ]
        )
        self.research.research.return_value = "evidence"
        self.planner.create_plan.return_value = self.plan
        self.planner.parse_plan.return_value = self.plan
        self.planner.validate_plan.return_value = (True, None)
        self.executor.execute_plan.return_value = ExecutionResult(
            success=False,
            results=[],
            error=ErrorInfo(
                code="fatal_execution",
                message="Execution failed",
                category=ErrorCategory.EXECUTION,
                retryable=False,
            ),
        )
        self.evaluator.evaluate.return_value = {
            "success": True,
            "evaluation": "not reached",
        }

    async def test_research_error_finishes_without_planning(self):
        self.research.research.side_effect = InternalAgentError(
            "Research failed",
            code="research_failed",
        )

        result = await self.orchestrator.run("goal", Mock(), max_retries=2)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "research_failed")
        self.planner.create_plan.assert_not_called()

    async def test_non_retryable_execution_error_is_not_repeated(self):
        result = await self.orchestrator.run("goal", Mock(), max_retries=3)

        self.assertFalse(result.success)
        self.assertEqual(result.total_attempts, 1)
        self.executor.execute_plan.assert_awaited_once()


class TestApiErrors(unittest.TestCase):

    def test_internal_error_does_not_expose_cause(self):
        with patch(
            "api.server.research_agent.research",
            side_effect=InternalAgentError(
                "provider password=secret",
                code="research_failed",
            ),
        ), patch(
            "api.server.manager.mcp_manager.connect_configured_servers",
            new_callable=AsyncMock,
        ), patch(
            "api.server.manager.mcp_manager.close_all",
            new_callable=AsyncMock,
        ):
            with TestClient(app) as client:
                response = client.post(
                    "/research",
                    params={"query": "question"},
                )

        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertEqual(body["error"]["code"], "research_failed")
        self.assertNotIn("secret", response.text)


if __name__ == "__main__":
    unittest.main()
