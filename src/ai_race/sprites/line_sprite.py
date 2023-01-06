import typing as t
from abc import ABC, abstractmethod

import pygame
from pygame.sprite import Sprite, Group

from local_typing import Point


class LineSprite(ABC, Sprite):
    """Basic class for all sprites based on line (pygame.draw.line)"""

    def __init__(self, camera: Group):
        super().__init__(camera)

        self.color: pygame.Color
        self.thickness: int
        self.offset = 2 * self.thickness

        self.start_position: Point
        self.end_position: Point
        self.line_start_position: Point
        self.line_end_position: Point
        self.mask: pygame.mask.Mask

        self.set_attributes()

    @abstractmethod
    def calculate_global_position(self) -> t.Tuple[Point, Point]:
        """Calculates start and end position of line on global surface"""
        ...

    def get_image(self, dx: int, dy: int) -> pygame.surface.Surface:
        """Returns pygame Surface based on lines attributes"""
        surface_width = max(abs(dx) + 2 * self.offset, self.thickness)
        surface_height = max(abs(dy) + 2 * self.offset, self.thickness)

        image = pygame.Surface((surface_width, surface_height))
        image.set_colorkey((0, 0, 0))

        return image

    def get_rect(self, dx: int, dy: int) -> pygame.rect.Rect:
        """Returns pygame Rect based on lines attributes"""
        rect = self.image.get_rect()
        rect.center = (self.start_position[0] + dx / 2, self.start_position[1] + dy / 2)

        return rect

    def get_line_coordinates(self, dx: int, dy: int) -> t.Tuple[Point, Point]:
        """Calculates position of the line on local surface (self.image)"""
        if dx * dy >= 0:
            line_start_position = (self.offset, self.offset)
            line_end_position = (abs(dx) + self.offset, abs(dy) + self.offset)
        else:
            line_start_position = (self.offset, abs(dy) + self.offset)
            line_end_position = (abs(dx) + self.offset, self.offset)

        return line_start_position, line_end_position

    def set_attributes(self) -> None:
        """Sets all calculated attributes for an instance of child class"""
        self.start_position, self.end_position = self.calculate_global_position()

        dx = self.end_position[0] - self.start_position[0]
        dy = self.end_position[1] - self.start_position[1]

        self.image = self.get_image(dx, dy)
        self.rect = self.get_rect(dx, dy)
        self.line_start_position, self.line_end_position = self.get_line_coordinates(dx, dy)

        self.mask = pygame.mask.from_surface(self.image)

    @abstractmethod
    def update(self) -> None:
        """Updates line sprite's data"""
