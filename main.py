import os
import asyncio
import pygame
import Tegelane_Varas
import random
import time
from coin import Coin

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

pygame.init()

laius = 1280
kõrgus = 720

aken = pygame.display.set_mode((laius, kõrgus))
pygame.display.set_caption("Labürindi mäng")
taustapilt = pygame.image.load("egypt_pixel.png")

TILE_SIZE = 40
tiles = [0, 1, 2, 4]


def generate_random_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    coin_positions = []

    # Iterative maze carving - no recursion so pygbag won't crash
    def carve_path(start_x, start_y):
        maze[start_y][start_x] = 0
        stack = [(start_x, start_y)]
        while stack:
            x, y = stack[-1]
            directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
            random.shuffle(directions)
            carved = False
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == 1:
                    maze[y + dy // 2][x + dx // 2] = 0
                    maze[ny][nx] = 0
                    stack.append((nx, ny))
                    carved = True
                    break
            if not carved:
                stack.pop()

    carve_path(1, 1)

    def remove_dead_ends():
        changed = True
        while changed:
            changed = False
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if maze[y][x] == 0:
                        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                        open_count = sum(
                            1 for nx, ny in neighbors
                            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 0
                        )
                        if open_count == 1:
                            wall_neighbors = [
                                (nx, ny) for nx, ny in neighbors
                                if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1
                            ]
                            if wall_neighbors:
                                wx, wy = random.choice(wall_neighbors)
                                maze[wy][wx] = 0
                                changed = True

    remove_dead_ends()

    for i in range(width):
        maze[0][i] = 1
        maze[height - 1][i] = 1
    for i in range(height):
        maze[i][0] = 1
        maze[i][width - 1] = 1

    maze[1][1] = 4
    goal_x, goal_y = width - 3, height - 3
    if maze[goal_y][goal_x] == 0:
        maze[goal_y][goal_x] = 2
    else:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                ny, nx = goal_y + dy, goal_x + dx
                if 0 < ny < height - 1 and 0 < nx < width - 1 and maze[ny][nx] == 0:
                    maze[ny][nx] = 2

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == 0 and random.random() < 0.03:
                coin_positions.append((x * TILE_SIZE, y * TILE_SIZE))

    return maze, coin_positions


maze, coin_positions = generate_random_maze(32, 18)

tile_images = {
    0: pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA),
    1: pygame.Surface((TILE_SIZE, TILE_SIZE)),
    2: pygame.Surface((TILE_SIZE, TILE_SIZE)),
    4: pygame.Surface((TILE_SIZE, TILE_SIZE)),
}
tile_images[0].fill((226, 208, 179))
tile_images[1].fill((164, 148, 98))
tile_images[2].fill((0, 255, 0))
tile_images[4].fill((255, 255, 0))

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

coins = pygame.sprite.Group()
for x, y in coin_positions:
    coins.add(Coin(x, y, TILE_SIZE))

coins_collected = 0
total_coins = len(coin_positions)
level = 1
font = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 24)

level_coins = {}
total_coins_collected = 0
time_out_triggered = False
game_over = False
intro = True

TIME_LIMIT = 20

