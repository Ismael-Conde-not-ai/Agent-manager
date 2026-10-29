
import unittest

from agents.planner_agent import PlannerAgent


class TestPlanValidation(unittest.TestCase):

    def setUp(self):
        self.planner = PlannerAgent()

        self.valid_plan = [
            {
                "step": 1,
                "action": "search_knowledge",
                "description": "Gather relevant evidence.",
            },
            {
                "step": 2,
                "action": "work",
                "description": "Prepare the final summary.",
            },
        ]

    def test_valid_plan(self):
        valid, error = self.planner.validate_plan(self.valid_plan)

        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_plan_with_too_few_steps(self):
        valid, error = self.planner.validate_plan(
            self.valid_plan[:1]
        )

        self.assertFalse(valid)
        self.assertIsNotNone(error)

    def test_plan_with_too_many_steps(self):
        plan = [
            {
                "step": index,
                "action": "work",
                "description": "Perform a task.",
            }
            for index in range(1, 7)
        ]

        valid, error = self.planner.validate_plan(plan)

        self.assertFalse(valid)
        self.assertIsNotNone(error)

    def test_unsupported_action(self):
        plan = [step.copy() for step in self.valid_plan]
        plan[0]["action"] = "delete_everything"

        valid, error = self.planner.validate_plan(plan)

        self.assertFalse(valid)
        self.assertIn("unsupported action", error)

    def test_missing_required_field(self):
        plan = [step.copy() for step in self.valid_plan]
        del plan[0]["description"]

        valid, error = self.planner.validate_plan(plan)

        self.assertFalse(valid)
        self.assertIn("missing required fields", error)

    def test_non_consecutive_step_numbers(self):
        plan = [step.copy() for step in self.valid_plan]
        plan[1]["step"] = 4

        valid, error = self.planner.validate_plan(plan)

        self.assertFalse(valid)
        self.assertIn("Step number", error)

    def test_empty_description(self):
        plan = [step.copy() for step in self.valid_plan]
        plan[0]["description"] = "   "

        valid, error = self.planner.validate_plan(plan)

        self.assertFalse(valid)
        self.assertIn("non-empty description", error)

    def test_plan_must_be_a_list(self):
        valid, error = self.planner.validate_plan(
            {"step": 1, "action": "work"}
        )

        self.assertFalse(valid)
        self.assertIn("must be a list", error)


if __name__ == "__main__":
    unittest.main(verbosity=2)
