from abc import ABC, abstractmethod
from math import sin, cos, radians, pi

import pygame
from pygame.math import Vector2

from globals import context
from sprites.ray import Ray


class AbstractCar(ABC, pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, camera: pygame.sprite.Group):
        super().__init__(camera)
        self.x = x
        self.y = y

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
        rays_number = max(2, number)
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
    def __init__(self, x, y, camera):
        self.color = context['theme'].USER_CAR_COLOR
        super().__init__(x, y, camera)

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
    def __init__(self, x, y, camera):
        self.color = context['theme'].AI_CAR_COLOR
        super().__init__(x, y, camera)

    def inherited_update(self, dt) -> None:
        ...
