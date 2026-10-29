
from unittest.mock import patch

from agents.planner_agent import PlannerAgent


def main():
    planner = PlannerAgent()

    previous_plan = [
        {
            "step": 1,
            "action": "search_knowledge",
            "description": "Find factual evidence."
        },
        {
            "step": 2,
            "action": "work",
            "description": "Write a summary."
        }
    ]

    execution_results = [
        {
            "success": False,
            "action": "search_knowledge",
            "error": "Knowledge source unavailable."
        }
    ]

    revised_plan = """
    [
        {
            "step": 1,
            "action": "search_knowledge",
            "description": "Retry research using an available source."
        },
        {
            "step": 2,
            "action": "work",
            "description": "Write a summary based on verified evidence."
        }
    ]
    """

    with patch(
        "agents.planner_agent.geminiAI",
        return_value=revised_plan
    ) as mock_gemini:
        response = planner.replan(
            goal="Prepare a factual summary about AI planning.",
            previous_plan=previous_plan,
            execution_results=execution_results
        )

    parsed_plan = planner.parse_plan(response)

    assert mock_gemini.called
    assert len(parsed_plan) == 2
    assert parsed_plan[0]["action"] == "search_knowledge"

    prompt = mock_gemini.call_args.args[0]

    assert "Knowledge source unavailable." in prompt
    assert "Previous plan" in prompt
    assert "Relevant memory" in prompt

    print("Replanning test passed.")
    print("Execution failure included in prompt: Yes")
    print("Previous plan included in prompt: Yes")
    print("Revised plan parsed correctly: Yes")


if __name__ == "__main__":
    main()
