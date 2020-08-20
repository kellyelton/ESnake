import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake

class Dylan:
    viewRadius = 10
    def __init__(self, parent = None):
        self.logger = logging.getLogger(__name__)

        inputCount = ((self.viewRadius*2)**2)+(self.viewRadius * 4)+1
        inputCount += 3 #direction and energy
        layer2Count = 16
        outputCount = 6

        if parent == None:
            self.weights0 = np.random.uniform(-1,1,size = (inputCount, layer2Count))
            self.weights1 = np.random.uniform(-1,1,size = (layer2Count, layer3Count))
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

            self.weights0 = np.empty((inputCount, layer2Count))
            for inputNum in range(0, inputCount):
                for layer2Num in range(0, layer2Count):
                    adjustment = random.uniform(-adjustmentMax, adjustmentMax)

                    newWeight = parent.weights0[inputNum][layer2Num]
                    newWeight = newWeight + adjustment;
                    newWeight = clamp(newWeight)

                    self.weights0[inputNum][layer2Num] = newWeight

            self.weights1 = np.empty((layer2Count, outputCount))
            for layer2Num in range(0, layer2Count):
                for outputNum in range(0, outputCount):
                    adjustment = random.uniform(-adjustmentMax, adjustmentMax)

                    newWeight = parent.weights1[layer2Num][outputNum]
                    newWeight = newWeight + adjustment;
                    newWeight = clamp(newWeight)

                    self.weights1[layer2Num][outputNum] = newWeight

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

        center = snake.segments[0].location

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
        elif isinstance(contents, Food):
            return 0.80
        elif contents is level.player:
            return 0.60
        elif isinstance(contents, Snake):
            return 0.40
        elif isinstance(contents, Wall):
            return 0.20
        else: raise "invalid contents"

    def activation(self, x):
        return 1 / (1 + np.exp(-x))