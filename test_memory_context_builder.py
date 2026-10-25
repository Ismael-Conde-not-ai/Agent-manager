
from memory.experience_memory import ExperienceMemory
from memory.memory_context_builder import MemoryContextBuilder
from memory.memory_manager import MemoryManager
from memory.persistent_memory import PersistentMemory

# Use separate files so the test does not modify real agent data.
manager = MemoryManager()
manager.experience = ExperienceMemory(
    path="data/test_memory_context_experiences.json"
)
manager.persistent = PersistentMemory(
    path="data/test_memory_context_persistent.json"
)

# Clear only these dedicated test files.
manager.experience.experiences = []
manager.experience.save()

manager.persistent.memories = {}
manager.persistent.save()

manager.record_experience({
    "goal": "Research RAG architecture",
    "action": "search_knowledge",
    "success": True,
    "result": "Found relevant documents",
    "lesson": "Search the knowledge base before answering"
})

manager.record_experience({
    "goal": "Research RAG architecture",
    "action": "search_knowledge",
    "success": False,
    "result": "No relevant documents found",
    "lesson": "Try a broader search query"
})

manager.remember_persistently(
    "preferred_language",
    "English"
)

builder = MemoryContextBuilder(manager)

context = builder.build("Research RAG architecture")

assert "Relevant past experiences:" in context
assert "search_knowledge" in context
assert "Persistent memories:" in context
assert "preferred_language" in context

print(context)
print("\nAll memory context tests passed!")
