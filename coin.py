import pygame

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_size=40):
        super().__init__()
        self.image = pygame.image.load("Coin.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=(x, y))
