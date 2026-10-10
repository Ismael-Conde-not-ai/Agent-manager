class ExperienceMemory:
    """
    A class that represents an experience memory storage system.
    """
    def record(self, experience):
        raise NotImplementedError
    def search(self, query, limit=5):
        raise NotImplementedError