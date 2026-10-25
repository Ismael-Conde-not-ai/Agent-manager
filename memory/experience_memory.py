import json
import os
from datetime import datetime, timezone
from uuid import uuid4


class ExperienceMemory:
    """
    A class that represents an experience memory storage system.
    """
    def __init__(self, path="data/experience_memory.json"):
        self.path = path
        self.experiences = []

        self.load()

    def load(self):
        """
        Loads the experiences from the specified file path.
        If the file does not exist, it initializes an empty experience memory.
        """
        if not os.path.exists(self.path):
            self.experiences = []
            return

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                raise TypeError("Experience memory file must contain a JSON list")
            self.experiences = data
        except (json.JSONDecodeError, TypeError) as error:
            raise ValueError(f"Invalid experience memory file: {self.path}") from error

    def save(self):
        """
        Saves the current experiences to the specified file path.
        """
        directory = os.path.dirname(self.path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self.experiences, file, indent=4, ensure_ascii=False)

    def record(self, experience):
        """
        Records a new experience in the memory.
        Each experience is stored as a dictionary with a unique ID and timestamp.
        """
        if not isinstance(experience, dict):
            raise TypeError("Experience must be a dictionary")

        entry = experience.copy()
        entry["id"] = str(uuid4())
        entry["created_at"] = datetime.now(timezone.utc).isoformat()
        self.experiences.append(entry)
        self.save()
        return entry
    def get_all(self):
        """
        Retrieves all recorded experiences.
        """
        return [experience.copy() for experience in self.experiences]
    
    def search(self, query, limit=5):
        """
        Searches for experiences that match the given query.
        The search is case-insensitive and looks for the query terms in the JSON representation of each experience.
        Returns a list of matching experiences, limited to the specified number.
        """
        if limit < 1:
            return []

        query_terms = set(query.lower().split())

        if not query_terms:
            return []

        matches = []

        for experience in reversed(self.experiences):
            searchable_text = json.dumps(experience, ensure_ascii=False).lower()

            if any(term in searchable_text for term in query_terms):
                matches.append(experience.copy())

            if len(matches) >= limit:
                break

        return matches

    def count(self):
        """
        Returns the number of recorded experiences.
        """
        return len(self.experiences)