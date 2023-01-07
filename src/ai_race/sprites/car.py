import typing as t
from abc import ABC, abstractmethod
from math import sin, cos, radians, pi, hypot

import pygame
from pygame.math import Vector2

from globals import context
from sprites.ray import Ray
from sprites.wall import Wall
from ai import NeuralNetwork
from local_typing import Point


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
        self.positional_vector = Vector2(self.x, self.y)

        self.mask = pygame.mask.from_surface(self.image)

        self.rotation = 0
        self.rotation_speed = 3.5

        self.velocity = 0
        self.max_velocity = 11
        self.acceleration = 0.2
        self.deceleration = 0.5

        self.camera = camera
        self.rays = pygame.sprite.Group()
        self.init_rays(number=6)

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
            dx = wall.start_position[0] - self.positional_vector.x
            dy = wall.start_position[1] - self.positional_vector.y
            distance = hypot(dx, dy)

            if distance <= 900:
                nearest_walls.append(wall)

        return nearest_walls

    def kill(self) -> None:
        for ray in self.rays:
            ray.kill()
        super().kill()

    def rotate(self, dt, left=False, right=False):
        if left:
            self.rotation = (self.rotation + self.rotation_speed * dt) % 360
        elif right:
            self.rotation = (self.rotation - self.rotation_speed * dt) % 360

        new_image = pygame.transform.rotate(self.original_image, self.rotation)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def move(self, dt):
        velocity_vector = Vector2(
            self.velocity * cos(radians(self.rotation)),
            -self.velocity * sin(radians(self.rotation))
        )
        self.positional_vector += velocity_vector * dt
        self.rect.center = self.positional_vector

    def move_forward(self, dt):
        self.velocity = min(self.velocity + self.acceleration * dt, self.max_velocity)
        self.move(dt)

    def move_backward(self, dt):
        self.velocity = max(self.velocity - self.acceleration * dt, -self.max_velocity / 2)
        self.move(dt)

    def reduce_speed(self, dt):
        self.velocity = max(self.velocity - self.deceleration * dt, 0)
        self.move(dt)

    def update(self, dt) -> None:
        self.inherited_update(dt)
        self.rays.update()

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
            self.rotate(dt, right=True)
        elif key[pygame.K_LEFT]:
            self.rotate(dt, left=True)

        if not moved:
            self.reduce_speed(dt)

        self.mask = pygame.mask.from_surface(self.image)


class AICar(AbstractCar):
    def __init__(self, start_position: Point, neural_network: NeuralNetwork, camera):
        self.color = context['theme'].AI_CAR_COLOR
        self.neural_network = neural_network

        super().__init__(start_position, camera)

    def get_neural_network_inputs(self):
        inputs = []
        for ray in self.rays:
            inputs.append(ray.current_distance / ray.length)
        inputs.append(self.velocity / self.max_velocity)

        return inputs

    def inherited_update(self, dt) -> None:
        inputs_list = self.get_neural_network_inputs()
        answer = self.neural_network.query(inputs_list)
        action = answer.argmax()

        moved = False
        if action == 0:
            moved = True
            self.move_backward(dt)
        elif action == 1:
            moved = True
            self.move_forward(dt)
        if action == 2:
            self.rotate(dt, right=True)
        elif action == 3:
            self.rotate(dt, left=True)

        if not moved:
            self.reduce_speed(dt)
