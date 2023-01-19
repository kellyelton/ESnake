import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake
from . import NetV2


class Dylan2:
    net: NetV2

    def __init__(self, view_distance, parent:"Dylan2" = None, mutate=True):
        self.logger = logging.getLogger(__name__)

        self.view_distance = view_distance

        # inputs = [direction, distance, reward, punishment, direction, distance, reward, punishment, ...]
        # outputs = [left, right, none]

        inputCount = (4 * 5)
        outputCount = 3

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
        # flatten view
        inputs = [
        ]
        for direction, distance, reward, punishment in snake.view2:
            inputs.append(direction)
            inputs.append(distance)
            inputs.append(reward)
            inputs.append(punishment)

        if len(inputs) != self.net.num_inputs:
            raise Exception("Number of view locations does not match number of inputs")

        outputs = self.net.process(inputs)

        # All outputs should be between 0 and 1
        for output in outputs:
            if output < 0 or output > 1:
                raise Exception("Output is not between 0 and 1")

        # outputs = [left, right, none]

        req_direction = outputs.index(max(outputs))
    
        if req_direction == 0:
            snake.requestedDirection = Direction.left()
        elif req_direction == 1:
            snake.requestedDirection = Direction.right()
        elif req_direction == 2:
            snake.requestedDirection = Direction.none()
        else:
            raise Exception(f"Invalid direction {req_direction}")