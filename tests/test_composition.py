import unittest

from core.composition import create_application


class TestApplicationComposition(unittest.TestCase):

    def setUp(self):
        self.application = create_application()

    def test_shared_infrastructure_instances(self):
        manager = self.application.manager

        self.assertIs(
            self.application.memory_manager,
            self.application.planner_agent.memory_manager,
        )
        self.assertIs(
            self.application.knowledge_base,
            self.application.research_agent.knowledge,
        )
        self.assertIs(
            self.application.tool_registry,
            manager.tool_registry,
        )
        self.assertIs(
            self.application.mcp_manager,
            manager.mcp_manager,
        )
        self.assertIs(
            self.application.tool_execution_service,
            self.application.executor_agent.tool_execution_service,
        )

    def test_orchestrator_receives_composed_agents(self):
        self.assertIs(
            self.application.orchestrator.agents["ResearchAgent"],
            self.application.research_agent,
        )
        self.assertIs(
            self.application.orchestrator.agents["PlannerAgent"],
            self.application.planner_agent,
        )
        self.assertIs(
            self.application.orchestrator.agents["ExecutorAgent"],
            self.application.executor_agent,
        )
        self.assertIs(
            self.application.orchestrator.agents["EvaluatorAgent"],
            self.application.evaluator_agent,
        )

    def test_manager_registry_is_shared_with_all_composed_agents(self):
        self.assertIs(
            self.application.tool_registry,
            self.application.manager.tool_registry,
        )
        self.assertIs(
            self.application.manager.get_agent("ExecutorAgent"),
            self.application.executor_agent,
        )


if __name__ == "__main__":
    unittest.main()
