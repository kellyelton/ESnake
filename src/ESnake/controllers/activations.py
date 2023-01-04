import numpy as np
import random

class Activations:
    # static function to return a random activation function
    @staticmethod
    def random_activation_function():
        return random.choice([
            Activations.sigmoid,
            Activations.relu,
            Activations.tanh,
            #NeuronV2.leaky_relu,
            #NeuronV2.softmax,
            #NeuronV2.linear,
            Activations.step,
            #NeuronV2.gaussian,
            #NeuronV2.identity,
            #NeuronV2.binary_step,
            #NeuronV2.absolute,
            #NeuronV2.hard_sigmoid,
            #NeuronV2.exponential,
            Activations.inverse,
            Activations.sine,
            Activations.cosine,
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