
import os
import tempfile

from memory.experience_memory import ExperienceMemory
from memory.memory_context_builder import MemoryContextBuilder
from memory.memory_manager import MemoryManager
from memory.persistent_memory import PersistentMemory

GOAL = "Prepare a factual summary explaining how AI agents use planning."

LESSON = (
    "For factual summaries, use search_knowledge before work. "
    "Base the summary on retrieved evidence and avoid unsupported claims."
)


def create_memory_manager(temp_dir):
    """Create a manager using persistent files in a temporary directory."""
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

        # 1. Simulate the original system recording an experience.
        print("\n========== FASE 1: GUARDAR ==========")

        manager_before = create_memory_manager(temp_dir)

        manager_before.record_experience({
            "goal": GOAL,
            "action": "work",
            "success": False,
            "result": "The summary contained unsupported claims.",
            "error": "Research was skipped before writing.",
            "lesson": LESSON,
        })

        manager_before.remember_persistently(
            "factual_summary_rule",
            LESSON,
        )

        print("Experiencia registrada: Sí")
        print("Lección guardada: Sí")

        # 2. Simulate a restart by creating a new manager.
        print("\n========== FASE 2: REINICIAR ==========")

        del manager_before

        manager_after = create_memory_manager(temp_dir)

        print("Nuevo MemoryManager creado: Sí")
        print(
            "Experiencias cargadas:",
            len(manager_after.get_experiences()),
        )
        print(
            "Memorias persistentes cargadas:",
            manager_after.persistent_memory_count(),
        )

        # 3. Verify that the experience and lesson survived.
        print("\n========== FASE 3: RECUPERAR ==========")

        experiences = manager_after.search_experiences(
            query=GOAL,
            limit=5,
        )

        recovered_experience = next(
            (
                experience
                for experience in experiences
                if experience.get("lesson") == LESSON
            ),
            None,
        )

        recovered_persistent = manager_after.recall_persistently(
            "factual_summary_rule"
        )

        assert recovered_experience is not None, (
            "No se recuperó la experiencia después del reinicio."
        )

        assert recovered_persistent == LESSON, (
            "No se recuperó la memoria persistente después del reinicio."
        )

        print("Experiencia recuperada: Sí")
        print("Lección de la experiencia recuperada: Sí")
        print("Memoria persistente recuperada: Sí")

        # 4. Verify that the planner can receive the recovered context.
        print("\n========== FASE 4: CONTEXTO ==========")

        context_builder = MemoryContextBuilder(manager_after)
        context = context_builder.build(GOAL)

        assert LESSON in context, (
            "El contexto no contiene la lección recuperada."
        )

        print("Contexto reconstruido: Sí")
        print("Lección disponible para el planificador: Sí")

        print("\nRESULTADO: TODAS LAS PRUEBAS SUPERADAS.")


if __name__ == "__main__":
    main()
