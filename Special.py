import pygame
import pygame_menu
import numpy as np
import sys
import time

# --- Configuration ---
GRID_SIZE = 14
CELL_SIZE = 40
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# --- Option Selection Menu ---

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Select Starting Option")
clock = pygame.time.Clock()

config = {
    "start_option": "A"  # Default option
}

def set_option(value, option):
    config["start_option"] = option

def start_simulation():
    global start_flag
    start_flag = True

menu = pygame_menu.Menu('Select Starting Option', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED)
menu.add.selector('Starting Option:', [('Option A', 'A'), ('Option B', 'B')], onchange=set_option)
menu.add.button('Start Simulation', start_simulation)

start_flag = False
while not start_flag:
    screen.fill((240, 240, 240))

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    menu.update(events)
    menu.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# --- Initialize Grid Based on Selected Option ---

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Simulation")

grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

if config["start_option"] == "A":
    positions = [(0,1),(2,3),(4,5),(6,7),(8,9),(10,11),(12,13)]
    positions += [(1,0),(3,2),(5,4),(7,6),(9,8),(11,10),(13,12)]
    stop_interval = 4  # Stop every 4 generations
elif config["start_option"] == "B":
    positions = [(4,3),(5,3),(3,8),(3,9),(6,8),(6,9),(4,10),(5,10)]
    stop_interval = 8  # Stop every 8 generations

for (i, j) in positions:
    grid[i][j] = 1

# --- Functions ---

def draw_grid(current_generation):
    screen.fill(WHITE)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            color = BLACK if grid[i][j] == 1 else WHITE
            pygame.draw.rect(screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (200, 200, 200), (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    if current_generation % 2 == 1:
        block_color = BLUE
        starts = range(0, GRID_SIZE + 1, 2)
    else:
        block_color = RED
        starts = range(1, GRID_SIZE, 2)

    for i in starts:
        pygame.draw.line(screen, block_color, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 2)
    for j in starts:
        pygame.draw.line(screen, block_color, (j * CELL_SIZE, 0), (j * CELL_SIZE, HEIGHT), 2)

    pygame.display.flip()

def update(grid, generation, wraparound=True):
    new_grid = grid.copy()
    N = grid.shape[0]

    if generation % 2 == 1:
        start_i, start_j = 0, 0
    else:
        start_i, start_j = 1, 1

    for i in range(start_i, N, 2):
        for j in range(start_j, N, 2):
            indices = [(i % N, j % N), (i % N, (j+1) % N), ((i+1) % N, j % N), ((i+1) % N, (j+1) % N)]
            if not wraparound and (i+1 >= N or j+1 >= N):
                continue

            block = [grid[x][y] for x, y in indices]
            alive = sum(block)

            if alive != 2:
                for x, y in indices:
                    new_grid[x][y] = 1 - grid[x][y]
                if alive == 3:
                    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = indices
                    new_grid[x0][y0], new_grid[x3][y3] = new_grid[x3][y3], new_grid[x0][y0]
                    new_grid[x1][y1], new_grid[x2][y2] = new_grid[x2][y2], new_grid[x1][y1]

    return new_grid

# --- Simulation ---

running = True
generation_sim = 1
FPS = 5
clock = pygame.time.Clock()

while running and generation_sim <= 100:
    clock.tick(FPS)

    grid = update(grid, generation_sim, wraparound=True)
    draw_grid(generation_sim)

    # Pause depending on selected option
    if generation_sim % stop_interval == 0:
        pygame.display.flip()
        time.sleep(3)

    generation_sim += 1

# --- Keep window open after simulation ends ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

