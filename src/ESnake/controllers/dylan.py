import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake

class Dylan:
    viewRadius = 5
    def __init__(self, parent = None):
        self.logger = logging.getLogger(__name__)

        if parent == None:
            self.weights = list(self.createBrainFromScratch())
        else:
            self.weights = list(self.createBrainFromParent(parent))
        
    def createBrainFromScratch(self):
        inputCount = ((self.viewRadius*2)**2)+(self.viewRadius * 4)+1
        inputCount += 3 #direction and energy
        outputCount = 6

        hiddenLayerSizes = [16, 16, 16, 16]
        hiddenLayerCount = len(hiddenLayerSizes)

        layerSizes = [inputCount, *hiddenLayerSizes, outputCount]
        layerCount = hiddenLayerCount + 2

        for i in range(0, layerCount - 1):
            layerSize = layerSizes[i]

            nextLayerSize = layerSizes[i + 1]

            layer = np.random.uniform(-1, 1, size = (layerSize, nextLayerSize))

            yield layer

    def createBrainFromParent(self, parent):
            def clamp(num):
                if num > 1:
                    return 1
                elif num < -1:
                    return -1
                else: return num
            def clampRow(weights):
                return [clamp(weight) for weight in weights]

            adjustmentMax = random.random() # maximum deviation that can occur per weight

            layerCount = len(parent.weights)

            for i in range(0, layerCount):
                layer = parent.weights[i].copy()

                sourceCount = len(layer)

                for sourceIndex in range(0, sourceCount):
                    source = layer[sourceIndex]

                    targetCount = len(source)

                    for targetIndex in range(0, targetCount):
                        adjustment = random.uniform(-adjustmentMax, adjustmentMax)

                        newWeight = parent.weights[i][sourceIndex][targetIndex]
                        newWeight = newWeight + adjustment;
                        newWeight = clamp(newWeight)

                        layer[sourceIndex][targetIndex] = newWeight

                yield layer

    def update(self, app, time, level, snake):
        pass

    def move(self, app, time, level, snake):
        if snake.direction != None:
            direction = snake.direction.toVector()
        else:
            direction = (0, 0)

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

        outputs = self.compute(inputs)

        oChangeDirection = outputs[0]

        if oChangeDirection <= 0.20: #None
            snake.requestedDirection = None
        elif oChangeDirection <= 0.40: #left
            snake.requestedDirection = Direction.left
        elif oChangeDirection <= 0.60: #up
            snake.requestedDirection = Direction.up
        elif oChangeDirection <= 0.80: #right
            snake.requestedDirection = Direction.right
        elif oChangeDirection <= 1: #down
            snake.requestedDirection = Direction.down

    def compute(self, inputs):
        layerCount = len(self.weights)

        prevValues = inputs
        for i in range(0, layerCount):
            layer = self.weights[i]

            prevValues = self.activation(np.dot(prevValues, layer))
        
        return prevValues

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