import typing as t
from random import randint, uniform

import numpy as np

from ai.neural_network.layers import Layer

if t.TYPE_CHECKING:
    from . import Individual

Shape = t.Tuple[int, ...]


def _check_compatibility(layer_a: Layer, layer_b: Layer) -> None:
    """
    Checks the compatibility of given layers

    :param layer_a: :class:`Layer` instance
    :param layer_b: :class:`Layer` instance

    :raises ValueError: If shapes of weights or biases are different
    """
    if layer_a.weights.shape != layer_b.weights.shape:
        raise ValueError(
            f'Layers\' weights must have the same shape. '
            f'{layer_a.weights.shape} != {layer_b.weights.shape}'
        )
    if layer_a.bias.shape != layer_b.bias.shape:
        raise ValueError(
            f'Layers\' biases must have the same shape. '
            f'{layer_a.bias.shape} != {layer_b.bias.shape}'
        )


def _process_weights(layer_a: Layer, layer_b: Layer) -> t.Tuple[Shape, np.ndarray, np.ndarray]:
    """
    Calculates original shape of weights of given layers, flattens weights

    :param layer_a: :class:`Layer` instance
    :param layer_b: :class:`Layer` instance
    :return: Original shape of weights, numpy array with flatten weights of given layers
    """
    original_shape = layer_a.weights.shape
    flatten_weights_a = layer_a.weights.flatten()
    flatten_weights_b = layer_b.weights.flatten()

    return original_shape, flatten_weights_a, flatten_weights_b


def _process_biases(layer_a: Layer, layer_b: Layer) -> t.Tuple[Shape, np.ndarray, np.ndarray]:
    """
    Calculates shape of bias, extracts biases

    :param layer_a: :class:`Layer` instance
    :param layer_b: :class:`Layer` instance
    :return: Shape of bias, numpy array with biases of given layers
    """

    shape = layer_a.bias.shape
    bias_a = layer_a.bias
    bias_b = layer_b.bias

    return shape, bias_a, bias_b


def single_point_crossover(a: "Individual", b: "Individual") -> t.Tuple["Individual", "Individual"]:
    """
    Single Point Crossover is a form of crossover in which two-parent chromosome are
    selected and a random point is selected and the data are
    interchanged between them after the selected point

    :param a: :class:`Individual` instance (father)
    :param b: :class:`Individual` instance (mother)
    :return: Two offsprings (:class:`Individual` instances)
    """
    for layer_a, layer_b in zip(a.neural_network.weighted_layers, b.neural_network.weighted_layers):
        _check_compatibility(layer_a, layer_b)

        # Crossing weights
        weights_shape, flatten_weights_a, flatten_weights_b = _process_weights(layer_a, layer_b)

        p = randint(1, len(flatten_weights_a) - 1)
        offspring_a_weights = np.concatenate([flatten_weights_a[:p], flatten_weights_b[p:]]).reshape(weights_shape)
        offspring_b_weights = np.concatenate([flatten_weights_b[:p], flatten_weights_a[p:]]).reshape(weights_shape)

        layer_a.weights = offspring_a_weights
        layer_b.weights = offspring_b_weights

        # Crossing biases
        bias_shape, bias_a, bias_b = _process_biases(layer_a, layer_b)

        k = randint(1, len(bias_a) - 1)
        offspring_a_bias = np.concatenate([bias_a[:k], bias_b[k:]])
        offspring_b_bias = np.concatenate([bias_b[:k], bias_a[k:]])

        layer_a.bias = offspring_a_bias
        layer_b.bias = offspring_b_bias

    return a, b


def uniform_crossover(a: "Individual", b: "Individual") -> t.Tuple["Individual", "Individual"]:
    """
    In uniform crossover each gen is chosen from either parent with equal probability.

    :param a: :class:`Individual` instance (father)
    :param b: :class:`Individual` instance (mother)
    :return: Two offsprings (:class:`Individual` instance
    """
    for layer_a, layer_b in zip(a.neural_network.weighted_layers, b.neural_network.weighted_layers):
        _check_compatibility(layer_a, layer_b)

        # Crossing weights
        weights_shape, flatten_weights_a, flatten_weights_b = _process_weights(layer_a, layer_b)

        offspring_a_weights = np.array([])
        offspring_b_weights = np.array([])

        for gen_a, gen_b in zip(flatten_weights_a, flatten_weights_b):
            if uniform(0, 1) <= 0.5:
                offspring_a_weights = np.append(offspring_a_weights, gen_b)
                offspring_b_weights = np.append(offspring_b_weights, gen_a)
            else:
                offspring_a_weights = np.append(offspring_a_weights, gen_a)
                offspring_b_weights = np.append(offspring_b_weights, gen_b)

        layer_a.weights = offspring_a_weights.reshape(weights_shape)
        layer_b.weights = offspring_b_weights.reshape(weights_shape)

        # Crossing biases
        bias_shape, bias_a, bias_b = _process_biases(layer_a, layer_b)

        offspring_a_bias = np.array([])
        offspring_b_bias = np.array([])

        for bias_a_unit, bias_b_unit in zip(bias_a, bias_b):
            if uniform(0, 1) <= 0.5:
                offspring_a_bias = np.append(offspring_a_bias, bias_b_unit)
                offspring_b_bias = np.append(offspring_b_bias, bias_a_unit)
            else:
                offspring_a_bias = np.append(offspring_a_bias, bias_a_unit)
                offspring_b_bias = np.append(offspring_b_bias, bias_b_unit)

        layer_a.bias = offspring_a_bias.reshape(bias_shape)
        layer_b.bias = offspring_b_bias.reshape(bias_shape)

    return a, b
