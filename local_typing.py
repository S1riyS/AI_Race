import typing as t

from numpy import ndarray

Coordinate = t.Union[int, float]
Point = t.Tuple[Coordinate, Coordinate]
Curve = t.Union[t.List[Point], ndarray]

Radians = float
