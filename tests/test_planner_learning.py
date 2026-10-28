
import os
import tempfile
from unittest.mock import patch

from agents.planner_agent import PlannerAgent
from memory.experience_memory import ExperienceMemory
from memory.memory_manager import MemoryManager
from memory.persistent_memory import PersistentMemory


def test_planner_uses_failed_experience():
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Crear una memoria aislada para la prueba
        memory_manager = MemoryManager(
            persistent=PersistentMemory(
                path=os.path.join(temp_dir, "persistent.json")
            ),
            experience=ExperienceMemory(
                path=os.path.join(temp_dir, "experiences.json")
            ),
        )

        # 2. Registrar una experiencia fallida
        memory_manager.record_experience({
            "goal": (
                "Research factual information about AI planning"
            ),
            "action": "work",
            "success": False,
            "result": (
                "The answer was incomplete because research "
                "was skipped."
            ),
            "error": "Insufficient information",
            "lesson": (
                "Run search_knowledge before work when the "
                "goal requires factual information."
            ),
        })

        # 3. Crear el planificador con esa memoria
        planner = PlannerAgent(
            memory_manager=memory_manager
        )

        goal = (
            "Research factual information about AI planning "
            "and prepare a reliable summary."
        )

        # 4. Simular una respuesta que evita el error anterior
        fake_response = """
        [
            {
                "step": 1,
                "action": "search_knowledge",
                "description": "Research relevant information first"
            },
            {
                "step": 2,
                "action": "work",
                "description": "Prepare a summary using the findings"
            }
        ]
        """

        with patch(
            "agents.planner_agent.geminiAI",
            return_value=fake_response,
        ) as mock_gemini:

            plan_text = planner.create_plan(goal)

            # Comprobar el contexto enviado al modelo
            prompt = mock_gemini.call_args.args[0]

            assert "Run search_knowledge before work" in prompt
            assert "Success: False" in prompt
            assert "Insufficient information" in prompt

            # Comprobar la estructura del plan recibido
            plan = planner.parse_plan(plan_text)

            assert len(plan) >= 2
            assert plan[0]["action"] == "search_knowledge"
            assert plan[1]["action"] == "work"

            print("\n===== RESULTADO DE LA PRUEBA =====")
            print("Experiencia fallida recuperada: Sí")
            print("Lección incluida en el prompt: Sí")
            print("Plan recibido y analizado correctamente: Sí")
            print("\nPlan generado:")
            for step in plan:
                print(
                    f"Paso {step['step']}: "
                    f"{step['action']} - "
                    f"{step['description']}"
                )
            print("\nPrueba superada.")
            print("==================================\n")


if __name__ == "__main__":
    test_planner_uses_failed_experience()
