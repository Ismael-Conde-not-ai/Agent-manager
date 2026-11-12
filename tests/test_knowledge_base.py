from knowledge.knowledge_base import KnowledgeBase
from tests.output import configure_utf8_output


def main():
    configure_utf8_output()
    knowledge = KnowledgeBase()
    query = "How do AI agents use planning?"
    results = knowledge.search(query, limit=3)

    print("\nQUERY:")
    print(query)
    print("\nRESULTS:\n")

    for index, result in enumerate(results):
        print(f"RESULT {index + 1}")
        print("ID:", result["id"])
        print("DISTANCE:", result["distance"])
        print("TEXT:", result["text"])
        print("METADATA:", result["metadata"])
        print("-" * 60)


if __name__ == "__main__":
    main()
