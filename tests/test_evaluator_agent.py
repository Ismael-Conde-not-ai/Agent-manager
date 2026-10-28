
from unittest.mock import patch

from agents.evaluator_agent import EvaluatorAgent


def test_positive_evaluation():
    agent = EvaluatorAgent()

    response = """
    {
        "success": true,
        "evaluation": "The goal was achieved."
    }
    """

    with patch("agents.evaluator_agent.geminiAI", return_value=response):
        result = agent.evaluate(
            goal="Activate the agent",
            research="Research completed",
            plan=["work"],
            execution={"success": True, "results": [
                {"success": True, "action": "work"}
            ]}
        )

    assert result["success"] is True
    assert result["evaluation"] == "The goal was achieved."


def test_negative_evaluation():
    agent = EvaluatorAgent()

    response = """
    {
        "success": false,
        "evaluation": "The goal was not achieved."
    }
    """

    with patch("agents.evaluator_agent.geminiAI", return_value=response):
        result = agent.evaluate(
            goal="Activate the agent",
            research="Research completed",
            plan=["work"],
            execution={"success": False, "results": []}
        )

    assert result["success"] is False


def test_invalid_response():
    agent = EvaluatorAgent()

    with patch(
        "agents.evaluator_agent.geminiAI",
        return_value="The goal was achieved successfully."
    ):
        result = agent.evaluate(
            goal="Activate the agent",
            research="Research completed",
            plan=["work"],
            execution={"success": True, "results": []}
        )

    assert result["success"] is False


if __name__ == "__main__":
    test_positive_evaluation()
    test_negative_evaluation()
    test_invalid_response()
    print("All evaluator tests passed!")
