import logging
import random
import numpy as np

from .. import Direction

class Dylan:
    viewRadius = 5
    def __init__(self, parent = None):
        self.logger = logging.getLogger(__name__)

        inputCount = ((self.viewRadius*2)**2)+(self.viewRadius * 4)+1
        inputCount += 3 #direction and energy
        layer2Count = 16
        outputCount = 6

        if parent == None:
            self.weights0 = np.random.uniform(-1,1,size = (inputCount, layer2Count))
            self.weights1 = np.random.uniform(-1,1,size = (layer2Count, outputCount))
        else:
            def clamp(num):
                if num > 1:
                    return 1
                elif num < -1:
                    return -1
                else: return num
            def clampRow(weights):
                return [clamp(weight) for weight in weights]

            adjustmentMax = random.random()

            adjustments = np.random.uniform(-(adjustmentMax), adjustmentMax, size = (inputCount, layer2Count))
            self.weights0 = np.add(adjustments, parent.weights0)
            self.weights0 = np.array([clampRow(row) for row in self.weights0])

            adjustments = np.random.uniform(-(adjustmentMax), adjustmentMax, size = (layer2Count, outputCount))
            self.weights1 = np.add(adjustments, parent.weights1)
            self.weights1 = np.array([clampRow(row) for row in self.weights1])

    def update(self, app, time, level, snake):
        if snake.direction == None:
            snake.direction = Direction.right

    def move(self, app, time, level, snake):
        direction = snake.direction.toVector()
        inputs = [
            direction[0],
            direction[1],
            snake.energy
        ]

        center = snake.segments[0]

        startX = center[0] - self.viewRadius
        startY = center[1] - self.viewRadius

        endX = center[0] + self.viewRadius
        endY = center[1] + self.viewRadius

        for y in range(startY, endY + 1):
            for x in range(startX, endX + 1):
                inputs.append(self.getLevelContents(level, snake, x, y))

        layer0 = self.activation(np.dot(inputs, self.weights0))
        outputs = self.activation(np.dot(layer0, self.weights1))

        oChangeDirection = outputs[0]

        if oChangeDirection <= 0.25: #left
            snake.requestedDirection = Direction.left
        elif oChangeDirection <= 0.50: #up
            snake.requestedDirection = Direction.up
        elif oChangeDirection <= 0.75: #right
            snake.requestedDirection = Direction.right
        elif oChangeDirection <= 1: #down
            snake.requestedDirection = Direction.down

    def getLevelContents(self, level, snake, x, y):
        if level.isOutsideWall((x, y)):
            return -1

        contents = level.getContents((x, y))

        if contents is None:
            return 0
        elif contents is snake:
            return 1
        elif "food" in contents.tags:
            return 0.80
        elif "player" in contents.tags:
            return 0.60
        elif "bot" in contents.tags:
            return 0.40
        elif "wall" in contents.tags:
            return 0.20
        else: raise "invalid contents"

    def activation(self, x):
        return 1 / (1 + np.exp(-x))