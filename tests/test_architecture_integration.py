import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient

from agents.agent import AIagent
from core.composition import create_application
from core.contracts import EvaluationResult, Plan, PlanStep


class TestComposedWorkflowIntegration(unittest.IsolatedAsyncioTestCase):

    def test_composed_dependencies_are_singletons(self):
        application = create_application()

        self.assertIs(
            application.manager.tool_registry,
            application.tool_registry,
        )
        self.assertIs(
            application.manager.tool_execution_service,
            application.executor_agent.tool_execution_service,
        )
        self.assertIs(
            application.manager.memory_manager,
            application.planner_agent.memory_manager,
        )
        self.assertIs(
            application.orchestrator.agents["ResearchAgent"],
            application.research_agent,
        )

    async def test_real_internal_workflow_with_external_models_stubbed(self):
        application = create_application()
        legacy_agent = AIagent(
            name="integration-agent",
            goal="Complete integration work",
            initial_energy=100,
            initial_status="ready",
            knowledge_base=application.knowledge_base,
            memory_manager=application.memory_manager,
            tool_registry=application.tool_registry,
            tool_execution_service=application.tool_execution_service,
            planner_agent=application.planner_agent,
            executor_agent=application.executor_agent,
            orchestrator=application.orchestrator,
        )
        application.memory_manager.record_experience = Mock()
        plan = Plan(
            steps=[
                PlanStep(
                    step=1,
                    action="work",
                    description="Perform the integration work.",
                ),
                PlanStep(
                    step=2,
                    action="rest",
                    description="Finish the integration work.",
                ),
            ]
        )

        application.research_agent.research = Mock(
            return_value="evidence"
        )
        application.planner_agent.create_plan = Mock(
            return_value=plan
        )
        application.planner_agent.parse_plan = Mock(
            return_value=plan
        )
        application.evaluator_agent.evaluate = Mock(
            return_value=EvaluationResult(
                success=True,
                evaluation="The step completed.",
            )
        )

        result = await application.orchestrator.run(
            "Complete integration work",
            legacy_agent,
            max_retries=0,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.research.text, "evidence")
        self.assertEqual(result.final_plan.steps[0].action, "work")
        self.assertTrue(result.final_execution.results[0].result.success)
        self.assertTrue(result.final_evaluation.success)
        self.assertEqual(legacy_agent.status, "resting")
        self.assertEqual(legacy_agent.energy, 80)


class TestApiSurfaceIntegration(unittest.TestCase):

    def setUp(self):
        import api.server as server

        self.server = server
        self.original_agent = server.agent
        self.agent = Mock()
        self.agent.name = "api-agent"
        self.agent.goal = "api goal"
        self.agent.energy = 100
        self.agent.status = "ready"
        self.agent.short_term_memory = []
        self.agent.long_term_memory = []
        self.agent.plan = None
        self.agent.knowledge.search.return_value = []
        server.agent = self.agent
        self.connect = patch.object(
            server.manager.mcp_manager,
            "connect_configured_servers",
            new_callable=AsyncMock,
        )
        self.close = patch.object(
            server.manager.mcp_manager,
            "close_all",
            new_callable=AsyncMock,
        )
        self.connect.start()
        self.close.start()
        self.client = TestClient(server.app)

    def tearDown(self):
        self.client.close()
        self.connect.stop()
        self.close.stop()
        self.server.agent = self.original_agent

    def test_core_endpoint_shapes_and_missing_agent_statuses(self):
        self.server.agent = None
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/status").status_code, 200)
        self.assertEqual(self.client.get("/system/health").status_code, 200)
        self.assertEqual(self.client.get("/agent/status").status_code, 404)
        self.assertEqual(self.client.post("/agent/step").status_code, 404)
        self.assertEqual(
            self.client.post(
                "/workflow/full",
                params={"goal": "g"},
            ).status_code,
            409,
        )
        self.assertEqual(self.client.get("/knowledge/search", params={
            "query": "q",
        }).status_code, 409)

    def test_shared_service_endpoints_remain_available(self):
        with patch.object(
            self.server.research_agent,
            "research",
            return_value="result",
        ), patch.object(
            self.server.planner_agent,
            "create_plan",
            return_value=Plan(
                steps=[
                    PlanStep(
                        step=1,
                        action="work",
                        description="Work",
                    ),
                ]
            ),
        ) as create_plan:
            research = self.client.post(
                "/research",
                params={"query": "q"},
            )
            plan = self.client.post(
                "/plan",
                params={"goal": "g"},
            )

        self.assertEqual(research.status_code, 200)
        self.assertEqual(research.json()["result"], "result")
        self.assertEqual(plan.status_code, 200)
        self.assertEqual(plan.json()["plan"][0]["action"], "work")
        create_plan.assert_called_once()
        self.assertEqual(
            self.client.get("/mcp/servers").status_code,
            200,
        )
        self.assertEqual(
            self.client.get("/mcp/tools").status_code,
            200,
        )

    def test_historical_and_system_endpoints(self):
        self.assertEqual(self.client.get("/system/health").status_code, 200)
        self.assertEqual(self.client.get("/system/metrics").status_code, 200)
        self.assertEqual(self.client.get("/system/logs").status_code, 200)
        self.assertEqual(self.client.get("/agent/status").status_code, 200)

        self.agent.autonomous_step = AsyncMock()
        step = self.client.post("/agent/step")
        self.assertEqual(step.status_code, 200)
        self.agent.autonomous_step.assert_awaited_once()

        with patch.object(
            self.server.manager.tool_registry,
            "get_tool",
            return_value=None,
        ):
            unknown_tool = self.client.post(
                "/mcp/tools/unknown",
                json={},
            )
        self.assertEqual(unknown_tool.status_code, 404)

        local_tool = self.client.post(
            "/mcp/tools/work",
            json={},
        )
        self.assertEqual(local_tool.status_code, 400)


if __name__ == "__main__":
    unittest.main()
