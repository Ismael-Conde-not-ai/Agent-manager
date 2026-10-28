
from memory.memory_context_builder import MemoryContextBuilder


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
            "long_memory": "Important information " * 100,
        }


def main():
    manager = FakeMemoryManager()

    builder = MemoryContextBuilder(
        manager,
        max_experiences=3,
        max_chars=250,
    )

    context = builder.build("Research AI planning")

    print(context)
    print("\nCaracteres:", len(context))

    assert len(context) <= 250
    assert "Relevant past experiences:" in context
    assert "Persistent memories:" in context

    empty_context = builder.build("")
    assert empty_context == ""

    print("\nTodas las pruebas del contexto fueron superadas.")


if __name__ == "__main__":
    main()
