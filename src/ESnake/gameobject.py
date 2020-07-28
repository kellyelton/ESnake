class GameObject:
    nextId = 1
    def __init__(self, tags = []):
        self.id = GameObject.nextId
        GameObject.nextId = GameObject.nextId + 1
        self.tags = tags