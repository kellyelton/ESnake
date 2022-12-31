import logging
import random
import numpy as np

from .. import Direction, Food, Wall, Snake


class Dylan:
    net = None

    def __init__(self, parent=None, mutate=True):
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
                self.color = (parent.color[0] + random.randint(-5, 5), parent.color[1] + random.randint(-5, 5), parent.color[2] + random.randint(-5, 5))
                # make sure no color value is less than 30 or greater than 200
                self.color = (max(30, min(200, self.color[0])), max(30, min(200, self.color[1])), max(30, min(200, self.color[2])))
            else:
                self.net = parent.net.clone()
                self.color = parent.color

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
        # Build an array of inputs
        # The inputs are the following:
        # 1. Contents of the tile directly in front of the snake
        # 2. Contents of the tile directly to the left of the snake
        # 3. Contents of the tile directly to the right of the snake
        # The coordinates are relative to the snake's head and the direction it's moving

        snake_head_location = snake.segments[0].location

        if snake.viewLocationsCount != self.net.num_inputs:
            raise "Number of view locations does not match number of inputs"

        inputs = []
        for i in range(0, snake.viewLocationsCount):
            contents = snake.viewContents[i]
            inputs.append(self.getLevelContents(level, snake, contents))

        outputs = self.net.process(inputs)

        # All outputs should be between 0 and 1
        for output in outputs:
            if output < 0 or output > 1:
                raise "Output is not between 0 and 1"

        # if the first output is greater than 0.8, then the snake should turn left
        # if the second output is greater than 0.8, then the snake should turn right
        # if both are greater than 0.8, then the snake should not turn
        # if both are equal, then the snake should not turn
        
        if outputs[0] > 0.8 and outputs[1] > 0.8:
            snake.requestedDirection = None
        elif outputs[0] > 0.8:
            snake.requestedDirection = Direction.left
        elif outputs[1] > 0.8:
            snake.requestedDirection = Direction.right
        else:
            snake.requestedDirection = None

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
            raise "invalid contents"

