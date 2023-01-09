import typing as t

import pygame

from globals import context
from states.state import State
from sprites.car import AICar, UserCar, CarClass
from sprites.track import Track
from ai import NeuralNetwork
from ai.layers import Layer
from ai.genetic_algorithm import run_evolution, print_population, Individual, Population


class Race(State):
    def __init__(self, app, track: Track):
        super().__init__(app)
        self.track = track
        self.cars = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        walls = track.generate_walls(self.app.camera_group, closed=False)
        self.walls.add(walls)

        self.cars_number = 15
        self.add_user_car = False

        self.race_time = 10000
        self.current_time = 0
        self.last_tick = pygame.time.get_ticks()

        self.current_population = []

        self.__start_race()

    def __add_to_population(self, car: CarClass) -> None:
        """
        Adds car to current population

        :param car: :class:`UserCar` or :class:`AICar` instance
        """
        if isinstance(car, AICar) and not car.destroyed:
            fitness = car.evaluate(self.track.central_curve)
            self.current_population.append(Individual(
                neural_network=car.neural_network,
                fitness=fitness
            ))
        car.kill()

    def __start_race(self) -> None:
        """Starts new race"""
        self.last_tick = pygame.time.get_ticks()

        # Adding user car
        if self.add_user_car:
            self.cars.add(UserCar(
                start_position=self.track.start_point,
                camera=self.app.camera_group
            ))

        # First race
        if not self.current_population:
            print('FIRST RACE', len(self.current_population))
            for i in range(self.cars_number):
                car = AICar(
                    start_position=self.track.start_point,
                    neural_network=NeuralNetwork([
                        Layer(units=7, activation='relu'),
                        Layer(units=5, activation='relu'),
                        Layer(units=4, activation='sigmoid'),
                        Layer(units=3),
                    ]),
                    camera=self.app.camera_group
                )
                self.cars.add(car)

        # Subsequent races
        else:
            print_population(self.current_population)
            next_generation = run_evolution(self.current_population)

            for individual in next_generation:
                car = AICar(
                    self.track.start_point,
                    neural_network=individual.neural_network,
                    camera=self.app.camera_group
                )
                self.cars.add(car)

        self.current_population = []

    def handle_events(self, event) -> None:
        key = pygame.key.get_pressed()

        # Starting the race from the very beginning
        if key[pygame.K_1]:
            for car in self.cars:
                car.kill()
            self.__start_race()

    def update(self, dt):
        self.cars.update(dt)
        self.walls.update()

        now = pygame.time.get_ticks()
        self.current_time = now - self.last_tick

        if self.current_time >= self.race_time:
            # Adding all remaining cars to the current population after the time expires
            for car in self.cars:
                self.__add_to_population(car)

            self.__start_race()

    def render(self, surface):
        surface.fill(context['theme'].BACKGROUND_COLOR)
        self.app.camera_group.custom_draw(target=self.cars.sprites()[0])

        for car in self.cars:
            nearest_walls = car.get_nearest_walls(self.walls)

            # Checking collision with walls
            for wall in nearest_walls:
                if pygame.sprite.collide_mask(car, wall):
                    self.__add_to_population(car)

                    # All cars have collided with walls
                    if len(self.cars) <= 0:
                        self.__start_race()

            # Raycasting
            for ray in car.rays:
                point, distance = ray.cast(nearest_walls)
                if point:
                    ray.current_distance = distance
                    pygame.draw.circle(surface, (254, 246, 91), point - self.app.camera_group.offset, 5)
