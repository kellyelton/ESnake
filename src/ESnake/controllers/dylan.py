import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake


class Dylan:
    viewRadius = 5
    net = None

    def __init__(self, parent=None, mutate=True):
        self.logger = logging.getLogger(__name__)

        inputCount = ((self.viewRadius * 2) - 1)**2
        inputCount += 8  # direction, energy, hunger
        outputCount = 6

        if parent is None:
            self.net = Net(inputCount, outputCount)
        else:
            if mutate:
                self.net = self.mutate(parent.net)
            else:
                self.net = self.clone(parent.net)

    def mutate(self, srcNet):
        def clamp(num, min, max):
            if num > max:
                return max
            elif num < min:
                return min
            else:
                return num

        adjMax = random.uniform(0, 0.001)

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

    def clone(self, srcNet):
        srcLayerCount = len(srcNet.layers)

        nlayers = []
        prevSrcLayer = None
        prevNewLayer = None
        for i in range(0, srcLayerCount):
            srcLayer = srcNet.layers[i]

            nNeurons = []
            for srcNeuron in srcLayer.neurons:
                activation = srcNeuron.activation
                nNeuron = Neuron(activation)
                nNeurons.append(nNeuron)

            if prevSrcLayer is not None:
                for i in range(0, len(prevSrcLayer.neurons)):
                    srcNeuron = prevSrcLayer.neurons[i]
                    ni = 0
                    for srcSynapse in srcNeuron.synapses:
                        weight = srcSynapse.weight
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
        dirLeft = 0
        dirUp = 0
        dirRight = 0
        dirDown = 0
        if snake.direction == Direction.left:
            dirLeft = 1
        elif snake.direction == Direction.up:
            dirUp = 1
        elif snake.direction == Direction.right:
            dirRight = 1
        elif snake.direction == Direction.down:
            dirDown = 1

        inputs = [
            dirLeft,
            dirUp,
            dirRight,
            dirDown,
            random.randrange(-10, 10),
            snake.energy,
            random.randrange(-1, 1),
            snake.hunger
        ]

        center = snake.segments[0].location

        startX = center[0] - (self.viewRadius - 1)
        startY = center[1] - (self.viewRadius - 1)

        endX = center[0] + (self.viewRadius - 1)
        endY = center[1] + (self.viewRadius - 1)

        # TODO: Add stress (how many threats nearby)
        # probably goes down over time
        # TODO: Add hunger value, basically time since last ate
        # TODO: Add a few random inputs

        for y in range(startY, endY + 1):
            for x in range(startX, endX + 1):
                inputs.append(self.getLevelContents(level, snake, x, y))

        outputs = self.net.process(inputs)

        largestI = 0
        for i in range(0, 4):
            if outputs[largestI] < outputs[i]:
                largestI = i

        if largestI < 0.5:
            snake.requestedDirection = None
        elif largestI == 0:
            snake.requestedDirection = Direction.left
        elif largestI == 1:
            snake.requestedDirection = Direction.up
        elif largestI == 2:
            snake.requestedDirection = Direction.right
        elif largestI == 3:
            snake.requestedDirection = Direction.down
        else:
            raise "unexpected..."

    def getLevelContents(self, level, snake, x, y):
        contents = level.getContents((x, y))

        if contents is None:
            return 0
        elif contents is snake:
            return 1
        elif isinstance(contents, Food):
            return 100
        elif isinstance(contents, Snake):
            return 1000
        elif contents is level.player:
            return 10000
        elif isinstance(contents, Wall):
            return 0.5
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

        # Only allow a percentage of the signal through
        adjustedSignal = signal * self.weight
        adjustedSignal = clamp(adjustedSignal)
        self.outputNeuron.accumulate(adjustedSignal)


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
            randomWeight = random.uniform(0, 0.5)

            synapse = Synapse(randomWeight, neuron)

            self.synapses.append(synapse)

    def accumulate(self, signal):
        self.accumulatedSignal = self.accumulatedSignal + float(signal)

    def process(self):
        self.accumulatedSignal = 1 / (1 + np.exp(-self.accumulatedSignal))

        if self.accumulatedSignal < self.activation:
            # self.activation = min(1, self.activation + 0.001)
            return

        # self.activation = max(0, self.activation - 0.002)

        splitSignal = self.accumulatedSignal / len(self.synapses)

        for synapse in self.synapses:
            synapse.stimulate(splitSignal)


class Layer:
    def __init__(self, neurons):
        self.neurons = list(neurons)
        self.size = len(self.neurons)

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
        layerCount = int(random.random() * 10) + 2
        for i in range(0, layerCount):
            layer = None
            if i == 0:
                layerSize = inputs
                layer = Layer.random(layerSize)
            elif i == layerCount - 1:
                layerSize = outputs
                layer = Layer.random(layerSize)
            else:
                layerSize = int(random.random() * 16) + 3
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

        for i in range(0, len(inputs)):
            self.layers[0].neurons[i].accumulate(inputs[i])

        for layer in self.layers:
            layer.process()

        output = []
        for neuron in self.layers[-1].neurons:
            output.append(neuron.accumulatedSignal)

        return output
