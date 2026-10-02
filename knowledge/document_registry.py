import json
import os


class DocumentRegistry:

    def __init__(self, path="data/document_registry.json"):
        self.path = path
        self.documents = {}

        self.load()

    def load(self):
        """
        Load the document registry from a JSON file.
        """
        if not os.path.exists(self.path):
            self.documents = {}
            return

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                self.documents = json.load(file)
        except (json.JSONDecodeError, OSError) as e:
            self.documents = {}

    def save(self):
        """
        Save the document registry to a JSON file.
        """
        directory = os.path.dirname(self.path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                self.documents,
                file,
                indent=4,
                ensure_ascii=False
            )

    def exists(self, source):
        """
        Check if a document with the given source exists in the registry.
        """
        return source in self.documents

    def get(self, source):
        """
        Get the metadata of a document by its source.
        """
        return self.documents.get(source)

    def set(self, source, metadata):
        """
        Set the metadata for a document in the registry.
        """
        self.documents[source] = metadata
        self.save()

    def delete(self, source):
        """
        Delete a document from the registry by its source.
        """
        if source in self.documents:
            del self.documents[source]
            self.save()