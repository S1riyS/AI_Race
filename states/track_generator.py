import typing as t
import math
import random

import pygame
import pygame_gui

from states.state import State
from states.race import Race
from sprites.track import Track
from utils.convex_hull import ConvexHull
from utils.bezier_curve import BezierCurve
from utils.math import angle_between_three_points, Radians
from utils.types import Point, Curve


class TrackGenerator(State):
    def __init__(self, app):
        super().__init__(app)
        self.track_width = 275
        self.scale_coefficient = 3
        self.number_of_random_points = 10
        self.interpolation_segments_number = 50
        self.min_segment_angle: Radians = math.pi / 2
        self.track = None

        self.local_width = app.config.WIDTH * self.scale_coefficient
        self.local_height = app.config.HEIGHT * self.scale_coefficient
        self.local_surface = pygame.surface.Surface((self.local_width, self.local_height))

        self.recreate_track_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (app.config.WIDTH - 170, app.config.HEIGHT - 50),
                (160, 40)
            ),
            text='Recreate track',
            manager=self.local_manager
        )

        self.start_race_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (app.config.WIDTH - 170, app.config.HEIGHT - 100),
                (160, 40)
            ),
            text='Start race',
            manager=self.local_manager
        )

        self.create_track()

    def generate_hull_points(self) -> Curve:
        """Creates array of points that lie on convex hull"""
        points = []
        for i in range(self.number_of_random_points):
            x = random.randint(self.local_width * 0.15, self.local_width * 0.85)
            y = random.randint(self.local_height * 0.15, self.local_height * 0.85)
            points.append((x, y))

        hull = ConvexHull(points)
        hull_points = hull.get_points()

        return hull_points

    def generate_bezier_curve_points(self, hull_points: Curve) -> t.Tuple[Curve, Point]:
        """Interpolates path of hull points through Bezier Curves"""
        bezier_curve = BezierCurve(points=hull_points, curve_points_number=self.interpolation_segments_number)
        bezier_curve_points = bezier_curve.get_points()
        start_point = bezier_curve_points[max(bezier_curve.curve_points_number // 10, 1)]

        return bezier_curve_points, start_point

    def filter_curve(self, curve: Curve) -> Curve:
        """Deletes all redundant points that create too sharp angles (less than `self.min_segment_angle`)"""
        flawless = False

        while flawless is not True:
            bad_angle_found = False
            for index in range(len(curve) - 2):
                p1 = curve[index]
                p2 = curve[index + 1]
                p3 = curve[index + 2]

                if angle_between_three_points(p1, p2, p3) < self.min_segment_angle:
                    del curve[index + 1]
                    break
            else:
                if not bad_angle_found:
                    flawless = True

        return curve

    def create_inner_and_outer_curves(self, central_curve: Curve) -> t.Tuple[Curve, Curve]:
        outer_curve_points = []
        inner_curve_points = []

        for index in range(len(central_curve) - 1):
            p1 = central_curve[index]
            p2 = central_curve[index + 1]

            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]

            alpha = math.atan2(dy, dx)
            beta = alpha - math.pi / 2

            outer_curve_points.append(
                (
                    p2[0] + (1 / self.scale_coefficient) * self.track_width * math.cos(beta),
                    p2[1] + (1 / self.scale_coefficient) * self.track_width * math.sin(beta)
                )
            )
            inner_curve_points.append(
                (
                    p2[0] - (1 / self.scale_coefficient) * self.track_width * math.cos(beta),
                    p2[1] - (1 / self.scale_coefficient) * self.track_width * math.sin(beta)
                )
            )

        inner_curve_points = self.filter_curve(inner_curve_points)
        outer_curve_points = self.filter_curve(outer_curve_points)
        return inner_curve_points, outer_curve_points

    def create_track(self) -> None:
        """Creates and displays new track"""
        self.local_surface.fill(pygame.Color(0, 0, 0))

        # Hull points
        hull_points = self.generate_hull_points()
        # Bezier interpolation
        central_curve, start_point = self.generate_bezier_curve_points(hull_points)
        # Inner and outer curves
        inner_curve, outer_curve = self.create_inner_and_outer_curves(central_curve)

        self.track = Track(
            central_curve=central_curve,
            inner_curve=inner_curve,
            outer_curve=outer_curve,
            start_point=start_point
        )
        self.track.render_preview(self.local_surface)

    def start_race(self) -> None:
        race = Race(self.app, self.track)
        race.enter_state()

    def handle_events(self, event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.recreate_track_button:
                self.create_track()
            elif event.ui_element == self.start_race_button:
                self.start_race()

    def update(self, dt):
        ...

    def render(self, surface):
        surface.blit(pygame.transform.scale(self.local_surface, self.app.config.WINDOW_SIZE), (0, 0))
