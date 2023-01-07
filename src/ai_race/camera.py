import pygame


class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.screen_width, self.screen_height = self.display_surface.get_size()
        self.offset = pygame.math.Vector2()

        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2

    def center_target_camera(self, target: pygame.sprite.Sprite):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def custom_draw(self, target: pygame.sprite.Sprite):
        self.center_target_camera(target)

        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset

            fits_width = -0.3 * self.screen_width <= offset_pos.x <= 1.3 * self.screen_width
            fits_height = -0.3 * self.screen_height <= offset_pos.y <= 1.3 * self.screen_height

            if fits_width and fits_height:
                self.display_surface.blit(sprite.image, offset_pos)
