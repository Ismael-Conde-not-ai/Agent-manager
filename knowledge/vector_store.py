import chromadb


class VectorStore:

    def __init__(self, collection_name="agent_knowledge"):
        self.client = chromadb.PersistentClient(path="data/vector_db")
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_document(self, document_id, text):
        """
        Add a document to the vector store.
        """
        self.collection.add(
            ids=[document_id],
            documents=[text]
        )

    def search(self, query, limit=3):
        """
        Search for documents in the vector store.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        return results