import json
import os


class PersistentMemory:
    """
    A class that represents a persistent memory storage system.
    """
    def __init__(self, path="data/memory.json"):
        """
        Initializes the PersistentMemory instance with a specified file path.
        Args:
            path (str): The file path where the memory will be stored.
        """
        self.path = path
        self.memories = {}

        self.load()

    def load(self):
        """
        Loads the memory from the specified file path.
        If the file does not exist, it initializes an empty memory.
        """
        if not os.path.exists(self.path):
            self.memories = {}
            return

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise TypeError("Memory file must contain JSON object")
            self.memories = data
        except (json.JSONDecodeError, TypeError) as error:
            raise ValueError(f"Invalid memory file: {self.path}") from error

    def save(self):
        """
        Saves the current memory to the specified file path.
        """
        directory = os.path.dirname(self.path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self.memories, file, indent=4, ensure_ascii=False)

    def remember(self, key, value):
        """
        Stores a key-value pair in the memory.
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Memory key must be a non-empty string")

        self.memories[key] = value
        self.save()

        
    def recall(self, key):
        """
        Retrieves the value associated with a key from the memory.
        Returns None if the key does not exist.
        """
        return self.memories.get(key)
    
    def forget(self, key):
        """
        Removes a key-value pair from the memory.
        Returns True if the key exists and is removed, False otherwise.
        """
        if key not in self.memories:
            return False

        del self.memories[key]
        self.save()
        return True

    def get_all(self):
        """
        Returns a copy of all key-value pairs in the memory.
        """
        return self.memories.copy()