from knowledge.knowledge_base import KnowledgeBase

knowledge = KnowledgeBase()
"""
print("\n=== SYNC ===")

sync_result = knowledge.sync()

print(sync_result)


print("\n=== CONSISTENCY ===")

problems = knowledge.check_consistency()

print(problems)


print("\n=== REGISTRY ===")

print(
    knowledge.registry.documents
)


print("\n=== HISTORY ===")

for source in knowledge.history.history:

    print(
        source,
        knowledge.history.get_history(
            source
        )
    )
"""
"""
knowledge.vector_store.delete_by_source(
    "planning.txt"
)

print(
    knowledge.check_consistency()
)
"""
"""
print(
    knowledge.repair_inconsistencies()
)
"""
"""print(
    knowledge.check_consistency()
)"""

results = knowledge.search("How does AI agents planning work?", limit=3)

print(results)