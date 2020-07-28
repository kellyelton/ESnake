import logging
import numpy as np

from .. import Direction

class Dylan:
    viewRadius = 15
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        inputCount = (self.viewRadius * self.viewRadius) + 2
        layer2Count = 16
        outputCount = 1

        self.weights0 = np.random.uniform(-1,1,size = (inputCount, 16))
        self.weights1 = np.random.uniform(-1,1,size = (layer2Count, outputCount))

    def update(self, app, time, level, snake):
        if snake.direction == None:
            snake.direction = Direction.right

    def move(self, app, time, level, snake):
        direction = snake.direction.toVector()
        inputs = [
            direction[0],
            direction[1]
        ]

        startX = max(0, snake.segments[0][0] - self.viewRadius)
        startY = max(0, snake.segments[0][1] - self.viewRadius)

        for y in range(startY, startY + self.viewRadius):
            for x in range(startX, startX + self.viewRadius):
                inputs.append(self.getLevelContents(level, snake, x, y))

        #inputs = np.array(inputs)
        #inputs = np.array([1, 0])

        layer0 = self.activation(np.dot(inputs, self.weights0))
        outputs = self.activation(np.dot(layer0, self.weights1))

        oChangeDirection = outputs[0]

        self.logger.debug(oChangeDirection)

        if oChangeDirection > 0.75: #right
            snake.direction = snake.direction.relativeRight
        elif oChangeDirection < 0.25: #left
            snake.direction = snake.direction.relativeLeft

    def getLevelContents(self, level, snake, x, y):
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