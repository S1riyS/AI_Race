import pygame

from globals import context
from states.state import State
from sprites.car import UserCar, AICar
from sprites.track import Track
from ai import NeuralNetwork
from ai.layers import Layer


class Race(State):
    def __init__(self, app, track: Track):
        super().__init__(app)
        self.car = None

        self.track = track
        self.cars = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()

        self.start_race()

        walls = track.generate_walls(self.app.camera_group, closed=False)
        self.walls.add(walls)

    def start_race(self):
        for i in range(10):
            car = AICar(
                self.track.start_point,
                neural_network=NeuralNetwork([
                    Layer(units=7, activation='sigmoid'),
                    Layer(units=10, activation='sigmoid'),
                    Layer(units=4),
                ]),
                camera=self.app.camera_group
            )
            self.cars.add(car)

    def handle_events(self, event) -> None:
        key = pygame.key.get_pressed()
        if key[pygame.K_1]:
            for car in self.cars:
                car.kill()
            self.start_race()

    def update(self, dt):
        self.cars.update(dt)
        self.walls.update()

    def render(self, surface):
        surface.fill(context['theme'].BACKGROUND_COLOR)
        # if self.app.config.DEBUG:
        #     for car in self.cars:
        #         car.draw_rays()

        self.app.camera_group.custom_draw(target=self.cars.sprites()[0])

        for car in self.cars:
            nearest_walls = car.get_nearest_walls(self.walls)

            for wall in nearest_walls:
                if pygame.sprite.collide_mask(car, wall):
                    car.kill()
                    if len(self.cars) <= 0:
                        self.start_race()

            for ray in car.rays:
                point, distance = ray.cast(nearest_walls)
                if point:
                    ray.current_distance = distance
                    pygame.draw.circle(surface, (254, 246, 91), point - self.app.camera_group.offset, 5)
