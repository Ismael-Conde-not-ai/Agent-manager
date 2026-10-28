from memory.memory_manager import MemoryManager

memory = MemoryManager()

print("=== SAVE TASK ===")

memory.remember_persistently(
    "last_goal",
    "Build a modular AI agent"
)

memory.remember_persistently(
    "last_completed_week",
    "Week 11 Day 3"
)


print("\n=== RETRIEVE TASK ===")

goal = memory.recall_persistently(
    "last_goal"
)

print("Last goal:", goal)


print("\n=== CHECK MEMORY ===")

print(
    "Contains goal:",
    memory.persistent.contains("last_goal")
)

print(
    "Memory count:",
    memory.persistent_memory_count()
)


print("\n=== ALL PERSISTENT MEMORIES ===")

print(
    memory.get_persistent_memories()
)