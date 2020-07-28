from . import GameObject

class Food(GameObject):
    def __init__(self, location, tags = []):
        self.tags = tags.append("food")

        super().__init__(tags)

        self.location = location