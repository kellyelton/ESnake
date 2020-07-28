from . import GameObject

class Wall(GameObject):
    def __init__(self, location, tags = []):
        self.tags = tags.append("wall")

        super().__init__(tags)

        self.location = location