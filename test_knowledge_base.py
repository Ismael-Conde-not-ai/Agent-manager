from knowledge.knowledge_base import KnowledgeBase

knowledge = KnowledgeBase()

results = knowledge.search("How can an agent use tools?")

print("\nRELEVANT KNOWLEDGE\n")
for index, result in enumerate(results):
    print(f"RESULT {index + 1}:")
    print(result)
    print("-"*60)

print(
    "\nDocuments in database:", 
    knowledge.vector_store.count()
)