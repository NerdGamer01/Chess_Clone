from constants import Window_Size
from lookup_tables import generate_lookup_tables
from game_classes import Board
import pygame

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([Window_Size, Window_Size])

clock = pygame.time.Clock()

# Generates lookup tables for the piece movements once when the game is launched
lookup_tables = generate_lookup_tables()

board = Board(lookup_tables, False)

# Main game loop
running = True
while running:

    dt = clock.tick(30)

    # Gathering user input
    clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True

    board.update(clicked, dt)
    board.draw(screen)

    pygame.display.flip()

pygame.quit()

