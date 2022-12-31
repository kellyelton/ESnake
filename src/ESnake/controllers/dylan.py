import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake
from . import NetV2


class Dylan:
    net: NetV2

    def __init__(self, parent:"Dylan" = None, mutate=True):
        self.logger = logging.getLogger(__name__)

        inputCount = 3
        outputCount = 2

        if parent is None:
            self.net = NetV2(inputCount, outputCount)
            self.color = (random.randint(30, 200), random.randint(30, 200), random.randint(30, 200))
        else:
            if mutate:
                self.net = parent.net.mutate()
                # use parent color, but randomly change one of the RGB values up to 1%
                self.color = (parent.color[0] + random.randint(-10, 10), parent.color[1] + random.randint(-10, 10), parent.color[2] + random.randint(-10, 10))
                # make sure no color value is less than 30 or greater than 200
                self.color = (max(30, min(200, self.color[0])), max(30, min(200, self.color[1])), max(30, min(200, self.color[2])))
            else:
                self.net = parent.net.clone()
                self.color = parent.color

    def update(self, app, time, level, snake):
        pass
    
    def move(self, app, time, level, snake):
        snake_head_location = snake.segments[0].location

        if snake.viewLocationsCount != self.net.num_inputs:
            raise Exception("Number of view locations does not match number of inputs")

        inputs = []
        for i in range(0, snake.viewLocationsCount):
            contents = snake.viewContents[i]
            inputs.append(self.getLevelContents(level, snake, contents))

        outputs = self.net.process(inputs)

        # All outputs should be between 0 and 1
        for output in outputs:
            if output < 0 or output > 1:
                raise Exception("Output is not between 0 and 1")

        # if the first output is greater than 0.8, then the snake should turn left
        # if the second output is greater than 0.8, then the snake should turn right
        # if both are greater than 0.8, then the snake should not turn
        # if both are equal, then the snake should not turn
        
        if outputs[0] > 0.8 and outputs[1] > 0.8:
            snake.requestedDirection = Direction.none()
        elif outputs[0] > 0.8:
            snake.requestedDirection = Direction.left()
        elif outputs[1] > 0.8:
            snake.requestedDirection = Direction.right()
        else:
            snake.requestedDirection = Direction.none()

    def getLevelContents(self, level, snake, contents):
        if contents is None:
            # nothing, probably outside of bounds
            return 0
        elif contents is snake:
            # self
            return -1
        elif isinstance(contents, Food):
            # Food to eat
            return 1
        elif isinstance(contents, Snake):
            # other ai snek
            return -1
        elif contents is level.player:
            # other snek, player snek
            return -1
        elif isinstance(contents, Wall):
            return -1
        else:
            raise Exception("invalid contents")