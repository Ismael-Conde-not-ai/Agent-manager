import tempfile
import unittest

from knowledge.vector_store import VectorStore


class TestVectorStore(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.store = VectorStore(
            path=self.temp_dir.name,
            collection_name="test_agent_knowledge"
        )

    def tearDown(self):
        self.store.close()
        self.temp_dir.cleanup()

    def test_add_document_without_metadata(self):
        self.store.add_document(
            "ai_001",
            "AI agents use planning tools and memory."
        )

        self.assertEqual(self.store.count(), 1)

    def test_add_document_with_metadata(self):
        self.store.add_document(
            "rag_001",
            "RAG retrieves relevant information.",
            metadata={
                "source": "test.txt",
                "category": "AI"
            }
        )

        self.assertEqual(self.store.count(), 1)

    def test_search_documents(self):
        self.store.add_document(
            "ai_001",
            "AI agents use planning tools and memory."
        )

        results = self.store.search(
            "How do AI agents use planning?"
        )

        self.assertIn("documents", results)
        self.assertTrue(results["documents"][0])

    def test_delete_document(self):
        self.store.add_document(
            "ai_001",
            "AI agents use planning tools."
        )

        self.store.delete_document("ai_001")

        self.assertEqual(self.store.count(), 0)

    def test_get_sources(self):
        self.store.add_document(
            "rag_001",
            "RAG retrieves relevant information.",
            metadata={
                "source": "rag.txt"
            }
        )

        sources = self.store.get_sources()

        self.assertIn("rag.txt", sources)


if __name__ == "__main__":
    unittest.main()