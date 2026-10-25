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
    
    def search(self, query="", limit=5, success=None, action=None):
        """
        Searches for experiences in the memory based on a query string.
        """
        if limit < 1:
            return []

        query_terms = set(
            query.lower().split()
        )

        matches = []

        for index, experience in enumerate(
            self.experiences
        ):
            if (
                success is not None
                and experience.get("success") != success
            ):
                continue

            if (
                action is not None
                and experience.get("action") != action
            ):
                continue

            searchable_fields = [
                experience.get("goal", ""),
                experience.get("action", ""),
                experience.get("result", ""),
                experience.get("error", ""),
                experience.get("lesson", "")
            ]

            searchable_text = " ".join(
                str(value)
                for value in searchable_fields
            ).lower()

            matched_terms = sum(
                1
                for term in query_terms
                if term in searchable_text
            )

            if query_terms and matched_terms == 0:
                continue

            score = (
                matched_terms / len(query_terms)
                if query_terms
                else 0
            )

            matches.append({
                "experience": experience,
                "score": score,
                "position": index
            })

        matches.sort(
            key=lambda item: (
                item["score"],
                item["position"]
            ),
            reverse=True
        )

        return [
            item["experience"].copy()
            for item in matches[:limit]
        ]

    def count(self):
        """
        Returns the number of recorded experiences.
        """
        return len(self.experiences)