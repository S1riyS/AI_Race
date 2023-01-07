import typing as t

import numpy as np

from .layers import Layer


class NeuralNetwork:
    def __init__(self, layers_sequence: t.Sequence[Layer]):
        """
        First layer must contain number of units that equals to number of car's rays + car's velocity

        For example: each car has 6 rays, then initialization of neural network will look like this:

            neural_network = NeuralNetwork([
                Layer(units=7, activation='sigmoid (e.g.)'),
                ...
            ])
        :param layers_sequence: Sequence of Layer class instances
        """
        self.layers = layers_sequence
        self.weighted_layers = self.layers[:-1]
        self.__set_weights()

    def __set_weights(self) -> None:
        """Sets random weights to layers of neural network"""
        for index in range(len(self.layers) - 1):
            layer = self.layers[index]
            next_layer = self.layers[index + 1]

            layer.weights = np.random.normal(0.0, pow(layer.units, -0.5), (next_layer.units, layer.units))

    def query(self, inputs_list: t.Iterable[t.Any]) -> np.ndarray:
        """Returns answer of neural network"""
        inputs = np.array(inputs_list, ndmin=2).T

        current_array = inputs
        for index in range(len(self.layers) - 1):
            layer = self.layers[index]
            dot_product = np.dot(layer.weights, current_array)
            current_array = layer.activation_function(dot_product)

        return current_array

    def __repr__(self):
        strings_list = []
        for index, layer in enumerate(self.layers):
            strings_list.append(f'#{index + 1}: {layer}')

        return '\n'.join(strings_list)
