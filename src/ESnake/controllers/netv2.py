import random
import numpy as np

from . import Activations

class NeuronV2:
    def __init__(self, num_inputs, activation_fn=None):
        self.num_inputs = num_inputs
        self.weights = np.random.uniform(-1, 1, num_inputs)
        self.bias = np.random.uniform(-1, 1)
        if activation_fn is None:
            self.activation_fn = Activations.sigmoid
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

class LayerV2:
    def __init__(self, num_neurons, num_inputs_per_neuron, activation_fn=None):
        self.num_neurons = num_neurons
        self.neurons = []
        self.size = num_neurons
        self.num_inputs_per_neuron = num_inputs_per_neuron
        if activation_fn is None:
            activation_fn = Activations.random_activation_function()
        
        self.activation_fn = activation_fn

        for i in range(num_neurons):
            neuron = NeuronV2(num_inputs_per_neuron, self.activation_fn)
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

    def randomLayers(self, inputs, outputs, min_layers=1, max_layers=6, min_neurons=1, max_neurons=12):
        config = []

        prevLayerSize = inputs
        layerCount = int(random.random() * (max_layers - min_layers)) + min_layers
        for i in range(0, layerCount):
            layer = None
            if i == layerCount - 1:
                layerSize = outputs
                layer = LayerV2(layerSize, prevLayerSize, Activations.sigmoid)
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
                if neuron.activation_fn != Activations.sigmoid:
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
            # Don't add or remove neurons from the last layer
            if random.random() < 0.05 and new_net.hidden_layers.index(layer) != len(new_net.hidden_layers) - 1:
                print("\a", end="", flush=True)
                print("\a", end="", flush=True)
                print("\a", end="", flush=True)
                print("\a", end="", flush=True)

                # Add or remove a neuron
                if random.random() < 0.5:
                    # Add a neuron at a random index
                    new_neuron = NeuronV2(layer.num_inputs_per_neuron)
                    new_index = random.randint(0, len(layer.neurons))
                    layer.neurons.insert(new_index, new_neuron)
                    
                    # update the next layer's input size and weights
                    next_layer_index = new_net.hidden_layers.index(layer) + 1
                    if next_layer_index < len(new_net.hidden_layers):
                        next_layer = new_net.hidden_layers[next_layer_index]
                        next_layer.num_inputs_per_neuron += 1
                        for neuron in next_layer.neurons:
                            neuron.weights = np.insert(neuron.weights, new_index, 0)
                else:
                    # Remove a random neuron from the layer
                    if len(layer.neurons) > 1:
                        removed_index = random.randint(0, len(layer.neurons) - 1)
                        layer.neurons.pop(removed_index)

                        # update the next layer's input size and weights
                        next_layer_index = new_net.hidden_layers.index(layer) + 1
                        if next_layer_index < len(new_net.hidden_layers):
                            next_layer = new_net.hidden_layers[next_layer_index]
                            next_layer.num_inputs_per_neuron -= 1
                            for neuron in next_layer.neurons:
                                neuron.weights = np.delete(neuron.weights, removed_index)

            # only change if not the last layer
            is_last_layer = layer == new_net.hidden_layers[-1]
            if random.random() < 0.005 and not is_last_layer:
                # Change the activation function of the layer
                layer.activation_fn = Activations.random_activation_function()
                for neuron in layer.neurons:
                    neuron.activation_fn = layer.activation_fn

            for neuron in layer.neurons:
                if random.random() < 0.005 and not is_last_layer:
                    # Change the activation function
                    neuron.activation_fn = Activations.random_activation_function()
                
                for i in range(neuron.weights.size):
                    if random.random() < 0.05:
                        # Change the weight
                        # increase or decrease by 0.5% of the existing value at most
                        neuron.weights[i] = neuron.weights[i] * (1 + random.random() * 0.0005)

                        # weight can be between -1 and 1
                        if neuron.weights[i] > 1:
                            neuron.weights[i] = 1
                        elif neuron.weights[i] < -1:
                            neuron.weights[i] = -1

                if random.random() < 0.05:
                    # mutate the bias
                    # increase or decrease by 0.5% of the existing value at most
                    neuron.bias = neuron.bias * (1 + random.random() * 0.0005)

                    # bias can be between -1 and 1
                    if neuron.bias > 1:
                        neuron.bias = 1
                    elif neuron.bias < -1:
                        neuron.bias = -1

        return new_net