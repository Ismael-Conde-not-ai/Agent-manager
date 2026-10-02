from knowledge.knowledge_base import KnowledgeBase
from knowledge.document_sync import DocumentSync


knowledge = KnowledgeBase()

"""sync = DocumentSync(
    knowledge
)

result = sync.sync()

print(result)"""

results = knowledge.search(
    "How do AI agents use memory?",
    source="memory.txt"
)

print(results)