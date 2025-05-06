import pygame
import pygame_menu
import numpy as np
import math
import sys
import matplotlib.pyplot as plt
import os

# Enable interactive mode for plotting (will be turned off later)
plt.ion()

# --- Initial Configuration ---
SIMULATION_FPS = 10  # Speed of the simulation in Frames Per Second

# Default simulation settings
config = {
    'N': 100,              # Grid size (NxN)
    'prob': 0.25,          # Initial alive cell probability
    'wraparound': True,    # Whether the grid wraps around edges
    'generations': 250     # Number of generations to simulate
}

# Flag to start the simulation after user input
def start_simulation():
    global start_flag
    start_flag = True

# --- Setup menu using pygame_menu ---
pygame.init()
screen = pygame.display.set_mode((600, 700))
pygame.display.set_caption("Cellular Automaton - Bio Menu")
clock = pygame.time.Clock()

# Create menu UI
menu = pygame_menu.Menu('Cellular Automaton - Bio Menu', 600, 700, theme=pygame_menu.themes.THEME_SOLARIZED)

# Add user-selectable options to the menu
menu.add.selector('Grid Size :', [('100', 100), ('150', 150), ('200', 200)], onchange=lambda v, val: config.update(N=val))
menu.add.selector('Alive Probability :', [('0.25', 0.25), ('0.5', 0.5), ('0.75', 0.75)], onchange=lambda v, val: config.update(prob=val))
menu.add.selector('Wraparound :', [('Yes', True), ('No', False)], onchange=lambda v, val: config.update(wraparound=val))
menu.add.text_input('Generations :', default='250', onchange=lambda val: config.update(generations=int(val)))
menu.add.button('Start Simulation', start_simulation)

start_flag = False
t = 0

# --- Wait for user to start simulation ---
while not start_flag:
    screen.fill((230, 255, 240))

    # Handle user input events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    menu.update(events)
    menu.draw(screen)

    pygame.display.flip()
    t += 0.05
    clock.tick(60)

pygame.quit()

# --- Simulation Initialization ---
N = config['N']
initial_alive_probability = config['prob']
wraparound = config['wraparound']
max_generations = config['generations']

CELL_SIZE = 5
WIDTH = HEIGHT = N * CELL_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH + 300, HEIGHT))  # Extra space for statistics
pygame.display.set_caption("Cellular Automaton Simulation")

# Initialize grid with alive/dead cells based on probability
grid = np.random.choice([0, 1], size=(N, N), p=[1 - initial_alive_probability, initial_alive_probability])

# --- Update function to evolve the grid ---
def update(grid, generation, wraparound=True):
    new_grid = grid.copy()

    # Alternate starting point for block processing based on generation parity
    if generation % 2 == 1:
        start_i, start_j = 0, 0
    else:
        start_i, start_j = 1, 1

    for i in range(start_i, N, 2):
        for j in range(start_j, N, 2):
            # Determine indices of the current 2x2 block (with optional wraparound)
            indices = [(i % N, j % N), (i % N, (j+1) % N), ((i+1) % N, j % N), ((i+1) % N, (j+1) % N)]
            
            if not wraparound and (i+1 >= N or j+1 >= N):
                continue  # Skip blocks at the edges if wraparound is disabled

            block = [grid[x][y] for x, y in indices]
            alive = sum(block)

            # Apply rules: Flip cells unless exactly 2 are alive, swap pairs if exactly 3 are alive
            if alive != 2:
                for x, y in indices:
                    new_grid[x][y] = 1 - grid[x][y]
                if alive == 3:
                    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = indices
                    new_grid[x0][y0], new_grid[x3][y3] = new_grid[x3][y3], new_grid[x0][y0]
                    new_grid[x1][y1], new_grid[x2][y2] = new_grid[x2][y2], new_grid[x1][y1]
    return new_grid

# Calculate stability: how much of the grid did not change
def compute_stability(grid_old, grid_new):
    return np.sum(grid_old == grid_new) / grid_old.size

# Calculate fraction of alive cells
def compute_alive_fraction(grid):
    return np.sum(grid) / grid.size

# Draw text on the right side of the screen
def draw_text(surface, font, label, value, x, y):
    text = font.render(f"{label}: {value}", True, (0, 0, 0))
    surface.blit(text, (x, y))
    return y + 25

# --- Main simulation loop ---
running = True
clock = pygame.time.Clock()
generation = 1

# History containers for plotting later
stability_history = []
alive_history = []
alive_dead_ratio_history = []
stability_std_history = []

prev_grid = grid.copy()

while running:
    clock.tick(SIMULATION_FPS)

    # Check for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update grid state
    grid = update(prev_grid, generation, wraparound)

    # Calculate simulation statistics
    stability = compute_stability(prev_grid, grid)
    alive_fraction = compute_alive_fraction(grid)

    alive_count = int(alive_fraction * grid.size)
    dead_count = grid.size - alive_count
    alive_dead_ratio = alive_count / dead_count if dead_count != 0 else float('inf')

    # Store historical data
    stability_history.append(stability)
    alive_history.append(alive_fraction)
    alive_dead_ratio_history.append(alive_dead_ratio)

    avg_stability = np.mean(stability_history)
    stability_std = np.std(stability_history)

    # --- Drawing the grid and statistics ---
    screen.fill(WHITE)

    # Draw alive cells
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 1:
                pygame.draw.rect(screen, BLACK, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw statistics text
    font = pygame.font.SysFont("Arial", 18)
    x_offset = WIDTH + 10
    y_offset = 20

    y_offset = draw_text(screen, font, "Generation", f"{generation}/{max_generations}", x_offset, y_offset)
    y_offset = draw_text(screen, font, "Current Stability", f"{stability:.4f}", x_offset, y_offset)
    y_offset = draw_text(screen, font, "Average Stability", f"{avg_stability:.4f}", x_offset, y_offset)
    y_offset = draw_text(screen, font, "Stability Std Dev", f"{stability_std:.4f}", x_offset, y_offset)
    y_offset = draw_text(screen, font, "Alive Cells", f"{alive_count}", x_offset, y_offset)
    y_offset = draw_text(screen, font, "Dead Cells", f"{dead_count}", x_offset, y_offset)
    y_offset = draw_text(screen, font, "Alive/Dead Ratio", f"{alive_dead_ratio:.2f}", x_offset, y_offset)

    pygame.display.flip()

    # Update previous grid for next step
    prev_grid = grid.copy()
    generation += 1

    # Stop simulation when max generations reached
    if generation > max_generations:
        running = False

# --- Plotting Results after Simulation ---

# Disable interactive plotting
plt.ioff()

# Ensure output directory exists
os.makedirs("simulation_results", exist_ok=True)

# Plot Stability over Generations
plt.figure(figsize=(10, 5))
plt.plot(stability_history, label="Stability", color='blue')
plt.xlabel("Generation")
plt.ylabel("Stability")
plt.title("Stability Over Generations")
plt.xlim(0, max_generations)
plt.legend()
plt.grid(True)
plt.savefig("simulation_results/stability_plot.png")
plt.close()

# Plot Alive/Dead Ratio over Generations
plt.figure(figsize=(10, 5))
plt.plot(alive_dead_ratio_history, label="Alive/Dead Ratio", color='red')
plt.xlabel("Generation")
plt.ylabel("Alive/Dead Ratio")
plt.title("Alive/Dead Ratio Over Generations")
plt.xlim(0, max_generations)
plt.legend()
plt.grid(True)
plt.savefig("simulation_results/alive_dead_ratio_plot.png")
plt.close()

# --- Keep window open until user closes it manually ---
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting = False

pygame.quit()
sys.exit()















