class WorkingMemory:
    """"A simple class to represent working memory, 
    which can store and manage items temporarily.
    """
    def __init__(self):
        self.items = []

    def add(self, content):
        self.items.append(content)

    def get_all(self):
        return self.items.copy()

    def clear(self):
        self.items.clear()