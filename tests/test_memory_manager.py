from memory.memory_manager import MemoryManager

memory = MemoryManager()

print("===ADD MEMORIES===")

memory.remember("Task started")
memory.remember("Research completed")
memory.remember("Plan created")

print("\n===WORKING MEMORY===")
print(memory.get_working_memory())

print("\n===CLEAR WORKING MEMORY===")
memory.clear_working_memory()
print(memory.get_working_memory())

memory.remember("test item")

items = memory.get_working_memory()
items.append("External item")

print(memory.get_working_memory())  # Should not include "External item"