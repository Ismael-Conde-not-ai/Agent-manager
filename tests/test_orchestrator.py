
import unittest
from unittest.mock import Mock

from core.orchestrator import Orchestrator


class TestOrchestrator(unittest.TestCase):

    def setUp(self):
        self.manager = Mock()

        self.research = Mock()
        self.planner = Mock()
        self.executor = Mock()
        self.evaluator = Mock()

        self.manager.get_agent.side_effect = {
            "ResearchAgent": self.research,
            "PlannerAgent": self.planner,
            "ExecutorAgent": self.executor,
            "EvaluatorAgent": self.evaluator,
        }.get

        self.orchestrator = Orchestrator(self.manager)

        self.goal = "Prepare a factual summary about AI planning."

        self.plan = [
            {
                "step": 1,
                "action": "search_knowledge",
                "description": "Gather evidence.",
            },
            {
                "step": 2,
                "action": "work",
                "description": "Write the summary.",
            },
        ]

        self.research.research.return_value = "Research evidence."

        self.planner.create_plan.return_value = "initial plan"
        self.planner.replan.return_value = "revised plan"
        self.planner.parse_plan.side_effect = lambda text: (
            self.plan if text in ("initial plan", "revised plan") else []
        )
        self.planner.validate_plan.return_value = (True, None)

        self.executor.execute_plan.return_value = {
            "success": True,
            "results": [
                {
                    "success": True,
                    "action": "search_knowledge",
                    "result": "Evidence found.",
                }
            ],
        }

        self.evaluator.evaluate.return_value = {
            "success": True,
            "evaluation": "The goal was achieved.",
        }

    def test_missing_agent(self):
        self.manager.get_agent.side_effect = lambda name: (
            None if name == "PlannerAgent"
            else {
                "ResearchAgent": self.research,
                "ExecutorAgent": self.executor,
                "EvaluatorAgent": self.evaluator,
            }.get(name)
        )

        with self.assertRaises(ValueError):
            self.orchestrator.run(self.goal, Mock())

    def test_invalid_max_retries(self):
        for invalid_value in (-1, 1.5, True, "2"):
            with self.subTest(value=invalid_value):
                with self.assertRaises(ValueError):
                    self.orchestrator.run(
                        self.goal,
                        Mock(),
                        max_retries=invalid_value,
                    )

    def test_success_first_attempt(self):
        result = self.orchestrator.run(self.goal, Mock())

        self.assertTrue(result["success"])
        self.assertEqual(result["total_attempts"], 1)
        self.planner.create_plan.assert_called_once()
        self.planner.replan.assert_not_called()

    def test_replan_after_failure(self):
        self.executor.execute_plan.side_effect = [
            {
                "success": False,
                "results": [
                    {
                        "success": False,
                        "action": "search_knowledge",
                        "error": "Source unavailable.",
                    }
                ],
            },
            {
                "success": True,
                "results": [
                    {
                        "success": True,
                        "action": "search_knowledge",
                        "result": "Evidence found.",
                    }
                ],
            },
        ]

        self.evaluator.evaluate.side_effect = [
            {
                "success": False,
                "evaluation": "Evidence is missing.",
            },
            {
                "success": True,
                "evaluation": "The goal was achieved.",
            },
        ]

        result = self.orchestrator.run(
            self.goal,
            Mock(),
            max_retries=1,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["total_attempts"], 2)
        self.planner.create_plan.assert_called_once()
        self.planner.replan.assert_called_once()

        replan_kwargs = self.planner.replan.call_args.kwargs

        self.assertEqual(replan_kwargs["goal"], self.goal)
        self.assertEqual(replan_kwargs["previous_plan"], self.plan)
        self.assertIn(
            "Source unavailable.",
            str(replan_kwargs["execution_results"]),
        )

    def test_stops_after_max_retries(self):
        self.executor.execute_plan.return_value = {
            "success": False,
            "results": [
                {
                    "success": False,
                    "action": "search_knowledge",
                    "error": "Source unavailable.",
                }
            ],
        }

        self.evaluator.evaluate.return_value = {
            "success": False,
            "evaluation": "Evidence is insufficient.",
        }

        result = self.orchestrator.run(
            self.goal,
            Mock(),
            max_retries=2,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["total_attempts"], 3)
        self.planner.create_plan.assert_called_once()
        self.assertEqual(self.planner.replan.call_count, 2)

    def test_evaluation_failure_triggers_replan(self):
        self.evaluator.evaluate.side_effect = [
            {
                "success": False,
                "evaluation": "The summary lacks evidence.",
            },
            {
                "success": True,
                "evaluation": "The revised summary is supported.",
            },
        ]

        result = self.orchestrator.run(
            self.goal,
            Mock(),
            max_retries=1,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["total_attempts"], 2)
        self.planner.replan.assert_called_once()

        feedback = self.planner.replan.call_args.kwargs[
            "execution_results"
        ]

        self.assertIn("evaluation", feedback)
        self.assertIn("execution", feedback)

    
    def test_invalid_plan_is_never_executed(self):
        self.planner.parse_plan.return_value = [
            {
                "step": 1,
                "action": "delete_everything",
                "description": "Unsupported action.",
            },
            {
                "step": 2,
                "action": "work",
                "description": "Continue the task.",
            },
        ]

        self.planner.validate_plan.return_value = (
            False,
            "Step 1 contains an unsupported action.",
        )

        result = self.orchestrator.run(
            self.goal,
            Mock(),
            max_retries=0,
        )

        self.executor.execute_plan.assert_not_called()
        self.assertFalse(result["success"])

    def test_invalid_plan_is_never_executed(self):
        self.planner.parse_plan.return_value = [
            {
                "step": 1,
                "action": "delete_everything",
                "description": "Unsupported action.",
            },
            {
                "step": 2,
                "action": "work",
                "description": "Continue the task.",
            },
        ]

        self.planner.validate_plan.return_value = (
            False,
            "Step 1 contains an unsupported action.",
        )

        result = self.orchestrator.run(
            self.goal,
            Mock(),
            max_retries=0,
        )

        self.executor.execute_plan.assert_not_called()
        self.assertFalse(result["success"])
        self.assertIn("unsupported action", result["error"].lower())

    
    def test_invalid_plan_feedback_is_sent_to_replanner(self):
        self.planner.parse_plan.side_effect = [
            [
                {
                    "step": 1,
                    "action": "delete_everything",
                    "description": "Invalid action.",
                },
                {
                    "step": 2,
                    "action": "work",
                    "description": "Continue.",
                },
            ],
            self.plan,
        ]

        self.planner.validate_plan.side_effect = [
            (False, "Unsupported action."),
            (True, None),
        ]

        self.executor.execute_plan.return_value = {"success": True}
        self.evaluator.evaluate.return_value = {"success": True}

        result = self.orchestrator.run(
            self.goal,
            Mock(),
            max_retries=1,
        )

        self.executor.execute_plan.assert_called_once()

        self.planner.replan.assert_called_once()
        feedback = self.planner.replan.call_args.kwargs["execution_results"]

        self.assertEqual(
            feedback["validation_error"],
            "Unsupported action.",
        )
        self.assertTrue(result["success"])




if __name__ == "__main__":
    unittest.main(verbosity=2)
