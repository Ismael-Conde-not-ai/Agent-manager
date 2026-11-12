from knowledge.knowledge_base import KnowledgeBase
from tests.output import configure_utf8_output


def main():
    configure_utf8_output()
    knowledge = KnowledgeBase()
    results = knowledge.search("How does AI agents planning work?", limit=3)
    print(results)


if __name__ == "__main__":
    main()
