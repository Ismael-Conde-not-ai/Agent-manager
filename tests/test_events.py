from knowledge.knowledge_base import KnowledgeBase


knowledge = KnowledgeBase()

print("\n=== SYNC ===")

result = knowledge.sync()

print(result)


print("\n=== EVENTS ===")

for event in knowledge.events.get_events():

    print(event)