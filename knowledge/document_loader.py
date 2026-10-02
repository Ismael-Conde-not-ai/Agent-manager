import hashlib
import os


class DocumentLoader:
    def __init__(self, folder = "knowledge/documents"):
        self.folder = folder

    def load_documents(self):
        '''
        Load documents from the specified folder and return a list of tuples containing
        the file name and its content.
        '''
        documents = []
        
        for file_name in os.listdir(self.folder):
            document = self.load_document(file_name)
            if document is not None:
                documents.append(document)
        
        return documents

    def get_category(self, file_name):
        '''
        Determine the category of the document based on its file name.
        '''
        if "planning" in file_name.lower():
            return "planning"
        if "ai" in file_name.lower():
            return "ai"
        if "tool" in file_name.lower():
            return "tool"
        return "general"

    def load_document(self, file_name):
        """
        Load a single document by its file name and return its content and metadata.
        """
        path = os.path.join(self.folder, file_name)

        if not os.path.isfile(path):
            return None
        if not file_name.endswith(".txt"):
            return None

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        category = self.get_category(file_name)
        file_hash = self.get_document_hash(content)

        return {
            "file_name": file_name,
            "content": content,
            "metadata": {
                "source": file_name,
                "category": category,
                "file_hash": file_hash
            }
        }

    def get_document_hash(self, content):
        """
        Generate a md5_hash for the given content.
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()