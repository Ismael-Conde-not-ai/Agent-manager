import unittest

from tools.search_knowledge import search_knowledge


class FakeAgent:
    def get_relevant_context(self):
        return [
            {"text": "RAG retrieves relevant documents."},
            {"text": "The agent uses context to make decisions."}
        ]


class TestSearchKnowledge(unittest.TestCase):

    def test_search_knowledge_returns_context(self):
        result = search_knowledge(FakeAgent())

        self.assertIsInstance(result, list)

        texts = [
            item["text"]
            for item in result
        ]

        self.assertIn(
            "RAG retrieves relevant documents.",
            texts
        )

        self.assertIn(
            "The agent uses context to make decisions.",
            texts
        )

    def test_search_knowledge_returns_text_items(self):
        result = search_knowledge(FakeAgent())

        for item in result:
            self.assertIsInstance(item, dict)
            self.assertIn("text", item)


if __name__ == "__main__":
    unittest.main()