class NeuronV2:
    def __init__(self, num_inputs, activation_fn=None):
        self.num_inputs = num_inputs
        self.weights = np.random.uniform(size=num_inputs)
        self.bias = np.random.uniform()
        if activation_fn is None:
            self.activation_fn = self.sigmoid
        else:
            self.activation_fn = activation_fn

    def forward(self, inputs):
        weighted_inputs = self.weights * inputs
        weighted_sum = np.sum(weighted_inputs) + self.bias
        return self.activation_fn(weighted_sum)
    
    def clone(self):
        clone = NeuronV2(self.num_inputs, self.activation_fn)
        clone.weights = np.copy(self.weights)
        clone.bias = self.bias
        return clone

    # static function to return a random activation function
    @staticmethod
    def random_activation_function():
        return random.choice([
            NeuronV2.sigmoid,
            NeuronV2.relu,
            NeuronV2.tanh,
            #NeuronV2.leaky_relu,
            #NeuronV2.softmax,
            #NeuronV2.linear,
            NeuronV2.step,
            #NeuronV2.gaussian,
            #NeuronV2.identity,
            #NeuronV2.binary_step,
            #NeuronV2.absolute,
            #NeuronV2.hard_sigmoid,
            #NeuronV2.exponential,
            NeuronV2.inverse,
            #NeuronV2.sine,
            #NeuronV2.cosine,
            #NeuronV2.arctan,
            #NeuronV2.softsign,
            #NeuronV2.bent_identity,
            #NeuronV2.softplus,
            #NeuronV2.sinc,
            #NeuronV2.gaussian_error,
            #NeuronV2.exponential_linear_unit,
            #NeuronV2.scaled_exponential_linear_unit,
            #NeuronV2.logarithm,
            #NeuronV2.square,
            #NeuronV2.cube,
            #NeuronV2.square_root
            #NeuronV2.cube_root,
            #NeuronV2.exponential,
            #NeuronV2.logarithm,
            #NeuronV2.logarithm_base_10,
            #NeuronV2.logarithm_base_2
        ])

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
    
    @staticmethod
    def relu(x):
        return max(0, x)

    @staticmethod
    def tanh(x):
        return np.tanh(x)
    
    @staticmethod
    def leaky_relu(x):
        return max(0.01 * x, x)
    
    @staticmethod
    def softmax(x):
        return np.exp(x) / np.sum(np.exp(x))

    @staticmethod
    def linear(x):
        return x

    @staticmethod    
    def step(x):
        return 1 if x > 0 else 0

    @staticmethod
    def gaussian(x):
        return np.exp(-x ** 2)
    
    @staticmethod
    def identity(x):
        return x
    
    @staticmethod
    def binary_step(x):
        return 1 if x >= 0 else 0
    
    @staticmethod
    def absolute(x):
        return abs(x)
    
    @staticmethod
    def hard_sigmoid(x):
        return max(0, min(1, 0.2 * x + 0.5))
    
    @staticmethod
    def inverse(x):
        return 1 / x
    
    @staticmethod
    def sine(x):
        return np.sin(x)
    
    @staticmethod
    def cosine(x):
        return np.cos(x)
    
    @staticmethod
    def arctan(x):
        return np.arctan(x)
    
    @staticmethod
    def softsign(x):
        return x / (1 + abs(x))
    
    @staticmethod
    def bent_identity(x):
        return (np.sqrt(x ** 2 + 1) - 1) / 2 + x
    
    @staticmethod
    def softplus(x):
        return np.log(1 + np.exp(x))
    
    @staticmethod
    def sinc(x):
        return np.sin(x) / x
    
    @staticmethod
    def gaussian_error(x):
        return np.exp(-x ** 2) / 2
    
    @staticmethod
    def exponential_linear_unit(x):
        return x if x > 0 else np.exp(x) - 1
    
    @staticmethod
    def logarithmic(x):
        return np.log(1 + np.exp(x))
    
    @staticmethod
    def square(x):
        return x ** 2
    
    @staticmethod
    def cube(x):
        return x ** 3

    @staticmethod
    def scaled_exponential_linear_unit(x):
        return x if x > 0 else 0.01 * (np.exp(x) - 1)
    
    @staticmethod
    def square_root(x):
        return np.sqrt(abs(x))
    
    @staticmethod
    def cube_root(x):
        return np.sign(x) * np.abs(x) ** (1 / 3)
    
    @staticmethod
    def exponential(x):
        return np.exp(x)
    
    @staticmethod
    def logarithm(x):
        return np.log(abs(x))
    
    @staticmethod
    def logarithm_base_10(x):
        return np.log10(abs(x))
    
    @staticmethod
    def logarithm_base_2(x):
        return np.log2(abs(x))

class LayerV2:
    def __init__(self, num_neurons, num_inputs_per_neuron, activation_fn=None):
        self.num_neurons = num_neurons
        self.neurons = []
        self.size = num_neurons
        self.num_inputs_per_neuron = num_inputs_per_neuron
        if activation_fn is None:
            activation_fn = NeuronV2.random_activation_function()
        for i in range(num_neurons):
            neuron = NeuronV2(num_inputs_per_neuron, activation_fn)
            self.neurons.append(neuron)

    def forward(self, inputs):
        outputs = []
        for neuron in self.neurons:
            outputs.append(neuron.forward(inputs))
        return outputs
    
    def clone(self):
        cloned_layer = LayerV2(0, 0)

        cloned_layer.num_neurons = self.num_neurons
        cloned_layer.size = self.size
        cloned_layer.num_inputs_per_neuron = self.num_inputs_per_neuron

        for neuron in self.neurons:
            cloned_layer.neurons.append(neuron.clone())
        
        return cloned_layer

