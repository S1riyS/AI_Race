from abc import ABC, abstractmethod

from pygame.surface import Surface
from pygame.event import Event
import pygame_gui


class State(ABC):
    def __init__(self, app):
        self.app = app
        self.local_manager = pygame_gui.UIManager(self.app.config.WINDOW_SIZE)
        self.prev_state = None

    @abstractmethod
    def update(self, dt: float) -> None:
        """Updates current state"""
        ...

    def update_wrapper(self, dt: float) -> None:
        self.update(dt)
        self.local_manager.update(dt)

    @abstractmethod
    def render(self, surface: Surface) -> None:
        """Renders current state"""
        ...

    def render_wrapper(self, surface: Surface) -> None:
        self.render(surface)
        self.local_manager.draw_ui(surface)

    @abstractmethod
    def handle_events(self, event: Event) -> None:
        """Handles events of current state"""
        ...

    def handle_events_wrapper(self, event: Event) -> None:
        self.handle_events(event)
        self.local_manager.process_events(event)

    def enter_state(self) -> None:
        if len(self.app.state_stack) > 1:
            self.prev_state = self.app.state_stack[-1]
        self.app.state_stack.append(self)

    def exit_state(self) -> None:
        self.app.state_stack.pop()
