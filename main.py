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
    
    # Remove dead ends to create a braid maze
    def remove_dead_ends():
        changed = True
        while changed:
            changed = False
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if maze[y][x] == 0:
                        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                        open_count = sum(1 for nx, ny in neighbors if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 0)
                        if open_count == 1:
                            # dead end, remove a random wall
                            wall_neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1]
                            if wall_neighbors:
                                wx, wy = random.choice(wall_neighbors)
                                maze[wy][wx] = 0
                                changed = True
    
    remove_dead_ends()
    
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
total_coins = len(coin_positions)
# Level counter
level = 1
font = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Track coins for each level and total
level_coins = {}
total_coins_collected = 0
time_out_triggered = False
death_time = None

# Time limit in seconds
TIME_LIMIT = 20  # aeg ehk time counter

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

    # Calculate time left
    elapsed_time = time.time() - start_time
    time_left = max(0, TIME_LIMIT - int(elapsed_time))

    # Check if time is up
    if time_left == 0 and not time_out_triggered:
        if coins_collected < total_coins:
            # Deduct 7 coins and advance to next level
            level_coins[level] = -7
            total_coins_collected -= 7
        elif coins_collected == total_coins:
            # Deduct 5 coins and advance to next level
            level_coins[level] = -5
            total_coins_collected -= 5
        level += 1
        time_out_triggered = True
        maze, coin_positions = generate_random_maze(32, 18)
        total_coins = len(coin_positions)
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
        if start_rect:
            tegelane_varvas.rect.topleft = start_rect.topleft
        coins = pygame.sprite.Group()
        for x, y in coin_positions:
            coins.add(Coin(x, y))
        coins_collected = 0
        start_time = time.time()
        time_out_triggered = False

    # Check for coin collisions
    for coin in pygame.sprite.spritecollide(tegelane_varvas, coins, True):
        coins_collected += 1

    # Check for goal collision (only if all coins collected and time remains)
    if tegelane_varvas.rect.colliderect(goal_rect) and coins_collected == total_coins and time_left > 0:
        # Record coins for this level and add to total
        level_coins[level] = coins_collected
        total_coins_collected += coins_collected
        time_out_triggered = False
        # Advance to next level
        level += 1
        maze, coin_positions = generate_random_maze(32, 18)
        total_coins = len(coin_positions)
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
        if start_rect:
            tegelane_varvas.rect.topleft = start_rect.topleft
        coins = pygame.sprite.Group()
        for x, y in coin_positions:
            coins.add(Coin(x, y))
        coins_collected = 0
        start_time = time.time()

    # Joonista taust ja maze
    
    # Check if player died (coins <= -10)
    if total_coins_collected <= -10:
        if death_time is None:
            death_time = time.time()
        
        # Draw black screen
        black_screen = pygame.Surface((laius, kõrgus))
        black_screen.fill((0, 0, 0))
        aken.blit(black_screen, (0, 0))
        
        # Display "You died" text
        death_font = pygame.font.Font(None, 72)
        death_text = death_font.render("You Died", True, (255, 0, 0))
        text_rect = death_text.get_rect(center=(laius // 2, kõrgus // 2))
        aken.blit(death_text, text_rect)
        
        pygame.display.flip()
        
        # Check if 7 seconds have passed
        if time.time() - death_time >= 7:
            # Reset game
            level = 1
            total_coins_collected = 0
            level_coins = {}
            time_out_triggered = False
            death_time = None
            maze, coin_positions = generate_random_maze(32, 18)
            total_coins = len(coin_positions)
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
            if start_rect:
                tegelane_varvas.rect.topleft = start_rect.topleft
            coins = pygame.sprite.Group()
            for x, y in coin_positions:
                coins.add(Coin(x, y))
            coins_collected = 0
            start_time = time.time()
    else:
        # Normal game rendering
        aken.blit(taustapilt, (0, 0))
        for row_idx, row in enumerate(maze):
            for col_idx, tile in enumerate(row):
                aken.blit(tile_images[tile], (col_idx * TILE_SIZE, row_idx * TILE_SIZE))
        # draw start block on top if it exists
        if start_rect:
            aken.blit(tile_images[4], start_rect)
        peategelane.draw(aken)
        coins.draw(aken)
        
        # Display level counter in middle top
        #level_text = font.render(f"Tase: {level}", True, (255, 255, 255))
        #aken.blit(level_text, (laius // 2 - 50, 10))
        
        # Display total coins collected at top right
        coin_text = font.render(f"Kokku Mündid: {total_coins_collected}", True, (255, 255, 255))
        aken.blit(coin_text, (laius - 220, 10))
        
        # Display timer at top left
        minutes = time_left // 60
        seconds = time_left % 60
        time_text = font.render(f"Aeg: {minutes}:{seconds:02d}", True, (255, 255, 255))
        aken.blit(time_text, (10, 10))
        
        pygame.display.flip()

pygame.quit()