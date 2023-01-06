import typing as t

import pygame
from pygame.surface import Surface
from pygame.sprite import Group

from globals import context
from sprites.wall import Wall
from local_typing import Point, Curve


class Track:
    def __init__(self, central_curve: Curve, inner_curve: Curve, outer_curve: Curve, start_point: Point):
        self.central_curve = central_curve
        self.inner_curve = inner_curve
        self.outer_curve = outer_curve
        self.start_point = start_point

    def generate_walls(self, group: Group, closed: bool = False) -> t.List[Wall]:
        walls = []
        inner_walls = self.__curve_to_sprites(self.inner_curve, group)
        outer_walls = self.__curve_to_sprites(self.outer_curve, group)
        if closed:
            additional_walls = [
                Wall(group, self.inner_curve[0], self.inner_curve[-1]),
                Wall(group, self.outer_curve[0], self.outer_curve[-1])
            ]
        else:
            additional_walls = [
                Wall(group, self.inner_curve[0], self.outer_curve[0]),
                Wall(group, self.inner_curve[-1], self.outer_curve[-1])
            ]

        walls.extend(inner_walls)
        walls.extend(outer_walls)
        walls.extend(additional_walls)

        return walls

    @staticmethod
    def __curve_to_sprites(curve: Curve, group: Group) -> t.List[Wall]:
        """Converts curve to array of Wall sprites"""
        walls = []
        for index in range(len(curve) - 1):
            start = curve[index]
            end = curve[index + 1]
            walls.append(Wall(group, start, end))

        return walls

    @staticmethod
    def __draw_curve(curve: Curve, color: pygame.Color, surface: Surface) -> None:
        """Draws closed curve with certain color"""
        pygame.draw.lines(surface, color, True, curve, 6)

    def __fill_road(self, color: pygame.Color, surface: Surface) -> None:
        """Fills polygon with certain color"""
        pygame.draw.polygon(surface, color, self.outer_curve)
        pygame.draw.polygon(surface, pygame.Color(0, 0, 0), self.inner_curve)

    def render_preview(self, surface: Surface, scale: int) -> None:
        """Renders preview of track"""
        self.__draw_curve(self.inner_curve, context['theme'].WALL_COLOR, surface)
        self.__draw_curve(self.outer_curve, context['theme'].WALL_COLOR, surface)
        pygame.draw.circle(surface, context['theme'].AI_CAR_COLOR, self.start_point, 50 * (1 / scale))
