import pygame

from globals import context
from states.state import State
from sprites.car import UserCar
from sprites.track import Track


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
        self.car = UserCar(
            self.track.start_point[0],
            self.track.start_point[1],
            camera=self.app.camera_group
        )
        self.cars.add(self.car)

    def handle_events(self, event) -> None:
        ...

    def update(self, dt):
        self.cars.update(dt)
        self.walls.update()

    def render(self, surface):
        surface.fill(context['theme'].BACKGROUND_COLOR)
        if self.app.config.DEBUG:
            self.car.draw_rays()

        for wall in self.walls:
            if pygame.sprite.collide_mask(self.car, wall):
                self.car.kill()
                self.start_race()

        self.app.camera_group.custom_draw(target=self.car)

        for ray in self.car.rays:
            point, distance = ray.cast(self.walls)
            if point:
                pygame.draw.circle(surface, (255, 255, 0), point - self.app.camera_group.offset, 5)