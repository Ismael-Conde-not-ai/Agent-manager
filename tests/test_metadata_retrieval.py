from knowledge.knowledge_base import KnowledgeBase
from tests.output import configure_utf8_output


def main():
    configure_utf8_output()
    knowledge = KnowledgeBase()
    for title, query in (
        ("SOURCE FILTER", "How do AI agents use planning?"),
        ("CATEGORY FILTER", "How do AI agents use tools?"),
    ):
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)
        for result in knowledge.search(query, limit=5):
            print("\nID:", result["id"])
            print("Source:", result["metadata"].get("source"))
            print("Category:", result["metadata"].get("category"))
            print("Distance:", result["distance"])
            print("Text:", result["text"])


if __name__ == "__main__":
    main()
