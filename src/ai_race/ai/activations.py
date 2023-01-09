import numpy as np


def _relu(x: np.ndarray) -> np.ndarray:
    """ReLu function"""
    return np.maximum(0, x)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    """Sigmoid function"""
    return 1 / (1 + np.exp(-x))


def _softmax(x: np.ndarray) -> np.ndarray:
    return np.exp(x - np.max(x)) / np.exp(x - np.max(x)).sum()


activation_functions = {
    'relu': _relu,
    'sigmoid': _sigmoid,
    'softmax': _softmax
}
