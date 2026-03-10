import pygame

class Varas(pygame.sprite.Sprite):
    def __init__(self, x, y, akna_laius, akna_korgus, walls):
        super().__init__()
        self.image = pygame.image.load("Tegelane_varas.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.kiirus = 10
        self.akna_laius = akna_laius
        self.akna_korgus = akna_korgus
        self.walls = walls

    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0

        # Liikumine klahvide järgi
        if keys[pygame.K_a]:
            dx = -self.kiirus
        if keys[pygame.K_d]:
            dx = self.kiirus
        if keys[pygame.K_w]:
            dy = -self.kiirus
        if keys[pygame.K_s]:
            dy = self.kiirus

        # Esmalt liiguta horisontaalselt ja kontrolli kollisiooni
        self.rect.x += dx
        for wall in self.walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        # Siis liiguta vertikaalselt ja kontrolli kollisiooni
        self.rect.y += dy
        for wall in self.walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

        
        
        
        maze_laius = 32 * 40
        maze_korgus = 18 * 40

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > maze_laius:
            self.rect.right = maze_laius
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > maze_korgus:
            self.rect.bottom = maze_korgus