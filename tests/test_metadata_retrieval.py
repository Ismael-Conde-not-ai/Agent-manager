from knowledge.knowledge_base import KnowledgeBase

knowledge = KnowledgeBase()


print("\n" + "=" * 70)
print("SOURCE FILTER")
print("=" * 70)

results = knowledge.search(
    "How do AI agents use planning?",
    limit=5,
    #source="planning.txt",
    #max_distance=1.0
)

for result in results:

    print("\nID:", result["id"])
    print("Source:", result["metadata"].get("source"))
    print("Category:", result["metadata"].get("category"))
    print("Distance:", result["distance"])
    print("Text:", result["text"])


print("\n" + "=" * 70)
print("CATEGORY FILTER")
print("=" * 70)

results = knowledge.search(
    "How do AI agents use tools?",
    limit=5,
    #category="tool",
    #max_distance=1.0
)

for result in results:

    print("\nID:", result["id"])
    print("Source:", result["metadata"].get("source"))
    print("Category:", result["metadata"].get("category"))
    print("Distance:", result["distance"])
    print("Text:", result["text"])