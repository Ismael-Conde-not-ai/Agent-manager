
from unittest.mock import patch

from core.manager import Manager
from agents.planner_agent import PlannerAgent


manager = Manager()

manager.memory_manager.record_experience({
    "goal": "How do AI agents use planning?",
    "action": "search_knowledge",
    "success": True,
    "result": "Found information about planning.",
    "lesson": "Research before creating a plan."
})

planner = PlannerAgent(
    memory_manager=manager.memory_manager
)

fake_response = """
[
    {
        "step": 1,
        "action": "search_knowledge",
        "description": "Research AI planning"
    },
    {
        "step": 2,
        "action": "work",
        "description": "Apply the findings"
    }
]
"""

with patch(
    "agents.planner_agent.geminiAI",
    return_value=fake_response
) as mock_gemini:

    result = planner.create_plan(
        "How do AI agents use planning?"
    )

    prompt_sent = mock_gemini.call_args.args[0]

    print("\n===== VALIDACIÓN DEL PROMPT =====")
    print("¿Incluye la acción?", "search_knowledge" in prompt_sent)
    print("¿Incluye la lección?", "Research before creating a plan." in prompt_sent)
    print("¿Incluye el objetivo?", "How do AI agents use planning?" in prompt_sent)
    print("=================================\n")

    assert "search_knowledge" in prompt_sent
    assert "Research before creating a plan." in prompt_sent
    assert "How do AI agents use planning?" in prompt_sent

    print("Prueba superada: el prompt contiene las experiencias recuperadas.")
