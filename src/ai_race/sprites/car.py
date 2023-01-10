import typing as t
from abc import ABC, abstractmethod
from math import sin, cos, radians, pi, hypot
from random import randint

import pygame
from pygame.math import Vector2

from globals import context
from ai.neural_network import NeuralNetwork
from sprites.ray import Ray
from sprites.wall import Wall
from local_typing import Point, Curve


class AbstractCar(ABC, pygame.sprite.Sprite):
    def __init__(self, start_position: Point, camera: pygame.sprite.Group):
        super().__init__(camera)
        self.x, self.y = start_position
        self.camera = camera

        # Size and color
        self.width = 60
        self.height = 30
        self.color: pygame.Color

        # Surface
        self.original_image = pygame.Surface((self.width, self.height))
        self.original_image.set_colorkey(pygame.Color(0, 0, 0))
        self.original_image.fill(self.color)
        self.image = self.original_image.copy()
        self.image.set_colorkey(pygame.Color(0, 0, 0))

        # Rect
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        # Position
        random_offset = Vector2(randint(-10, 10), randint(-10, 10))
        self.position = Vector2(self.x, self.y) + random_offset
        self.start_position = Vector2(self.x, self.y) + random_offset

        # Collision
        self.mask = pygame.mask.from_surface(self.image)
        self.destroyed = False

        # Movement
        self.rotation = randint(-10, 10)
        self.rotation_speed = 5
        self.velocity = 0
        self.max_velocity = 15
        self.acceleration = 0.3
        self.deceleration = 0.3

        # Rays
        self.rays = pygame.sprite.Group()
        self.ray_length = 300
        self.rays_number = 6
        self.view_angle = 2 * pi / 3
        self.__init_rays()

    def __init_rays(self) -> None:
        number = max(2, self.rays_number)
        for i in range(number):
            angle = (self.view_angle / (number - 1)) * i
            ray = Ray(
                car=self,
                length=self.ray_length,
                angle=angle,
            )
            self.rays.add(ray)

    def draw_rays(self) -> None:
        for ray in self.rays:
            ray.draw()

    def get_nearest_walls(self, walls: t.Iterable[Wall]) -> t.Iterable[Wall]:
        nearest_walls = []
        for wall in walls:
            dx = wall.start_position[0] - self.position.x
            dy = wall.start_position[1] - self.position.y
            distance = hypot(dx, dy)

            if distance <= self.ray_length * 1.5:
                nearest_walls.append(wall)

        return nearest_walls

    def kill(self) -> None:
        self.destroyed = True
        for ray in self.rays:
            ray.kill()
        super().kill()

    def rotate(self, dt: float, rotation_coefficient: float = 0) -> None:
        """
        Rotates car

        :param dt: Delta time
        :param rotation_power: Power of rotation (varies from -1 to 1)
        """
        self.rotation = (self.rotation + self.rotation_speed * rotation_coefficient * dt) % 360

        new_image = pygame.transform.rotate(self.original_image, self.rotation)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def move_forward(self, dt: float, engine_power: float = 1) -> None:
        self.velocity = min(self.velocity + self.acceleration * engine_power * dt, self.max_velocity)
        self._move(dt, engine_power)

    def move_backward(self, dt: float, engine_power: float = 1) -> None:
        self.velocity = max(self.velocity - self.acceleration * dt, -self.max_velocity / 2)
        self._move(dt, engine_power)

    def reduce_speed(self, dt: float) -> None:
        self.velocity = max(self.velocity - self.deceleration * dt, 0)
        self._move(dt, engine_power=1)

    def _move(self, dt: float, engine_power: float) -> None:
        """
        Moves car

        :param dt: Delta time
        :param engine_power: Power of engine (varies from 0 to 1)
        """
        velocity_vector = Vector2(
            self.velocity * cos(radians(self.rotation)),
            -self.velocity * sin(radians(self.rotation))
        )
        self.position += velocity_vector * engine_power * dt
        self.rect.center = self.position

    @abstractmethod
    def update(self, dt: float) -> None:
        """Updates car's data"""
        self.rays.update()
        self.mask = pygame.mask.from_surface(self.image)


class UserCar(AbstractCar):
    def __init__(self, start_position, camera):
        self.color = context['theme'].USER_CAR_COLOR
        super().__init__(start_position, camera)

    def update(self, dt) -> None:
        key = pygame.key.get_pressed()
        moved = False

        if key[pygame.K_DOWN]:
            moved = True
            self.move_backward(dt)
        elif key[pygame.K_UP]:
            moved = True
            self.move_forward(dt)
        if key[pygame.K_RIGHT]:
            self.rotate(dt, rotation_power=-1)
        elif key[pygame.K_LEFT]:
            self.rotate(dt, rotation_power=1)

        if not moved:
            self.reduce_speed(dt)

        super().update(dt)


class AICar(AbstractCar):
    def __init__(self, start_position: Point, neural_network: NeuralNetwork, camera):
        self.color = context['theme'].AI_CAR_COLOR
        self.neural_network = neural_network

        super().__init__(start_position, camera)

    @staticmethod
    def __calculate_path_length_to_point_on_curve(point: Point, curve: Curve) -> float:
        min_distance = float('inf')
        closest_index = None

        # Calculating index of point on curve that is the closest to given point
        for index, curve_point in enumerate(curve):
            dx = curve_point[0] - point[0]
            dy = curve_point[1] - point[1]
            distance = hypot(dx, dy)

            if distance <= min_distance:
                min_distance = distance
                closest_index = index

        # Calculating path length from the first point on curve to the point before closest to given
        path_length = 0.0
        for i in range(closest_index - 1):
            current_point = curve[i]
            next_point = curve[i + 1]
            dx = next_point[0] - current_point[0]
            dy = next_point[1] - current_point[1]
            path_length += hypot(dx, dy)

        return path_length

    def evaluate(self, curve: Curve) -> float:
        """
        Evaluates car's results based on its position relative to given curve.
        Formula: (path_on_curve / 50) ^ 2

        :param curve: Curve to evaluation
        :return: Fitness coefficient
        """
        path_length_to_start_position = self.__calculate_path_length_to_point_on_curve(self.start_position, curve)
        path_length_to_current_position = self.__calculate_path_length_to_point_on_curve(self.position, curve)

        path_length = path_length_to_current_position - path_length_to_start_position

        if path_length < 0:
            return 0.0

        return (path_length / 50) ** 2

    def __get_neural_network_inputs(self) -> t.List[float]:
        inputs = []
        for ray in self.rays:
            inputs.append(ray.current_distance / ray.length)

        inputs.append(self.velocity / self.max_velocity)

        return inputs

    def update(self, dt) -> None:
        inputs_list = self.__get_neural_network_inputs()
        answer = self.neural_network.query(inputs_list)

        move_forward = answer[0][0]
        move_backward = answer[1][0]
        rotate_left = answer[2][0]
        rotate_right = answer[3][0]

        moved = False

        if move_forward > 0.5:
            moved = True
            self.move_forward(dt)
        elif move_backward > 0.5:
            moved = True
            self.move_backward(dt)

        if rotate_left > 0.5:
            self.rotate(dt, rotation_coefficient=1)
        elif rotate_right > 0.5:
            self.rotate(dt, rotation_coefficient=-1)

        if not moved:
            self.reduce_speed(dt)

        super().update(dt)


CarClass = t.Union[UserCar, AICar]
