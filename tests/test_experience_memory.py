"""from memory.memory_manager import MemoryManager

memory = MemoryManager()

print("=== RECORD EXPERIENCES ===")

memory.record_experience({
    "goal": "Research AI agent planning",
    "action": "search_knowledge",
    "success": True,
    "result": "Relevant documents found"
})

memory.record_experience({
    "goal": "Research AI agent planning",
    "action": "execute_plan",
    "success": False,
    "result": "Tool unavailable"
})

memory.record_experience({
    "goal": "Build a REST API",
    "action": "work",
    "success": True,
    "result": "Endpoint created"
})


print("\n=== EXPERIENCE COUNT ===")

print(
    memory.experience.count()
)


print("\n=== SEARCH ===")

results = memory.search_experiences(
    "planning tool",
    limit=5
)

for result in results:
    print(result)"""

"""from memory.memory_manager import MemoryManager

memory = MemoryManager()

for experience in memory.get_experiences():
    print(experience)"""

from agents.planner_agent import PlannerAgent
from core.manager import Manager

manager = Manager()
planner_agent = PlannerAgent(memory_manager=manager.memory_manager)  # Pass the memory manager to the planner agent
print(
    "¿Comparten memoria?",
    planner_agent.memory_manager is manager.memory_manager
)

assert planner_agent.memory_manager is manager.memory_manager
print("Memoria compartida correctamente.")
