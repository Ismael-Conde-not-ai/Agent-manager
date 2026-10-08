from knowledge.vector_store import VectorStore

store = VectorStore()

store.add_document(
    "ai_001",
    "Ai agents can use planning tools and memory to achieve goals."
)
store.add_document(
    "rag_001",
    "Retrieval-Augmented_Generation allos AI systems to retrieve relevant information before an answer."
)
store.add_document(
    "agent_001",
    "Autonnomous agents can select tools and execute action according to their goals."
)
results = store.search(
    "How do AI agents use planning?"
)

print(results)