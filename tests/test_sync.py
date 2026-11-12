from knowledge.knowledge_base import KnowledgeBase


def main():
    results = KnowledgeBase().search(
        "How do AI agents use memory?",
        source="memory.txt",
    )
    print(results)


if __name__ == "__main__":
    main()
