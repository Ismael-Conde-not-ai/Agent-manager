

from knowledge.knowledge_base import KnowledgeBase

knowledge = KnowledgeBase()

result = (
    knowledge.repair_inconsistencies()
)

print(result)

print(
    knowledge.check_consistency()
)