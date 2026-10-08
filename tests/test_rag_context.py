from knowledge.knowledge_base import KnowledgeBase

knowledge = KnowledgeBase()


query = "How do AI agents use planning?"


context = knowledge.get_context(
    query,
    limit=3
)


print("\nRAG CONTEXT\n")
print(context)