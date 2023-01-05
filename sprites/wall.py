import pygame

from local_typing import Coordinate


class Wall(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, start_position: Coordinate, end_position: Coordinate):
        super().__init__(group)
        self.start_position = start_position
        self.end_position = end_position

        self.color = pygame.Color(15, 52, 96)
        self.thickness = 15
        self.offset = 2 * self.thickness

        dx = self.end_position[0] - self.start_position[0]
        dy = self.end_position[1] - self.start_position[1]

        surface_width = max(abs(dx) + 2 * self.offset, self.thickness)
        surface_height = max(abs(dy) + 2 * self.offset, self.thickness)
        self.image = pygame.Surface((surface_width, surface_height))
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (start_position[0] + dx / 2, start_position[1] + dy / 2)

        if dx * dy >= 0:
            line_start_position = (self.offset, self.offset)
            line_end_position = (abs(dx) + self.offset, abs(dy) + self.offset)
        else:
            line_start_position = (self.offset, abs(dy) + self.offset)
            line_end_position = (abs(dx) + self.offset, self.offset)

        pygame.draw.line(self.image, self.color, line_start_position, line_end_position, self.thickness)

        self.mask = pygame.mask.from_surface(self.image)
