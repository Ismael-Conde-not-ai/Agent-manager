import unittest
from unittest.mock import AsyncMock, Mock

from agents.agent import AIagent
from core.contracts import Plan


class TestAIagentCompatibility(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.planner = Mock()
        self.executor = Mock()
        self.executor.execute_step = AsyncMock()
        self.orchestrator = Mock()
        self.orchestrator.run = AsyncMock()
        self.registry = Mock()
        self.memory_manager = Mock()

        self.agent = AIagent(
            name="legacy",
            goal="Complete the task",
            initial_energy=100,
            initial_status="ready",
            memory_manager=self.memory_manager,
            tool_registry=self.registry,
            planner_agent=self.planner,
            executor_agent=self.executor,
            orchestrator=self.orchestrator,
        )

    def test_composition_dependencies_are_shared(self):
        self.assertIs(self.agent.tool_registry, self.registry)
        self.assertIs(self.agent.memory_manager, self.memory_manager)
        self.assertIs(self.agent.planner_agent, self.planner)
        self.assertIs(self.agent.executor_agent, self.executor)
        self.assertIs(self.agent.orchestrator, self.orchestrator)

    def test_create_plan_delegates_to_planner(self):
        plan = Plan.from_legacy(
            [
                {
                    "step": 1,
                    "action": "work",
                    "description": "Complete the task.",
                },
                {
                    "step": 2,
                    "action": "rest",
                    "description": "Finish safely.",
                },
            ]
        )
        self.planner.create_plan.return_value = plan
        self.planner.parse_plan.return_value = plan

        result = self.agent.create_plan()

        self.assertIs(result, plan)
        self.assertIs(self.agent.plan, plan)
        self.planner.create_plan.assert_called_once_with(
            "Complete the task"
        )

    async def test_autonomous_step_delegates_to_orchestrator_once(self):
        workflow_result = Mock()
        workflow_result.final_execution = None
        workflow_result.final_plan = None
        self.orchestrator.run.return_value = workflow_result

        result = await self.agent.autonomous_step()

        self.assertIs(result, workflow_result)
        self.orchestrator.run.assert_awaited_once_with(
            "Complete the task",
            self.agent,
            max_retries=0,
        )
        self.executor.execute_step.assert_not_called()

    def test_execute_tool_delegates_to_shared_executor(self):
        tool_result = Mock(success=True, result="done")
        self.executor.execute_step.return_value = tool_result
        self.agent.save_memory = Mock()
        self.agent.reflect_on_action = Mock(return_value="done")

        self.assertTrue(self.agent.execute_tool("work"))

        self.executor.execute_step.assert_awaited_once()
        self.registry.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
