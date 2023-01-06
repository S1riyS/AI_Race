import typing as t
from math import sin, cos, radians, pi, hypot

import pygame
from pygame.math import Vector2

from sprites.line_sprite import LineSprite
from sprites.wall import Wall
from local_typing import Point, Radians

if t.TYPE_CHECKING:
    from sprites.car import AbstractCar


class Ray(LineSprite):
    def __init__(self, car: "AbstractCar", length: int, angle: Radians):
        self.car = car
        self.length = length
        self.angle = angle

        self.color = pygame.Color(200, 200, 200)
        self.thickness = 1

        super().__init__(self.car.camera)

    def calculate_global_position(self):
        direction = Vector2(
            cos(radians(self.car.rotation) + self.angle - pi / 2),
            -sin(radians(self.car.rotation) + self.angle - pi / 2)
        )
        start_position = self.car.positional_vector
        end_position = start_position + direction * self.length

        return start_position, end_position

    def cast(self, walls: t.Iterable[Wall]) -> t.Tuple[t.Optional[Point], float]:
        """
        Casts ray in given walls
        :returns: Coordinates of nearest collision point and distance to this point
        """
        result_point = None
        result_distance = float('inf')

        for wall in walls:
            collision_point, distance = self.cast_to_singe_wall(wall)
            if collision_point and distance:
                if distance < result_distance:
                    result_point = collision_point
                    result_distance = distance

        return result_point, result_distance

    def cast_to_singe_wall(self, wall: Wall) -> t.Union[t.Tuple[None, None], t.Tuple[Point, float]]:
        """Casts ray in given wall"""
        # Get start and end points of the wall
        x1, y1 = wall.start_position
        x2, y2 = wall.end_position

        # Position of the ray
        x3, y3 = self.start_position
        x4, y4 = self.end_position

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        numerator = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        if denominator == 0:
            return None, None

        t = numerator / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if (t > 0) and (t < 1) and (u > 0):
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            distance = hypot(x - x3, y - y3)
            if distance <= self.length:
                coordinates = Vector2(x, y)
                return coordinates, distance

        return None, None

    def update(self) -> None:
        self.set_attributes()

    def draw(self):
        pygame.draw.line(self.image, self.color, self.line_start_position, self.line_end_position, self.thickness)
        self.mask = pygame.mask.from_surface(self.image)
