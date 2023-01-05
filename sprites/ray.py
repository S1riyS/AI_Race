import typing as t
from math import sin, cos, radians, pi

import pygame
from pygame.sprite import Group
from pygame.math import Vector2

from sprites.line_sprite import LineSprite
from local_typing import Radians

if t.TYPE_CHECKING:
    from sprites.car import AbstractCar


class Ray(LineSprite):
    def __init__(
            self,
            car: "AbstractCar",
            length: int,
            angle: Radians,
            collision_groups: t.Iterable[Group],
            group: Group
    ):
        self.object_ = car
        self.length = length
        self.angle = angle
        self.collision_groups = collision_groups

        self.color = pygame.Color(255, 255, 255)
        self.thickness = 2

        super().__init__(group)

    def calculate_global_position(self):
        direction = Vector2(
            cos(radians(self.object_.rotation) + self.angle - pi / 2),
            -sin(radians(self.object_.rotation) + self.angle - pi / 2)
        )
        start_position = self.object_.positional_vector
        end_position = start_position + direction * self.length

        return start_position, end_position

    def update(self) -> None:
        self.set_attributes()

    def draw(self):
        pygame.draw.line(self.image, self.color, self.line_start_position, self.line_end_position, self.thickness)
