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

from memory.memory_manager import MemoryManager

memory = MemoryManager()

for experience in memory.get_experiences():
    print(experience)