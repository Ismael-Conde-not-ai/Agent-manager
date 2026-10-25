from memory.experience_memory import ExperienceMemory
from memory.persistent_memory import PersistentMemory
from memory.working_memory import WorkingMemory


class MemoryManager:
    """
    A class that manages different types of memory: working, persistent, and experience.
    """
    def __init__(self):
        self.working = WorkingMemory()
        self.persistent = PersistentMemory()
        self.experience = ExperienceMemory()        

    def remember(self, content):
        """
        Store content in working memory...
        """
        self.working.add(content)

    def get_working_memory(self):
        """
        Retrieve all items from working memory...
        """
        return self.working.get_all()

    def clear_working_memory(self):
        """
        Clear all items from working memory...
        """
        self.working.clear()

    def remember_persistently(self, key, value):
        """
        Store a key-value pair in persistent memory...
        """
        self.persistent.remember(key, value)

    def recall_persistently(self, key):
        """
        Retrieve a value from persistent memory by key...
        """
        return self.persistent.recall(key)

    def forget_persistently(self, key):
        """
        Remove a key-value pair from persistent memory...
        """
        return self.persistent.forget(key)

    def get_persistent_memories(self):
        """
        Retrieve all items from persistent memory...
        """
        return self.persistent.get_all()

    def persistent_memory_count(self):
        """
        Get the count of items in persistent memory...
        """
        return self.persistent.count()

    def record_experience(self, experience):
        """
        Store an experience in experience memory...
        """
        return self.experience.record(experience)

    def search_experiences(self, query, limit=5):
        """
        Search for experiences in experience memory based on a query...
        """
        return self.experience.search(query, limit)

    def get_experiences(self):
        """
        Retrieve all experiences from experience memory...
        """
        return self.experience.get_all()