from knowledge.knowledge_base import KnowledgeBase

knowledge = KnowledgeBase()



success = knowledge.update_document("planning.txt")

print(success)  