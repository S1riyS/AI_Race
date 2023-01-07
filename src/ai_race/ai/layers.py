import typing as t
from abc import ABC

import numpy as np

from .activations import activation_functions


class BaseLayer(ABC):
    def _repr(self, fields: t.Mapping[str, t.Any]) -> str:
        field_strings = []
        for key, field in fields.items():
            field_strings.append(f'{key}={field!r}')

        return f"<{self.__class__.__name__}({','.join(field_strings)})>"


class Layer(BaseLayer):
    """Dense layer of neural network"""

    def __init__(self, units: int, activation: t.Optional[str] = None):
        """
        :param units: Number of neurons
        :param activation: Name of activation function
        """
        self.units = units
        self.activation_function = activation_functions.get(activation, None)

        self.weights: t.Optional[np.ndarray] = None

    def __repr__(self):
        return self._repr({
            'units': self.units,
            'activation function': getattr(self.activation_function, '__name__', 'Undefined'),
            'weights': getattr(self, 'weights', 'Undefined')
        })
