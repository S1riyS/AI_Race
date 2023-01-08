import typing as t
from abc import ABC, abstractmethod
from math import sin, cos, radians, pi, hypot
from random import randint

import pygame
from pygame.math import Vector2

from globals import context
from ai import NeuralNetwork
from sprites.ray import Ray
from sprites.wall import Wall
from local_typing import Point, Curve


class AbstractCar(ABC, pygame.sprite.Sprite):
    def __init__(self, start_position: Point, camera: pygame.sprite.Group):
        super().__init__(camera)
        self.x, self.y = start_position

        self.width = 60
        self.height = 30
        self.color: pygame.Color

        self.original_image = pygame.Surface((self.width, self.height))
        self.original_image.set_colorkey(pygame.Color(0, 0, 0))
        self.original_image.fill(self.color)

        self.image = self.original_image.copy()
        self.image.set_colorkey(pygame.Color(0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        random_offset = Vector2(randint(-10, 10), randint(-10, 10))
        self.position = Vector2(self.x, self.y) + random_offset
        self.start_position = Vector2(self.x, self.y) + random_offset
        self.destroyed = False

        self.mask = pygame.mask.from_surface(self.image)

        self.rotation = 0
        self.rotation_speed = 4

        self.velocity = 0
        self.max_velocity = 15
        self.acceleration = 0.2
        self.deceleration = 0.1

        self.camera = camera
        self.rays = pygame.sprite.Group()
        self.init_rays(number=9)

    def init_rays(self, number: int):
        number = max(2, number)
        for i in range(number):
            angle = (pi / (number - 1)) * i
            ray = Ray(
                car=self,
                length=250,
                angle=angle,
            )
            self.rays.add(ray)

    def draw_rays(self):
        for ray in self.rays:
            ray.draw()

    def get_nearest_walls(self, walls: t.Iterable[Wall]) -> t.Iterable[Wall]:
        nearest_walls = []
        for wall in walls:
            dx = wall.start_position[0] - self.position.x
            dy = wall.start_position[1] - self.position.y
            distance = hypot(dx, dy)

            if distance <= 900:
                nearest_walls.append(wall)

        return nearest_walls

    def evaluate(self, curve: Curve, lifetime: int) -> float:
        """
        Evaluates car's results based on its position relative to given curve

        :param curve: Curve to evaluation
        :param lifetime: time of car's life in milliseconds
        :return: Fitness coefficient
        """
        if hypot(self.position.x - self.start_position.x, self.position.y - self.start_position.y) <= 5:
            return 1.0

        fit = 0

        min_distance = float('inf')
        closest_index = None

        # Calculating index of point on curve that is the closest to current position of car
        for index, point in enumerate(curve):
            dx = point[0] - self.position[0]
            dy = point[1] - self.position[1]
            distance = hypot(dx, dy)
            if distance <= min_distance:
                min_distance = distance
                closest_index = index

        # Calculating path length from the first point on curve to the point before closest to current position of car
        path_length = 0
        for i in range(closest_index - 1):
            current_point = curve[i]
            next_point = curve[i + 1]
            dx = next_point[0] - current_point[0]
            dy = next_point[1] - current_point[1]
            path_length += hypot(dx, dy)

        # Calculating distance between the point before closest to current position of car to the position of car
        penultimate_closest_point = curve[closest_index - 1]
        path_length += hypot(penultimate_closest_point[0] - self.position[0],
                             penultimate_closest_point[1] - self.position[1])

        fit += path_length
        fit += (path_length / lifetime) * 75
        return fit

    def kill(self) -> None:
        self.destroyed = True
        for ray in self.rays:
            ray.kill()
        super().kill()

    def rotate(self, dt, rotation_power=0):
        self.rotation = (self.rotation + self.rotation_speed * rotation_power * dt) % 360

        new_image = pygame.transform.rotate(self.original_image, self.rotation)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def move_forward(self, dt: float, engine_power: float = 1):
        self.velocity = min(self.velocity + self.acceleration * engine_power * dt, self.max_velocity)
        self.move(dt, engine_power)

    def move_backward(self, dt: float):
        self.velocity = max(self.velocity - self.acceleration * dt, -self.max_velocity / 2)
        self.move(dt)

    def reduce_speed(self, dt: float):
        self.velocity = max(self.velocity - self.deceleration * dt, 0)
        self.move(dt)

    def move(self, dt: float, power: float = 1):
        velocity_vector = Vector2(
            self.velocity * cos(radians(self.rotation)),
            -self.velocity * sin(radians(self.rotation))
        )
        self.position += velocity_vector * power * dt
        self.rect.center = self.position

    def update(self, dt) -> None:
        self.inherited_update(dt)
        self.rays.update()
        self.mask = pygame.mask.from_surface(self.image)

    @abstractmethod
    def inherited_update(self, dt) -> None:
        """Updates car's data"""


class UserCar(AbstractCar):
    def __init__(self, start_position, camera):
        self.color = context['theme'].USER_CAR_COLOR
        super().__init__(start_position, camera)

    def inherited_update(self, dt) -> None:
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


class AICar(AbstractCar):
    def __init__(self, start_position: Point, neural_network: NeuralNetwork, camera):
        self.color = context['theme'].AI_CAR_COLOR
        self.neural_network = neural_network

        super().__init__(start_position, camera)

    def get_neural_network_inputs(self):
        inputs = []
        for ray in self.rays:
            inputs.append(ray.current_distance / ray.length)

        return inputs

    def inherited_update(self, dt) -> None:
        inputs_list = self.get_neural_network_inputs()
        answer = self.neural_network.query(inputs_list)

        rotation_power = (2 * answer[0][0]) - 1  # Scales output to [-1; 1]
        engine_power = answer[1][0]

        self.rotate(dt, rotation_power=rotation_power)
        self.move_forward(dt, engine_power=engine_power)


CarClass = t.Union[UserCar, AICar]
