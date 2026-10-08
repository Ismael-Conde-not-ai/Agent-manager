import json
import os
from datetime import datetime


class DocumentHistory:
    """
    A class to manage the history of document versions.
    """
    def __init__(self, path="data/document_history.json"):
        self.path = path
        self.history = {}

        self.load()

    def load(self):
        if not os.path.exists(self.path):                
            self.history = {}
            return

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                self.history = json.load(file)
        except Exception:
            self.history = {}

    def save(self):
        """Saves the current history to the specified JSON file."""
        directory = os.path.dirname(self.path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                self.history,
                file,
                indent=4,
                ensure_ascii=False
            )

    def add_version(self, source, file_hash, chunk_count):
        """Adds a new version entry for a document source."""
        if source not in self.history:
            self.history[source] = []

        versions = self.history[source]

        version_number = len(versions) + 1

        version = {
            "version": version_number,
            "file_hash": file_hash,
            "chunk_count": chunk_count,
            "created_at": datetime.now().astimezone().isoformat()
        }

        versions.append(version)

        self.save()

        return version

    def get_history(self, source):
        """Returns the version history for a given document source."""
        return self.history.get(source, [])

    def get_latest_version(self, source):
        """Returns the latest version entry for a document source."""
        versions = self.get_history(source)
        if not versions:
            return None
        return versions[-1]
                    