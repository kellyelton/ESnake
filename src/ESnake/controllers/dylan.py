import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake

class Dylan:
    viewRadius = 5
    net = None
    def __init__(self, parent = None):
        self.logger = logging.getLogger(__name__)

        inputCount = ((self.viewRadius*2)**2)+(self.viewRadius * 4)+1
        inputCount += 3 #direction and energy
        outputCount = 6

        self.net = Net(inputCount, outputCount)
        
    def mutatedWeightsFromParent(self, parent):
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

                        adjustment = random.uniform(-adjustmentMax, adjustmentMax)

                        activation = parent.weights[i][sourceIndex][targetIndex][1]
                        activation = activation + adjustment;
                        activation = clamp(activation)

                        layer[sourceIndex][targetIndex] = [newWeight, activation]

                yield layer

    def update(self, app, time, level, snake):
        pass

    def move(self, app, time, level, snake):
        if snake.direction != None:
            direction = snake.direction.toVector()
        else:
            direction = (0, 0)

        inputs = [
            ((direction[0] + 1) / 2),
            ((direction[1] + 1) / 2),
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

        outputs = self.net.process(inputs)

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

    def getLevelContents(self, level, snake, x, y):
        if level.isOutsideWall((x, y)):
            return 0.2

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

class Synapse:
    def __init__(self, weight, outputNeuron):
        self.weight = weight
        self.outputNeuron = outputNeuron
    
    def stimulate(self, signal):
        def clamp(num):
            if num > 1:
                return 1
            elif num < 0:
                return 0
            else: return num

        adjustedSignal = self.adjust(signal)
        adjustedSignal = clamp(adjustedSignal)
        self.outputNeuron.accumulate(adjustedSignal)

    def adjust(self, signal):
        adjustment = self.weight 

        adjustedSignal = signal + (signal * adjustment)
        return adjustedSignal
        #return 1 / (1 + exp(-signal))

class Neuron:
    def __init__(self, activation = None):
        self.activation = activation
        self.synapses = []
        if activation == None:
            self.activation = random.uniform(0, 1)

        self.accumulatedSignal = float(0)
    
    def attach(self, layer):
        for neuron in layer.neurons:
            # maxWeight = 1 / layer.size
            randomWeight = random.uniform(-1, 1)

            synapse = Synapse(randomWeight, neuron)
            self.synapses.append(synapse)
    
    def accumulate(self, signal):
        s = float(min(1, self.accumulatedSignal + signal))
        self.accumulatedSignal = s
        asdf = self.accumulatedSignal

    def process(self):
        synapseCount = len(self.synapses)
        if synapseCount == 0: return

        if self.accumulatedSignal < self.activation:
            self.activation = min(1, self.activation + 0.01)
            return

        self.activation = max(0, self.activation - 0.01)
        
        splitSignal = self.accumulatedSignal / synapseCount

        for synapse in self.synapses:
            synapse.stimulate(splitSignal)

class Layer:
    def __init__(self, size):
        self.size = size
        self.neurons = [Neuron() for i in range(0, size)]
    
    def accumulate(self, inputs):
        i = 0

        for signal in inputs:
            if i == self.size: break

            self.neurons[i].accumulate(signal)

            i = i + 1

    def process(self):
        for i in range(0, self.size):
            self.neurons[i].process()

class Net:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.layers = self.randomLayers(inputs, outputs)
    
    def randomLayers(self, inputs, outputs):
        config = []

        prevLayer = None
        layerCount = int(random.random() * 10) + 1
        for i in range(0, layerCount):
            layer = None
            if i == 0:
                layerSize = inputs
                layer = Layer(layerSize)
                for neuron in layer.neurons:
                    neuron.activation = 0

            elif i == layerCount - 1:
                layerSize = outputs
                layer = Layer(layerSize)
            else:
                layerSize = int(random.random() * 24) + 1
                layer = Layer(layerSize)

            if not prevLayer == None:
                for neuron in prevLayer.neurons:
                    neuron.attach(layer)

            config.append(layer)
            prevLayer = layer

        return config
    
    def process(self, inputs):
        for layer in self.layers:
            for neuron in layer.neurons:
                neuron.accumulatedSignal = 0

        self.layers[0].accumulate(inputs)

        for layer in self.layers:
            layer.process()

        output = []
        for neuron in self.layers[-1].neurons:
            output.append(neuron.accumulatedSignal)

        return output