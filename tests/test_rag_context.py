from knowledge.knowledge_base import KnowledgeBase
from tests.output import configure_utf8_output


def main():
    configure_utf8_output()
    knowledge = KnowledgeBase()
    context = knowledge.get_context(
        "How do AI agents use planning?",
        limit=3,
    )
    print("\nRAG CONTEXT\n")
    print(context)


if __name__ == "__main__":
    main()
