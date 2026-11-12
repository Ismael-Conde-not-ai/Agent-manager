from knowledge.knowledge_base import KnowledgeBase


def main():
    knowledge = KnowledgeBase()
    print("\n=== SYNC ===")
    print(knowledge.sync())
    print("\n=== EVENTS ===")
    for event in knowledge.events.get_events():
        print(event)


if __name__ == "__main__":
    main()