class NetV2:
    def __init__(self, num_inputs, num_outputs, hidden_layers=None):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        if hidden_layers is None:
            self.hidden_layers = self.randomLayers(num_inputs, num_outputs)
        else:
            self.hidden_layers = hidden_layers

    def randomLayers(self, inputs, outputs, min_layers=1, max_layers=20, min_neurons=1, max_neurons=20):
        config = []

        prevLayerSize = inputs
        layerCount = int(random.random() * (max_layers - min_layers)) + min_layers
        for i in range(0, layerCount):
            layer = None
            if i == layerCount - 1:
                layerSize = outputs
                layer = LayerV2(layerSize, prevLayerSize, NeuronV2.sigmoid)
            else:
                layerSize = int(random.random() * (max_neurons - min_neurons)) + min_neurons
                layer = LayerV2(layerSize, prevLayerSize)

            config.append(layer)
            prevLayerSize = layerSize

        return config

    def process(self, inputs):
        last_layer = None
        current_inputs = inputs
        for hidden_layer in self.hidden_layers:
            current_inputs = hidden_layer.forward(current_inputs)
            last_layer = hidden_layer

        # verify last later is sigmoid
        if last_layer is not None:
            for neuron in last_layer.neurons:
                if neuron.activation_fn != NeuronV2.sigmoid:
                    print("ERROR: Last layer is not sigmoid")
                    exit(1)

        return current_inputs
    
    def clone(self):
        # create copy of hidden layers
        new_hidden_layers = []
        for layer in self.hidden_layers:
            new_layer = layer.clone()
            new_hidden_layers.append(new_layer)
        
        new_net = NetV2(self.num_inputs, self.num_outputs, new_hidden_layers)

        return new_net

    def mutate(self):
        # Builds a new network with the following mutations:
        # 1% chance to add a new layer or remove an existing layer
        # 5% chance to add a new neuron to a layer or remove an existing neuron from a layer
        # 1% chance per each neuron to change the activation function
        # 1% chance to change the activation function of a layer
        # 5% chance per each neuron weight to change itself by 0.5% at most
        # 5% chance per each neuron to change the bias by 0.5% at most

        new_net = self.clone()

#        if random.random() < 0.01:
#            # Add or remove a layer
#            if random.random() < 0.5:
#                # Add a layer
#                new_net.hidden_layers.append(LayerV2(int(random.random() * 16) + 3, new_net.hidden_layers[-1].size))
#            else:
#                # Remove a layer
#                if len(new_net.hidden_layers) > 1:
#                    new_net.hidden_layers.pop()

        for layer in new_net.hidden_layers:
            #if random.random() < 0.05:
            #    # Add or remove a neuron
            #    if random.random() < 0.5:
            #        # Add a neuron
            #        layer.neurons.append(NeuronV2(layer.neurons[0].weights.size))
            #    else:
            #        # Remove a neuron
            #        if len(layer.neurons) > 1:
            #            layer.neurons.pop()

            # only change if not the last layer
            is_last_layer = layer == new_net.hidden_layers[-1]
            if random.random() < 0.01 and not is_last_layer:
                # Change the activation function of the layer
                layer.activation_fn = NeuronV2.random_activation_function()
                for neuron in layer.neurons:
                    neuron.activation_fn = layer.activation_fn

            for neuron in layer.neurons:
                if random.random() < 0.01 and not is_last_layer:
                    # Change the activation function
                    neuron.activation_fn = NeuronV2.random_activation_function()
                
                for i in range(neuron.weights.size):
                    if random.random() < 0.05:
                        # Change the weight
                        # increase or decrease by 0.5% of the existing value at most
                        neuron.weights[i] = neuron.weights[i] * (1 + random.random() * 0.005)

                if random.random() < 0.05:
                    # mutate the bias
                    # increase or decrease by 0.5% of the existing value at most
                    neuron.bias = neuron.bias * (1 + random.random() * 0.005)

        return new_net