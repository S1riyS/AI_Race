from math import sin, cos, radians

import pygame
from pygame.math import Vector2


class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, group):
        super().__init__(group)
        self.x = x
        self.y = y

        self.width = 60
        self.height = 30
        self.color = pygame.Color(243, 69, 96)

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