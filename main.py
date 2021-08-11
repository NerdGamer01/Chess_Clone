from constants import Tile_Size
from game_classes import Board
import pygame

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([Tile_Size * 8, Tile_Size * 8])

clock = pygame.time.Clock()

board = Board(False)

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
