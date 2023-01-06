import typing as t

from pygame.math import Vector2
from numpy import ndarray

Coordinate = t.Union[int, float]
Point = t.Union[t.Tuple[Coordinate, Coordinate], Vector2]
Curve = t.Union[t.List[Point], ndarray]

Radians = float
