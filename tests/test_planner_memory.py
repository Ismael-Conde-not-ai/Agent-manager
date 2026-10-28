
from core.manager import Manager
from agents.planner_agent import PlannerAgent

# 1. Crear la memoria compartida
manager = Manager()

# 2. Registrar una experiencia de prueba
manager.memory_manager.record_experience({
    "goal": "How do AI agents use planning?",
    "action": "search_knowledge",
    "success": True,
    "result": "Found information about planning and decision-making.",
    "lesson": "Research relevant information before creating a plan."
})

# 3. Crear el planificador con esa misma memoria
planner_agent = PlannerAgent(
    memory_manager=manager.memory_manager
)

# 4. Recuperar experiencias para el objetivo
goal = "How do AI agents use planning?"

context = planner_agent.memory_context_builder.build(goal)

# 5. Mostrar y validar el resultado
print("\n===== CONTEXTO RECUPERADO =====")
print(context or "No se encontraron experiencias.")
print("===============================\n")

assert "search_knowledge" in context
assert "Research relevant information" in context

print("Prueba superada: se recuperó la experiencia pertinente.")
