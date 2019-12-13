from ESnake.direction import Direction

def Location(location: (int, int)):
    return Location(location[0], location[1])

class Location:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def getNeighbor(self, direction: Direction):
        if direction == Direction.left:
            return Location(self.x - 1, self.y)
        elif direction == Direction.right:
            return Location(self.x + 1, self.y)
        elif direction == Direction.up:
            return Location(self.x, self.y - 1)
        elif direction == Direction.down:
            return Location(self.x, self.y + 1)
        else: raise Exception(f"Invalid direction {direction}")

    def __str__(self):
        return f"({self.x}, {self.y})"
        
    def __eq__(self, value):
        if value == None:
            return False
        elif isinstance(value, Location):
            return value.x == self.x and value.y == self.y
        elif isinstance(value, (int, int)):
            return self.x == value[0] and self.y == value[1]
        else:
            return False