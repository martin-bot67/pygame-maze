import os
import pygame

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_size=40, asset_dir=None):
        super().__init__()
        if asset_dir:
            image_path = os.path.join(asset_dir, "Coin.png")
        else:
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Coin.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=(x, y))