restart_button = pygame.Rect(laius // 2 - 100, kõrgus // 2 + 60, 200, 50)
start_button = pygame.Rect(laius // 2 - 100, kõrgus // 2 + 60, 200, 50)

if start_rect:
    x_asukoht, y_asukoht = start_rect.topleft
else:
    x_asukoht, y_asukoht = 70, 130

tegelane_varvas = Tegelane_Varas.Varas(x_asukoht, y_asukoht, laius, kõrgus, walls)
peategelane = pygame.sprite.Group()
peategelane.add(tegelane_varvas)


def setup_new_maze():
    global maze, coin_positions, total_coins, walls, start_rect, goal_rect, coins, coins_collected, start_time

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
        coins.add(Coin(x, y, TILE_SIZE))
    coins_collected = 0
    start_time = time.time()


def reset_game():
    global level, total_coins_collected, level_coins, time_out_triggered, game_over

    level = 1
    total_coins_collected = 0
    level_coins = {}
    time_out_triggered = False
    game_over = False
    setup_new_maze()


start_time = None
clock = pygame.time.Clock()


async def main():
    global coins_collected, total_coins_collected, level, time_out_triggered, game_over, intro, start_time

    tootab = True
    while tootab:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                tootab = False

            if intro and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    intro = False
                    game_over = False
                    start_time = time.time()

            if intro and event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                intro = False
                game_over = False
                start_time = time.time()

            if game_over and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos):
                    reset_game()

            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                reset_game()

        if not intro and not game_over:
            peategelane.update()

        if intro:
            aken.fill((0, 0, 0))
            game_name_text = font_large.render("Labyrint", True, (255, 127, 80))
            game_name_rect = game_name_text.get_rect(center=(laius // 2, kõrgus // 2 - 130))
            aken.blit(game_name_text, game_name_rect)

            title = font.render("How to move: W, A, S, D", True, (255, 255, 255))
            title_rect = title.get_rect(center=(laius // 2, kõrgus // 2 - 40))
            aken.blit(title, title_rect)

            pygame.draw.rect(aken, (255, 255, 255), start_button)
            start_text = font.render("Start", True, (0, 0, 0))
            start_text_rect = start_text.get_rect(center=start_button.center)
            aken.blit(start_text, start_text_rect)

            pygame.display.flip()
            await asyncio.sleep(0)
            clock.tick(60)
            continue

        elapsed_time = time.time() - start_time
        time_left = max(0, TIME_LIMIT - int(elapsed_time))

        if time_left == 0 and not time_out_triggered:
            if coins_collected < total_coins:
                level_coins[level] = -7
                total_coins_collected -= 7
            elif coins_collected == total_coins:
                level_coins[level] = -5
                total_coins_collected -= 5
            level += 1
            time_out_triggered = True
            setup_new_maze()
            time_out_triggered = False

        for coin in pygame.sprite.spritecollide(tegelane_varvas, coins, True):
            coins_collected += 1

        if tegelane_varvas.rect.colliderect(goal_rect) and coins_collected == total_coins and time_left > 0:
            level_coins[level] = coins_collected
            total_coins_collected += coins_collected
            time_out_triggered = False
            level += 1
            setup_new_maze()

        if total_coins_collected <= -10:
            game_over = True

            black_screen = pygame.Surface((laius, kõrgus))
            black_screen.fill((0, 0, 0))
            aken.blit(black_screen, (0, 0))

            death_font = pygame.font.Font(None, 72)
            death_text = death_font.render("Game Over", True, (255, 0, 0))
            text_rect = death_text.get_rect(center=(laius // 2, kõrgus // 2 - 50))
            aken.blit(death_text, text_rect)

            pygame.draw.rect(aken, (255, 255, 255), restart_button)
            button_text = font.render("Play again", True, (0, 0, 0))
            button_text_rect = button_text.get_rect(center=restart_button.center)
            aken.blit(button_text, button_text_rect)

            pygame.display.flip()
        else:
            aken.blit(taustapilt, (0, 0))
            for row_idx, row in enumerate(maze):
                for col_idx, tile in enumerate(row):
                    aken.blit(tile_images[tile], (col_idx * TILE_SIZE, row_idx * TILE_SIZE))
            if start_rect:
                aken.blit(tile_images[4], start_rect)
            peategelane.draw(aken)
            coins.draw(aken)

            coin_text = font.render(f"Kokku Mündid: {total_coins_collected}", True, (255, 255, 255))
            aken.blit(coin_text, (laius - 220, 10))

            minutes = time_left // 60
            seconds = time_left % 60
            time_text = font.render(f"Aeg: {minutes}:{seconds:02d}", True, (255, 255, 255))
            aken.blit(time_text, (10, 10))

            pygame.display.flip()

        await asyncio.sleep(0)
        clock.tick(60)

    pygame.quit()


asyncio.run(main())