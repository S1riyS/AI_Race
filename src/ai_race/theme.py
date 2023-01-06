from abc import ABC

from pygame import Color


class Theme(ABC):
    BACKGROUND_COLOR: Color
    WALL_COLOR: Color
    USER_CAR_COLOR: Color
    AI_CAR_COLOR: Color


class DarkTheme(Theme):
    BACKGROUND_COLOR = Color('#0D0D17')
    WALL_COLOR = Color('#0F3460')
    USER_CAR_COLOR = Color('#E94560')
    AI_CAR_COLOR = Color('#5FE944')
