import pygame
import pygame_menu
import subprocess
import sys

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Select Simulation")
clock = pygame.time.Clock()

def run_simulation(simulation):
    # Run the selected simulation and wait for it to finish
    if config["simulation"] == "Cellular Automaton":
        subprocess.call(["Cellular_Automaton.exe"])
    elif config["simulation"] == "Gliders":
        subprocess.call(["Gliders.exe"])
    elif config["simulation"] == "Special":
        subprocess.call(["Special.exe"])


# Infinite loop until user chooses to quit
while True:
    config = {
        "simulation": "Cellular Automaton"
    }

    # Callback to update selected simulation
    def set_simulation(value, simulation_name):
        config["simulation"] = simulation_name

    # Start flag
    def start_simulation():
        global start_flag
        start_flag = True

    # Create the menu
    menu = pygame_menu.Menu('Select Simulation', 600, 400, theme=pygame_menu.themes.THEME_SOLARIZED)
    menu.add.selector('Simulation Type:', [
        ('Cellular Automaton', 'Cellular Automaton'), 
        ('Gliders', 'Gliders'), 
        ('Special', 'Special')], onchange=set_simulation)

    menu.add.button('Start Simulation', start_simulation)
    menu.add.button('Quit', pygame_menu.events.EXIT)

    start_flag = False

    # Menu loop
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

    pygame.quit()  # Close the menu window

    # Run the selected simulation (will wait until it finishes)
    run_simulation(config["simulation"])

    # Reinitialize Pygame for returning to the menu
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Select Simulation")
    clock = pygame.time.Clock()





