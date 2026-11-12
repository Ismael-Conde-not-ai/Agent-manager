from knowledge.knowledge_base import KnowledgeBase
from tests.output import configure_utf8_output


def main():
    configure_utf8_output()
    knowledge = KnowledgeBase()
    queries = [
        "How do AI agents use planning?",
        "How does Retrieval-Augmented Generation work?",
        "What is quantum teleportation?",
    ]
    for query in queries:
        print("\n" + "=" * 70)
        print("QUERY:")
        print(query)
        print("=" * 70)
        results = knowledge.search(query, limit=5)
        if not results:
            print("No results found.")
            continue
        for index, result in enumerate(results):
            print(f"\nRESULT {index + 1}")
            print("Distance:", result["distance"])
            print("Source:", result["metadata"].get("source"))
            print("Text:", result["text"])


if __name__ == "__main__":
    main()
