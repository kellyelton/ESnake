import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake

class Automatic:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.color = (255, 0, 255)
    
    def update(self, app, time, level, snake):
        pass

    def move(self, app, time, level, snake):
        front = snake.viewContents[0]
        left = snake.viewContents[1]
        right = snake.viewContents[2]

        # If we can go forward, just go forward

        # move toword Food first.
        if isinstance(front, Food):
            snake.requestedDirection = Direction.none()
            return
        
        if random.random() < 0.5:
            if isinstance(left, Food):
                snake.requestedDirection = Direction.left()
                return
            if isinstance(right, Food):
                snake.requestedDirection = Direction.right()
                return
        else:
            if isinstance(right, Food):
                snake.requestedDirection = Direction.right()
                return
            if isinstance(left, Food):
                snake.requestedDirection = Direction.left()
                return

        # Turn if we can't go forward
        if front is not None:
            if random.random() < 0.5:
                if left is None:
                    snake.requestedDirection = Direction.left()
                    return
                if right is None:
                    snake.requestedDirection = Direction.right()
                    return
            else:
                if right is None:
                    snake.requestedDirection = Direction.right()
                    return
                if left is None:
                    snake.requestedDirection = Direction.left()
                    return
        
