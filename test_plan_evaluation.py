
from test_planner_real_gemini import evaluate_plan


def main():
    sample_plan = [
        {
            "step": 1,
            "action": "search_knowledge",
            "description": (
                "Research the topic using reliable sources."
            ),
        },
        {
            "step": 2,
            "action": "work",
            "description": (
                "Write a summary based on retrieved evidence."
            ),
        },
        {
            "step": 3,
            "action": "work",
            "description": (
                "Verify each claim and remove unsupported claims."
            ),
        },
    ]

    result = evaluate_plan(sample_plan)

    assert result["research_before_work"] is True
    assert result["mentions_evidence"] is True
    assert result["verifies_claims"] is True

    print("Todas las pruebas del evaluador fueron superadas.")


if __name__ == "__main__":
    main()
