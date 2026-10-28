from memory.memory_manager import MemoryManager

memory = MemoryManager()

print(
    memory.recall_persistently("last_goal")
)

print(
    memory.recall_persistently("last_completed_week")
)