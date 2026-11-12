from knowledge.knowledge_base import KnowledgeBase


def main():
    knowledge = KnowledgeBase()
    result = knowledge.sync()
    print(knowledge.history.get_history("planning.txt"))
    print(result)


if __name__ == "__main__":
    main()
