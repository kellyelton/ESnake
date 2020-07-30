from . import GameObject, Direction

class SnakeSegment(GameObject):
    def __init__(self, snake, location, direction: Direction, tags = []):
        tags.append("snake")
        tags.append("snakesegment")

        self.snake = snake
        self.direction: Direction = direction
        self.location = location
        self.isHead = True

        if self.isHead:
            tags.append("snakehead")
        else:
            tags.append("snakebody")

        super().__init__(tags=tags)

    def isTipOfTail(self):
        return self.index == len(self.snake.segments) - 1