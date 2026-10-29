import pytest

from memory.experience_memory import ExperienceMemory
from memory.memory_context_builder import MemoryContextBuilder
from memory.memory_manager import MemoryManager
from memory.persistent_memory import PersistentMemory


def test_memory_context_builder_integration():
    """Prueba de integración usando archivos temporales reales."""
    manager = MemoryManager()
    manager.experience = ExperienceMemory(
        path="data/test_memory_context_experiences.json"
    )
    manager.persistent = PersistentMemory(
        path="data/test_memory_context_persistent.json"
    )

    # Limpiar archivos de prueba
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

    manager.remember_persistently("preferred_language", "English")

    builder = MemoryContextBuilder(manager)
    context = builder.build("Research RAG architecture")

    assert "Relevant past experiences:" in context
    assert "search_knowledge" in context
    assert "Persistent memories:" in context
    assert "preferred_language" in context


class FakeMemoryManager:
    def search_experiences(self, query="", limit=3):
        return [
            {
                "goal": "Research AI planning",
                "action": "search_knowledge",
                "success": True,
                "result": "Found useful information",
                "lesson": "Research before writing",
            }
        ][:limit]

    def get_persistent_memories(self):
        return {
            "preference": "Use reliable sources",
            "long_memory": "Important information",
        }


def test_memory_context_builder_limits_and_edge_cases():
    """Prueba unitaria con un FakeManager para validar límites de caracteres y casos vacíos."""
    manager = FakeMemoryManager()
    builder = MemoryContextBuilder(
        manager,
        max_experiences=3,
        max_chars=250,
    )

    context = builder.build("Research AI planning")

    assert len(context) <= 250
    assert "Relevant past experiences:" in context
    assert "Persistent memories:" in context

    empty_context = builder.build("")
    assert empty_context == ""