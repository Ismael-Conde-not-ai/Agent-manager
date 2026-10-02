#import os

from knowledge.context_builder import ContextBuilder
from knowledge.document_loader import DocumentLoader
from knowledge.document_registry import DocumentRegistry
from knowledge.document_sync import DocumentSync
from knowledge.vector_store import VectorStore


class KnowledgeBase:
    ''' 
    A class that represents a knowledge base for an AI agent. It loads documents 
    from a specified folder, splits them into chunks, and stores them in a vector 
    store for efficient retrieval.
    '''
    
    def __init__(self, folder = "knowledge/documents"):
        self.folder = folder
        self.context_builder = ContextBuilder()
        self.document_loader = DocumentLoader(folder)
        self.registry = DocumentRegistry()
        self.document_sync = DocumentSync(self)
        self.vector_store = VectorStore()

        #self.load_documents()
        

    def load_documents(self):
        '''
        Load documents from the specified folder, split them into chunks, and add
        them to the vector store with metadata indicating the source file and chunk index.
        '''
        
        documents = self.document_loader.load_documents()

        for document in documents:
            self.index_document(document)
    

    def search (self, query, limit=3, max_distance=None,source=None,category=None):
        '''
        Search for relevant documents in the vector store based on the query.
        Returns a list of documents that match the query.
        '''
        metadata_filter = None
        if source is not None:
            metadata_filter = {"source": source}
        if category is not None:
            if metadata_filter is None:
                metadata_filter = {"category": category}
            else:
                metadata_filter = {
                    "$and": [
                        metadata_filter,
                        {"category": category}
                    ]
                }

        results = self.vector_store.search(query, limit, metadata_filter)

        documents = results.get("documents", [[]])
        metadatas = results.get("metadatas", [[]])
        ids = results.get("ids", [[]])
        distances = results.get("distances", [[]])

        if not documents or not documents[0]:
            return []

        results_list = []
        for index, document in enumerate(documents[0]):

            distance = distances[0][index]
            if max_distance is not None and distance > max_distance:
                continue

            results_list.append({
                "id": ids[0][index],
                "text": document,
                "metadata": metadatas[0][index],
                "distance": distances[0][index]
            })

        return results_list

    def chunk_text(self, text, chunk_size=500, overlap=50):
        """
        Split the text into chunks of a specified size.
        """
        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk size.")
        
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)

            start += chunk_size - overlap
        return chunks

    def get_context(self, query, limit=3, max_characters=4000, max_distance=None):
        """
        Get a context string based on the search results for the given query.
        """
        results = self.search(query, limit, max_distance)
        return self.context_builder.build_context(results, max_characters)

    def delete_document(self, source):
        """
        Delete a document from the vector store by its source file name.
        """
        self.vector_store.delete_by_source(source)
        self.registry.delete(source)

    def update_document(self, file_name):
        """
        Update a document in the vector store by reloading it from the file system.
        """
        document = self.document_loader.load_document(file_name)

        if document is None:
            return False

        self.delete_document(file_name)

        self.index_document(document)
        return True

    def index_document(self, document):
        """
        Index a single document in the vector store.
        """
        file_name = document["file_name"]
        content = document["content"]
        base_metadata = document["metadata"]

        chunks = self.chunk_text(content)
        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks):
            document_id = f"{file_name}_chunk_{index}"

            metadata = {
                **base_metadata,
                "chunk_index": index,
                "total_chunks": total_chunks
            }

            self.vector_store.add_document(
                document_id, 
                chunk,
                metadata
            )

            self.registry.set(file_name, {
                "source": file_name,
                "file_hash": base_metadata["file_hash"],
                "category": base_metadata["category"],
                "chunk_count": total_chunks
            })

    def sync(self):
        """
        Synchronize the documents in the vector store with the documents in the folder.
        This will add new documents, update modified documents, and delete removed documents.
        """
        return self.document_sync.sync()