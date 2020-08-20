from . import GameObject

class Wall(GameObject):
    def __init__(self, location, tags = []):
        tempTags = tags.copy()
        tempTags.append("wall")

        super().__init__(tempTags)

        self.location = location