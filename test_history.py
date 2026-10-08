from knowledge.knowledge_base import KnowledgeBase

knowledge = KnowledgeBase()

#knowledge.sync()
result = knowledge.sync()

print(
    knowledge.history.get_history("planning.txt")
)
print(result)