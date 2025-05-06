import pygame
import numpy as np
import sys
import time

# --- Configuration ---
GRID_SIZE = 14          # Number of cells in each row and column (grid size)
CELL_SIZE = 40          # Size (in pixels) of each cell
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE  # Screen dimensions based on grid
WHITE = (255, 255, 255) # Color for dead cells and background
BLACK = (0, 0, 0)       # Color for alive cells
BLUE = (0, 0, 255)      # Color for block grid lines on odd generations
RED = (255, 0, 0)       # Color for block grid lines on even generations

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Setup - Glider Pattern")

# Initialize the grid (all cells are dead initially)
grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
generation = 1

# --- Define glider pattern (preset initial condition) ---
def initialize_glider():
    """
    Initialize the grid with a glider pattern at specific positions.
    """
    glider_cells = [(0, 6), (0, 7), (2, 5), (2, 8)]
    for i, j in glider_cells:
        grid[i][j] = 1

initialize_glider()

# --- Function to draw the grid on the screen ---
def draw_grid(current_generation):
    """
    Draw the entire grid and the block lines on the screen.
    """
    screen.fill(WHITE)

    # Draw each cell: black for alive, white for dead
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            color = BLACK if grid[i][j] == 1 else WHITE
            pygame.draw.rect(screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (200, 200, 200), (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)  # Light grid lines

    # Draw block lines to show the current processing pattern
    if current_generation % 2 == 1:
        block_color = BLUE
        starts = range(0, GRID_SIZE + 1, 2)
    else:
        block_color = RED
        starts = range(1, GRID_SIZE, 2)

    # Draw horizontal block lines
    for i in starts:
        pygame.draw.line(screen, block_color, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 2)

    # Draw vertical block lines
    for j in starts:
        pygame.draw.line(screen, block_color, (j * CELL_SIZE, 0), (j * CELL_SIZE, HEIGHT), 2)

    pygame.display.flip()

# --- Function to update the grid state (cellular automaton rules) ---
def update(grid, generation, wraparound=True):
    """
    Update the grid based on the custom block rules.
    """
    new_grid = grid.copy()
    N = grid.shape[0]

    # Alternate starting positions between even and odd generations
    if generation % 2 == 1:
        start_i, start_j = 0, 0
    else:
        start_i, start_j = 1, 1

    # Process each 2x2 block
    for i in range(start_i, N, 2):
        for j in range(start_j, N, 2):

            # Collect indices for the current 2x2 block (with wraparound if enabled)
            indices = [(i % N, j % N), (i % N, (j+1) % N), ((i+1) % N, j % N), ((i+1) % N, (j+1) % N)]

            # If wraparound is disabled, skip out-of-bound blocks
            if not wraparound and (i+1 >= N or j+1 >= N):
                continue

            block = [grid[x][y] for x, y in indices]
            alive = sum(block)

            # Rule: if alive cells are not exactly 2, flip the state of each cell
            if alive != 2:
                for x, y in indices:
                    new_grid[x][y] = 1 - grid[x][y]

                # If exactly 3 alive after flip, swap pairs to introduce motion
                if alive == 3:
                    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = indices
                    new_grid[x0][y0], new_grid[x3][y3] = new_grid[x3][y3], new_grid[x0][y0]
                    new_grid[x1][y1], new_grid[x2][y2] = new_grid[x2][y2], new_grid[x1][y1]

    return new_grid

# --- Simulation loop ---
running = True
generation_sim = 1
FPS = 5  # Simulation speed (generations per second)
clock = pygame.time.Clock()

while running and generation_sim <= 100:
    clock.tick(FPS)

    # Update grid state
    grid = update(grid, generation_sim, wraparound=True)

    # Draw the grid
    draw_grid(generation_sim)

    # Pause for 2 seconds every 4 generations (for visualization)
    if generation_sim % 4 == 0:
        pygame.display.flip()
        time.sleep(2)

    generation_sim += 1

# --- Keep window open after simulation finishes ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


