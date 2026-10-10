class PersistentMemory:
    """
    A class that represents a persistent memory storage system.
    """
    def remember(self, key, value):
        raise NotImplementedError
    def recall(self, key):
        raise NotImplementedError
    def forget(self, key):
        raise NotImplementedError