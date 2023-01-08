import typing as t

import pygame

from globals import context
from states.state import State
from sprites.car import AICar, UserCar, CarClass
from sprites.track import Track
from ai import NeuralNetwork
from ai.layers import Layer
from ai.genetic_algorithm import run_evolution, print_population, Individual


class Race(State):
    def __init__(self, app, track: Track):
        super().__init__(app)
        self.track = track
        self.cars = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        walls = track.generate_walls(self.app.camera_group, closed=False)
        self.walls.add(walls)

        self.cars_number = 10
        self.add_user_car = False
        self.current_time = 0
        self.last_tick = pygame.time.get_ticks()
        self.cooldown = 10000  # Race time in milliseconds
        self.population = []

        self.start_race()

    def add_to_population(self, car: CarClass):
        if isinstance(car, AICar) and not car.destroyed:
            fitness = car.evaluate(self.track.central_curve, self.current_time)
            self.population.append(Individual(
                neural_network=car.neural_network,
                fitness=fitness
            ))
        car.kill()

    def start_race(self, neural_networks: t.Optional[t.Sequence[NeuralNetwork]] = None):
        self.last_tick = pygame.time.get_ticks()
        self.population = []

        if self.add_user_car:
            self.cars.add(UserCar(
                start_position=self.track.start_point,
                camera=self.app.camera_group
            ))

        if neural_networks is None:
            for i in range(self.cars_number):
                car = AICar(
                    start_position=self.track.start_point,
                    neural_network=NeuralNetwork([
                        Layer(units=9, activation='sigmoid'),
                        Layer(units=6, activation='sigmoid'),
                        Layer(units=5, activation='sigmoid'),
                        Layer(units=2),
                    ]),
                    camera=self.app.camera_group
                )
                self.cars.add(car)
        else:
            for neural_network in neural_networks:
                car = AICar(
                    self.track.start_point,
                    neural_network=neural_network,
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

        now = pygame.time.get_ticks()
        self.current_time = now - self.last_tick

        if self.current_time >= self.cooldown:
            self.last_tick = now
            for car in self.cars:
                self.add_to_population(car)

            print_population(self.population)
            neural_networks = run_evolution(self.population)
            self.start_race(neural_networks)

    def render(self, surface):
        surface.fill(context['theme'].BACKGROUND_COLOR)
        if self.app.config.DEBUG:
            for car in self.cars:
                car.draw_rays()

        self.app.camera_group.custom_draw(target=self.cars.sprites()[0])

        for car in self.cars:
            nearest_walls = car.get_nearest_walls(self.walls)

            for wall in nearest_walls:
                if pygame.sprite.collide_mask(car, wall):
                    self.add_to_population(car)

                    if len(self.cars) <= 0:
                        print_population(self.population)
                        neural_networks = run_evolution(self.population)
                        self.start_race(neural_networks)

            for ray in car.rays:
                point, distance = ray.cast(nearest_walls)
                if point:
                    ray.current_distance = distance
                    pygame.draw.circle(surface, (254, 246, 91), point - self.app.camera_group.offset, 5)
