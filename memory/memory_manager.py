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