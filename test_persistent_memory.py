from memory.persistent_memory import PersistentMemory

memory = PersistentMemory(
    path="data/test_memory.json"
)

print("=== SAVE MEMORIES ===")

memory.remember(
    "last_goal",
    "Research AI agent planning"
)

memory.remember(
    "last_tool",
    "search_knowledge"
)

print(memory.get_all())


print("\n=== RECALL ===")

print(
    memory.recall("last_goal")
)


print("\n=== MISSING KEY ===")

print(
    memory.recall("unknown_key")
)


print("\n=== DELETE ===")

print(
    memory.forget("last_tool")
)

print(memory.get_all())

"""from memory.persistent_memory import PersistentMemory


memory = PersistentMemory(
    path="data/test_memory.json"
)

print(
    memory.recall("last_goal")
)"""