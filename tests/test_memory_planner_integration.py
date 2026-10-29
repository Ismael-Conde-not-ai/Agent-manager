
import os
import tempfile
from unittest.mock import patch

from agents.planner_agent import PlannerAgent
from memory.experience_memory import ExperienceMemory
from memory.memory_manager import MemoryManager
from memory.persistent_memory import PersistentMemory

GOAL = (
    "Prepare a factual summary explaining "
    "how AI agents use planning."
)

LESSON = (
    "For factual summaries, use search_knowledge "
    "before work. Base the summary on retrieved "
    "evidence and avoid unsupported claims."
)


def create_memory_manager(temp_dir):
    """Create a manager with isolated persistent storage."""
    return MemoryManager(
        persistent=PersistentMemory(
            path=os.path.join(temp_dir, "persistent.json")
        ),
        experience=ExperienceMemory(
            path=os.path.join(temp_dir, "experiences.json")
        ),
    )


def main():
    with tempfile.TemporaryDirectory() as temp_dir:

        # 1. Save an experience in the original manager.
        print("\n========== FASE 1: GUARDAR EXPERIENCIA ==========")

        manager_before = create_memory_manager(temp_dir)

        manager_before.record_experience({
            "goal": GOAL,
            "action": "work",
            "success": False,
            "result": "The summary contained unsupported claims.",
            "error": "Research was skipped before writing.",
            "lesson": LESSON,
        })

        print("Experiencia fallida registrada: Sí")

        # 2. Simulate a restart by creating a new manager.
        print("\n========== FASE 2: RECONSTRUIR MEMORIA ==========")

        del manager_before

        manager_after = create_memory_manager(temp_dir)

        experiences = manager_after.search_experiences(
            query=GOAL,
            limit=5,
        )

        assert any(
            experience.get("lesson") == LESSON
            for experience in experiences
        ), "La experiencia no se recuperó después del reinicio."

        print("Experiencia recuperada del archivo: Sí")

        # 3. Inject the recovered manager into the planner.
        print("\n========== FASE 3: INTEGRAR PLANIFICADOR ==========")

        planner = PlannerAgent(
            memory_manager=manager_after
        )

        assert planner.memory_manager is manager_after, (
            "PlannerAgent no utiliza el gestor reconstruido."
        )

        context = planner.memory_context_builder.build(GOAL)

        assert LESSON in context, (
            "La lección no aparece en el contexto del planificador."
        )

        print("Gestor reconstruido inyectado: Sí")
        print("Lección incluida en el contexto: Sí")

        # 4. Simulate Gemini and inspect the actual prompt.
        print("\n========== FASE 4: VERIFICAR PROMPT ==========")

        fake_response = """
[
    {
        "step": 1,
        "action": "search_knowledge",
        "description": "Research the topic and gather factual evidence."
    },
    {
        "step": 2,
        "action": "work",
        "description": "Write a factual summary based on retrieved evidence."
    }
]
"""

        with patch(
            "agents.planner_agent.geminiAI",
            return_value=fake_response,
        ) as mocked_gemini:

            raw_plan = planner.create_plan(GOAL)

        # Inspect the arguments sent to the mocked model.
        prompt_parts = []

        for value in mocked_gemini.call_args.args:
            prompt_parts.append(str(value))

        for value in mocked_gemini.call_args.kwargs.values():
            prompt_parts.append(str(value))

        prompt = "\n".join(prompt_parts)

        assert LESSON in prompt, (
            "La lección recuperada no llegó al prompt de Gemini."
        )

        plan = planner.parse_plan(raw_plan)

        assert plan, "El plan recibido no pudo analizarse."
        assert plan[0].get("action") == "search_knowledge", (
            "El plan de prueba no comienza investigando."
        )

        print("Gemini fue invocado: Sí")
        print("Lección presente en el prompt: Sí")
        print("Plan recibido y analizado: Sí")
        print("Primera acción: search_knowledge")

        print("\nRESULTADO: INTEGRACIÓN SUPERADA.")


if __name__ == "__main__":
    main()
