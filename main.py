import os
import pygame
import Tegelane_Varas
import random
import time

# See rida on vajalik, et pilves ei tekiks helivigu
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

pygame.init()

#ekraani suurus
laius = 1280
kõrgus = 720

aken = pygame.display.set_mode((laius, kõrgus))
pygame.display.set_caption("Labürindi mäng")
taustapilt = pygame.image.load("egypt_pixel.png")

TILE_SIZE = 40  # iga ruudu suurus
tiles = [0, 1, 2, 4]  # added 4 for start tile (yellow)

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Coin.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

def generate_random_maze(width, height):
    """Generate a random maze using recursive backtracking."""
    # Initialize maze with all walls
    maze = [[1 for _ in range(width)] for _ in range(height)]
    coin_positions = []
    
    # Carve paths using recursive backtracking
    def carve_path(x, y):
        maze[y][x] = 0
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve_path(nx, ny)
    
    # Start from position (1, 1)
    carve_path(1, 1)
    
    # Set borders to walls
    for i in range(width):
        maze[0][i] = 1
        maze[height - 1][i] = 1
    for i in range(height):
        maze[i][0] = 1
        maze[i][width - 1] = 1
    
    # Set start and end positions
    maze[1][1] = 4  # yellow start block
    # Find the furthest carved position from start and place goal there
    goal_x, goal_y = width - 3, height - 3
    if maze[goal_y][goal_x] == 0:
        maze[goal_y][goal_x] = 2
    else:
        # If that position is a wall, find nearby carved position
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                ny, nx = goal_y + dy, goal_x + dx
                if 0 < ny < height - 1 and 0 < nx < width - 1 and maze[ny][nx] == 0:
                    maze[ny][nx] = 2
    
    # Randomly place coins in the maze
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == 0 and random.random() < 0.03:  # 3% chance for coins
                coin_positions.append((x * TILE_SIZE, y * TILE_SIZE))
    
    return maze, coin_positions

maze, coin_positions = generate_random_maze(32, 18)

# Seina ja tee värvid
tile_images = {
    0: pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA),
    1: pygame.Surface((TILE_SIZE, TILE_SIZE)),
    2: pygame.Surface((TILE_SIZE, TILE_SIZE)),
    4: pygame.Surface((TILE_SIZE, TILE_SIZE))  # yellow start block
}
tile_images[0].fill((226, 208, 179))  # liivatee
tile_images[1].fill((164, 148, 98))   # sein
tile_images[2].fill((0, 255, 0))      # sihtpunkt
tile_images[4].fill((255, 255, 0))    # start (yellow)

# Loo seinad rectangle objektid
walls = []
start_rect = None
goal_rect = None
for row_idx, row in enumerate(maze):
    for col_idx, tile in enumerate(row):
        if tile == 1:
            walls.append(pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        elif tile == 2:
            goal_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        elif tile == 4:
            start_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)

# Create coin sprites
coins = pygame.sprite.Group()
for x, y in coin_positions:
    coins.add(Coin(x, y))

# Coin counter
coins_collected = 0
# Level counter
level = 1
font = pygame.font.Font(None, 36)

# Tegelase asukoht
if start_rect:
    x_asukoht, y_asukoht = start_rect.topleft
else:
    x_asukoht, y_asukoht = 70, 130

# Loo tegelane koos seinadega
tegelane_varvas = Tegelane_Varas.Varas(x_asukoht, y_asukoht, laius, kõrgus, walls)
peategelane = pygame.sprite.Group()
peategelane.add(tegelane_varvas)

# Game timer
start_time = time.time()

# Peatsükl
tootab = True
while tootab:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            tootab = False

    peategelane.update()

    # Check for coin collisions
    for coin in pygame.sprite.spritecollide(tegelane_varvas, coins, True):
        coins_collected += 1

    # Check for goal collision
    if tegelane_varvas.rect.colliderect(goal_rect):
        # reset timer and generate new maze
        start_time = time.time()
        level += 1
        maze, coin_positions = generate_random_maze(32, 18)
        # rebuild walls, start_rect, goal_rect
        walls = []
        start_rect = None
        goal_rect = None
        for row_idx, row in enumerate(maze):
            for col_idx, tile in enumerate(row):
                if tile == 1:
                    walls.append(pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif tile == 2:
                    goal_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                elif tile == 4:
                    start_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        tegelane_varvas.walls = walls
        # reposition player
        if start_rect:
            tegelane_varvas.rect.topleft = start_rect.topleft
        # reset coins
        coins = pygame.sprite.Group()
        for x, y in coin_positions:
            coins.add(Coin(x, y))

    # Joonista taust ja maze
    aken.blit(taustapilt, (0, 0))
    for row_idx, row in enumerate(maze):
        for col_idx, tile in enumerate(row):
            aken.blit(tile_images[tile], (col_idx * TILE_SIZE, row_idx * TILE_SIZE))
    # draw start block on top if it exists
    if start_rect:
        aken.blit(tile_images[4], start_rect)
    peategelane.draw(aken)
    coins.draw(aken)
    
    # Calculate elapsed time
    elapsed_time = int(time.time() - start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    
    # Display level counter in middle top
    level_text = font.render(f"Tase: {level}", True, (255, 255, 255))
    aken.blit(level_text, (laius // 2 - 50, 10))
    
    # Display coin counter at top right
    coin_text = font.render(f"M\xfcndid: {coins_collected}", True, (255, 255, 255))
    aken.blit(coin_text, (laius - 200, 10))
    
    # Display timer at top left
    time_text = font.render(f"Aeg: {minutes}:{seconds:02d}", True, (255, 255, 255))
    aken.blit(time_text, (10, 10))
    
    pygame.display.flip()

pygame.quit()