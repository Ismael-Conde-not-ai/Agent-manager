from knowledge.knowledge_base import KnowledgeBase


def main():
    knowledge = KnowledgeBase()
    print(knowledge.repair_inconsistencies())
    print(knowledge.check_consistency())


if __name__ == "__main__":
    main()
