import datetime
import json
import os
import re
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

        # An empty file represents an empty experience history.
        if os.path.getsize(self.path) == 0:
            self.experiences = []
            self.save()
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
        entry["created_at"] = datetime.datetime.now(datetime.UTC).isoformat()
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
        Searches for experiences that match the given query.
        """
        if limit < 1:
            return []

        stopwords = {
            "a", "an", "the", "about", "and", "or", "of",
            "to", "in", "on", "for", "with", "by", "from",
            "is", "are", "was", "were", "how", "what",
            "when", "where", "why", "who", "do", "does",
            "did", "can", "could", "should", "would",
            "i", "you", "we", "they", "it", "this", "that",
            "be", "as", "at", "before", "after"
        }

        def tokenize(text):
            words = re.findall(r"\b[a-z0-9]+\b", str(text).lower())
            return {
                word for word in words
                if word not in stopwords and len(word) > 1
            }

        query_terms = tokenize(query)
        matches = []

        for index, experience in enumerate(self.experiences):
            if success is not None and experience.get("success") != success:
                continue

            if action is not None and experience.get("action") != action:
                continue

            searchable_fields = [
                experience.get("goal", ""),
                experience.get("action", ""),
                experience.get("result", ""),
                experience.get("error", ""),
                experience.get("lesson", "")
            ]

            searchable_terms = tokenize(
                " ".join(str(value) for value in searchable_fields)
            )

            if query_terms:
                matched_terms = query_terms & searchable_terms
                score = len(matched_terms) / len(query_terms)

                # Exigir coincidencia suficiente para considerar
                # una experiencia relevante.
                if not matched_terms or score < 0.30:
                    continue
            else:
                score = 0

            matches.append({
                "experience": experience,
                "score": score,
                "position": index
            })

        matches.sort(
            key=lambda item: (item["score"], item["position"]),
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