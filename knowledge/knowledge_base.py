import os

from knowledge.vector_store import VectorStore


class KnowledgeBase:
    ''' 
    A class that represents a knowledge base for an AI agent. It loads documents 
    from a specified folder, splits them into chunks, and stores them in a vector 
    store for efficient retrieval.
    '''
    
    def __init__(self, folder = "knowledge/documents"):
        self.folder = folder
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

            for index, chunk in enumerate(chunks):
                document_id = (f"{file_name}_chunk_{index}")
                self.vector_store.add_document(
                    document_id, 
                    chunk, 
                    {
                        "source": file_name,
                        "chunk": index
                        }
                    )
    

    def search (self, query, limit=3):
        '''
        Search for relevant documents in the vector store based on the query.
        Returns a list of documents that match the query.
        '''
        results = self.vector_store.search(query, limit)

        documents = results.get("documents", [[]])

        if not documents or not documents[0]:
            return []

        return documents[0]

    def chunk_text(self, text, chunk_size=250):
        """
        Split the text into chunks of a specified size.
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

