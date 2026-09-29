import os

from knowledge.context_builder import ContextBuilder
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
        self.vector_store = VectorStore()

        self.load_documents()
        

    def load_documents(self):
        '''
        Load documents from the specified folder, split them into chunks, and add
        them to the vector store with metadata indicating the source file and chunk index.
        '''
        
        for file_name in os.listdir(self.folder):
            path = os.path.join(self.folder,file_name)

            if not os.path.isfile(path):
                continue

            with open(path,"r",encoding="utf-8") as f:
                content = f.read()

            chunks = self.chunk_text(content)

            total_chunks = len(chunks)

            for index, chunk in enumerate(chunks):
                document_id = (f"{file_name}_chunk_{index}")

                metadata = {
                    "source": file_name,
                    "chunk_index": index,
                    "total_chunks": total_chunks
                }

                self.vector_store.add_document(
                    document_id, 
                    chunk,
                    metadata
                    )
    

    def search (self, query, limit=3):
        '''
        Search for relevant documents in the vector store based on the query.
        Returns a list of documents that match the query.
        '''
        results = self.vector_store.search(query, limit)

        documents = results.get("documents", [[]])
        metadatas = results.get("metadatas", [[]])
        ids = results.get("ids", [[]])

        if not documents or not documents[0]:
            return []

        results_list = []
        for index, document in enumerate(documents[0]):
            results_list.append({
                "id": ids[0][index],
                "text": document,
                "metadata": metadatas[0][index]
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

    def get_context(self, query, limit=3, max_characters=4000):
        """
        Get a context string based on the search results for the given query.
        """
        results = self.search(query, limit)
        return self.context_builder.build_context(results, max_characters)