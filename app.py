import pygame
import pygame_gui

from config import Config, base_config
from camera import CameraGroup
from states.track_generator import TrackGenerator

pygame.init()


class App:
    def __init__(self, config: Config):
        self.config = config
        self.screen = pygame.display.set_mode(self.config.WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.config.CAPTION)

        self.camera_group = CameraGroup()
        self.manager = pygame_gui.UIManager(self.config.WINDOW_SIZE)

        self.is_running = True
        self.state_stack = []
        self.dt = 0

        self.__load_states()

    def __get_delta_time(self) -> None:
        self.dt = self.clock.tick(self.config.FPS) / 1000 * self.config.TARGET_FPS

    def __handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            self.state_stack[-1].handle_events_wrapper(event)

            self.manager.process_events(event)

    def __update(self) -> None:
        self.state_stack[-1].update_wrapper(self.dt)
        self.manager.update(self.dt)

    def __render(self):
        self.state_stack[-1].render_wrapper(self.screen)
        self.manager.draw_ui(self.screen)

    def __load_states(self):
        track_generator = TrackGenerator(self)
        self.state_stack.append(track_generator)

    def run(self) -> None:
        while self.is_running:
            self.clock.tick(Config.FPS)

            self.__get_delta_time()
            self.__handle_events()
            self.__update()
            self.__render()

            pygame.display.update()

        pygame.quit()  # Quit


if __name__ == '__main__':
    app = App(config=base_config)
    app.run()
