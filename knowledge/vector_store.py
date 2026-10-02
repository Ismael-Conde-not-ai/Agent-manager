import chromadb


class VectorStore:
    
    """
    A vector store for managing documents and their embeddings.
    """

    def __init__(self, path = "data/vector_db", collection_name="agent_knowledge"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_document(self, document_id, text, metadata=None):
        """
        Add a document to the vector store.
        """
        self.collection.upsert(
            ids=[document_id],
            documents=[text],
            metadatas=[metadata or {}]
        )

    def search(self, query, limit=3, metadata_filter=None):
        """
        Search for documents in the vector store.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=metadata_filter,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )
        return results

    def count(self):
        """
        Count the number of documents in the vector store.
        """
        return self.collection.count()

    def delete_document(self, document_id):
        """
        Delete a document from the vector store.
        """
        self.collection.delete(
            ids=[document_id]
        )

    def delete_by_source(self, source):
        """
        Delete documents from the vector store by source.
        """
        self.collection.delete(
            where={"source": source}
        )

    def get_sources(self):
        """
        Get a set of all sources in the vector store.
        """
        results = self.collection.get(include=["metadatas"])
        metadatas = results.get("metadatas", [])
        sources = set()

        for metadata in metadatas:
            if metadata and "source" in metadata:
                sources.add(metadata["source"])

        return sources

    def get_document_hash(self, source):
        """
        Get the hash of a document by its source.
        """
        results = self.collection.get(
            where={"source": source},
            include=["metadatas"]
        )
        metadatas = results.get("metadatas", [])

        if not metadatas:
            return None
        metadata = metadatas[0]
        if not metadata:
            return None
        
        return metadata.get("file_hash")