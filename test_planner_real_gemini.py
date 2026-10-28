
import os
import tempfile

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


def create_isolated_manager(temp_dir):
    """Create memory stores isolated from real project data."""
    return MemoryManager(
        persistent=PersistentMemory(
            path=os.path.join(temp_dir, "persistent.json")
        ),
        experience=ExperienceMemory(
            path=os.path.join(temp_dir, "experiences.json")
        ),
    )




def evaluate_plan(plan):
    """Evaluate observable properties of a parsed plan."""
    actions = [
        str(step.get("action", "")).strip().lower()
        for step in plan
    ]

    descriptions = [
        str(step.get("description", "")).lower()
        for step in plan
    ]

    text = " ".join(descriptions)

    research_indices = [
        index
        for index, action in enumerate(actions)
        if action == "search_knowledge"
    ]

    work_indices = [
        index
        for index, action in enumerate(actions)
        if action == "work"
    ]

    # Criterion 1: research must occur before work.
    research_before_work = (
        bool(research_indices)
        and bool(work_indices)
        and min(research_indices) < min(work_indices)
    )

    # Criterion 2: the plan explicitly mentions evidence.
    evidence_phrases = (
        "evidence",
        "source",
        "reliable information",
        "retrieved information",
        "retrieved data",
        "research findings",
        "factual evidence",
        "supported by the data",
        "supported by evidence",
        "supported by the retrieved data",
        "grounded in evidence",
        "claims are supported",
        "based on the data",
        "based on factual evidence",
    )

    mentions_evidence = any(
        phrase in text for phrase in evidence_phrases
    )

    # Criterion 3: the plan explicitly includes factual verification.
    verification_phrases = (
        "verify the claims",
        "verify each claim",
        "verify all claims",
        "check each claim",
        "check all claims",
        "validate the claims",
        "validate each claim",
        "cross-check",
        "fact-check",
        "confirm each claim",
        "confirm all claims",
        "identify unsupported claims",
        "detect unsupported claims",
        "remove unsupported claims",
        "flag unsupported claims",
        "avoid unsupported claims",
        "ensure every claim is supported",
        "ensure all claims are supported",
        "check for unsupported claims",
    )

    verifies_claims = any(
        phrase in text
        for phrase in verification_phrases
    )

    return {
        "actions": actions,
        "research_before_work": research_before_work,
        "mentions_evidence": mentions_evidence,
        "verifies_claims": verifies_claims,
    }



def print_evaluation(label, evaluation):
    print(f"\n--- Evaluación: {label} ---")
    print("Acciones:", evaluation["actions"])

    print(
        "Investiga antes de trabajar:",
        evaluation["research_before_work"],
    )

    print(
        "Menciona evidencia o fuentes:",
        evaluation["mentions_evidence"],
    )

    print(
        "Incluye verificación factual explícita:",
        evaluation["verifies_claims"],
    )



def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = create_isolated_manager(temp_dir)

        planner = PlannerAgent(
            memory_manager=memory_manager
        )

        # A. Confirmar que no existen experiencias previas.
        context_a = planner.memory_context_builder.build(GOAL)

        assert context_a == "", (
            "El escenario A debía comenzar sin contexto de memoria."
        )

        print("\n========== ESCENARIO A ==========")
        print("Memoria previa disponible: No")
        print("Generando plan sin experiencia previa...")

        raw_plan_a = planner.create_plan(GOAL)
        plan_a = planner.parse_plan(raw_plan_a)

        print("\nPlan A:")
        print(raw_plan_a)

        if not plan_a:
            raise RuntimeError(
                "Gemini no devolvió un plan válido para el escenario A."
            )

        evaluation_a = evaluate_plan(plan_a)
        print_evaluation("A: sin memoria", evaluation_a)

        # B. Registrar la experiencia después del escenario A.
        recorded = memory_manager.record_experience({
            "goal": GOAL,
            "action": "work",
            "success": False,
            "result": (
                "The summary contained unsupported claims."
            ),
            "error": (
                "Research was skipped before writing."
            ),
            "lesson": LESSON,
        })

        # Confirmar que la experiencia llegó al contexto.
        context_b = planner.memory_context_builder.build(GOAL)

        assert context_b, (
            "El escenario B debía recuperar una experiencia."
        )
        assert LESSON in context_b, (
            "La lección no aparece en el contexto recuperado."
        )

        print("\n========== ESCENARIO B ==========")
        print("Memoria previa disponible: Sí")
        print("Experiencia registrada:", recorded["id"])
        print("Lección recuperada correctamente: Sí")
        print("Generando plan con experiencia previa...")

        raw_plan_b = planner.create_plan(GOAL)
        plan_b = planner.parse_plan(raw_plan_b)

        print("\nPlan B:")
        print(raw_plan_b)

        if not plan_b:
            raise RuntimeError(
                "Gemini no devolvió un plan válido para el escenario B."
            )

        evaluation_b = evaluate_plan(plan_b)
        print_evaluation("B: con memoria", evaluation_b)

        # Comparar resultados.
        print("\n========== COMPARACIÓN FINAL ==========")

        print(
            "¿Cambió la secuencia de acciones?",
            evaluation_a["actions"] != evaluation_b["actions"],
        )

        criteria = (
            "research_before_work",
            "mentions_evidence",
            "verifies_claims",
        )

        improvements = [
            criterion
            for criterion in criteria
            if (
                not evaluation_a[criterion]
                and evaluation_b[criterion]
            )
        ]

        regressions = [
            criterion
            for criterion in criteria
            if (
                evaluation_a[criterion]
                and not evaluation_b[criterion]
            )
        ]

        print(
            "Criterios que mejoraron:",
            improvements or "Ninguno observado",
        )
        print(
            "Criterios que empeoraron:",
            regressions or "Ninguno observado",
        )

        if improvements and not regressions:
            print(
                "\nResultado: hay indicios de mejora "
                "en los criterios evaluados."
            )
        elif regressions:
            print(
                "\nResultado: el plan con memoria perdió "
                "al menos una propiedad evaluada."
            )
        else:
            print(
                "\nResultado: no se observó una mejora "
                "clara en esta ejecución."
            )

        print(
            "\nNota: los criterios se evalúan mediante reglas "
            "de palabras y orden de acciones. No constituyen "
            "una evaluación semántica completa."
        )


if __name__ == "__main__":
    main()
