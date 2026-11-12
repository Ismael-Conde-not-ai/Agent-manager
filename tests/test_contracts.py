import unittest

from pydantic import ValidationError

from core.contracts import (
    ErrorCategory,
    ErrorInfo,
    EvaluationResult,
    Plan,
    PlanStep,
    ToolResult,
)


class TestContracts(unittest.TestCase):

    def valid_steps(self):
        return [
            {
                "step": 1,
                "action": "search_knowledge",
                "description": "Gather evidence.",
                "arguments": {},
            },
            {
                "step": 2,
                "action": "work",
                "description": "Prepare the result.",
                "arguments": {"format": "summary"},
            },
        ]

    def test_valid_plan(self):
        plan = Plan(steps=self.valid_steps())
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0]["action"], "search_knowledge")

    def test_empty_plan_is_invalid(self):
        with self.assertRaises(ValidationError):
            Plan(steps=[])

    def test_invalid_order_and_duplicate_steps(self):
        steps = self.valid_steps()
        steps[1]["step"] = 1
        with self.assertRaises(ValidationError):
            Plan(steps=steps)

    def test_empty_action_and_arguments(self):
        steps = self.valid_steps()
        steps[0]["action"] = " "
        with self.assertRaises(ValidationError):
            Plan(steps=steps)

        steps = self.valid_steps()
        steps[0]["arguments"] = []
        with self.assertRaises(ValidationError):
            Plan(steps=steps)

    def test_unknown_fields_are_rejected(self):
        steps = self.valid_steps()
        steps[0]["unexpected"] = True
        with self.assertRaises(ValidationError):
            Plan(steps=steps)

    def test_structured_tool_error(self):
        result = ToolResult(
            success=False,
            action="external_search",
            source="mcp",
            error=ErrorInfo(
                code="mcp_tool_error",
                message="Server returned an error",
                category=ErrorCategory.TOOL,
            ),
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.category, ErrorCategory.TOOL)

    def test_evaluation_has_explicit_fields(self):
        result = EvaluationResult(
            success=True,
            evaluation="Evidence supports the result.",
            evidence=["Source A"],
        )
        self.assertTrue(result.success)
        self.assertEqual(result.evidence, ["Source A"])


if __name__ == "__main__":
    unittest.main()
