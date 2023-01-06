import pygame

from globals import context
from sprites.line_sprite import LineSprite
from local_typing import Point


class Wall(LineSprite):
    def __init__(self, start_position: Point, end_position: Point, camera: pygame.sprite.Group):
        self.start_position = start_position
        self.end_position = end_position

        self.color = context['theme'].WALL_COLOR
        self.thickness = 15

        super().__init__(camera)
        pygame.draw.line(self.image, self.color, self.line_start_position, self.line_end_position, self.thickness)

    def calculate_global_position(self):
        return self.start_position, self.end_position

    def update(self) -> None:
        self.mask = pygame.mask.from_surface(self.image)
