import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake


class Dylan:
    viewRadius = 5
    net = None

    def __init__(self, parent=None):
        self.logger = logging.getLogger(__name__)

        inputCount = ((self.viewRadius*2)**2)+(self.viewRadius * 4)+1
        inputCount += 3  # direction and energy
        outputCount = 6

        if parent is None:
            self.net = Net(inputCount, outputCount)
        else:
            self.net = self.mutate(parent.net)

    def mutate(self, srcNet):
        def clamp(num, min, max):
            if num > max:
                return max
            elif num < min:
                return min
            else:
                return num

        adjMax = random.random()  # maximum deviation per weight

        srcLayerCount = len(srcNet.layers)

        nlayers = []
        prevSrcLayer = None
        prevNewLayer = None
        for i in range(0, srcLayerCount):
            srcLayer = srcNet.layers[i]

            nNeurons = []
            for srcNeuron in srcLayer.neurons:
                adjustment = random.uniform(-adjMax, adjMax)
                activation = srcNeuron.activation
                activation = activation + adjustment
                activation = clamp(activation, 0, 1)
                nNeuron = Neuron(activation)
                nNeurons.append(nNeuron)

            if prevSrcLayer is not None:
                for i in range(0, len(prevSrcLayer.neurons)):
                    srcNeuron = prevSrcLayer.neurons[i]
                    ni = 0
                    for srcSynapse in srcNeuron.synapses:
                        adjustment = random.uniform(-adjMax, adjMax)
                        weight = srcSynapse.weight
                        weight = weight + adjustment
                        weight = clamp(weight, -1, 1)
                        nSynapse = Synapse(weight, nNeurons[ni])
                        prevNewLayer.neurons[i].synapses.append(nSynapse)
                        ni = ni + 1

            nLayer = Layer(nNeurons)
            prevNewLayer = nLayer

            prevSrcLayer = srcLayer
            nlayers.append(nLayer)

        newnet = Net(srcNet.inputs, srcNet.outputs, nlayers)
        return newnet

    def update(self, app, time, level, snake):
        pass

    def move(self, app, time, level, snake):
        mov = 0
        dir = 0
        if snake.direction == Direction.left:
            mov = 1
            dir = 0.15
        elif snake.direction == Direction.up:
            mov = 1
            dir = 0.35
        elif snake.direction == Direction.right:
            mov = 1
            dir = 0.65
        elif snake.direction == Direction.down:
            mov = 1
            dir = 0.85

        inputs = [
            mov,
            dir,
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

        oDoMove = outputs[0]
        oDirection = outputs[1]

        if oDoMove < 0.5:
            snake.requestedDirection = None
        elif oDirection <= 0.25:  # left
            snake.requestedDirection = Direction.left
        elif oDirection <= 0.50:  # up
            snake.requestedDirection = Direction.up
        elif oDirection <= 0.75:  # right
            snake.requestedDirection = Direction.right
        elif oDirection <= 1:  # down
            snake.requestedDirection = Direction.down

    def getLevelContents(self, level, snake, x, y):
        if level.isOutsideWall((x, y)):
            return 0.9

        contents = level.getContents((x, y))

        if contents is None:
            return 0
        elif contents is snake:
            return 1
        elif isinstance(contents, Food):
            return 0.60
        elif isinstance(contents, Snake):
            return 0.70
        elif contents is level.player:
            return 0.80
        elif isinstance(contents, Wall):
            return 0.90
        else:
            raise "invalid contents"

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
            else:
                return num

        adjustedSignal = self.adjust(signal)
        adjustedSignal = clamp(adjustedSignal)
        self.outputNeuron.accumulate(adjustedSignal)

    def adjust(self, signal):
        adjustment = self.weight

        adjustedSignal = signal + (signal * adjustment)
        return adjustedSignal
        # return 1 / (1 + exp(-signal))


class Neuron:
    def __init__(self, activation=None):
        self.activation = activation
        self.synapses = []
        if activation is None:
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

    def process(self):
        synapseCount = len(self.synapses)
        if synapseCount == 0:
            return

        if self.accumulatedSignal < self.activation:
            self.activation = min(1, self.activation + 0.001)
            return

        self.activation = max(0, self.activation - 0.002)

        splitSignal = self.accumulatedSignal / synapseCount

        for synapse in self.synapses:
            synapse.stimulate(splitSignal)


class Layer:
    def __init__(self, neurons):
        self.neurons = list(neurons)
        self.size = len(self.neurons)

    def accumulate(self, inputs):
        i = 0

        for signal in inputs:
            if i == self.size:
                break

            self.neurons[i].accumulate(signal)

            i = i + 1

    def process(self):
        for i in range(0, self.size):
            self.neurons[i].process()

    @staticmethod
    def random(size):
        neurons = [Neuron() for i in range(0, size)]
        return Layer(neurons)


class Net:
    def __init__(self, inputs, outputs, layers=None):
        self.inputs = inputs
        self.outputs = outputs
        if layers is None:
            self.layers = self.randomLayers(inputs, outputs)
        else:
            self.layers = layers

    def randomLayers(self, inputs, outputs):
        config = []

        prevLayer = None
        layerCount = 4  # int(random.random() * 10) + 1
        for i in range(0, layerCount):
            layer = None
            if i == 0:
                layerSize = inputs
                layer = Layer.random(layerSize)
                for neuron in layer.neurons:
                    neuron.activation = 0

            elif i == layerCount - 1:
                layerSize = outputs
                layer = Layer.random(layerSize)
            else:
                layerSize = int(random.random() * 16) + 8
                layer = Layer.random(layerSize)

            if prevLayer is not None:
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
