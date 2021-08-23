from constants import Window_Size
from lookup_tables import generate_lookup_tables
from game_classes import Board
from menu_classes import Menu, File_Menu
import pygame

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([Window_Size, Window_Size])

clock = pygame.time.Clock()

# Generates lookup tables for the piece movements once when the game is launched
lookup_tables = generate_lookup_tables()

# Variable which determines which window is shown
# 0: Game 1: Main Menu 2: Pause 3: Save Files 4: Load Files 5: Are you sure
window = 1

# Creates the menus
Main_Menu = Menu(['New Game', 'Load Game', 'Quit Game'], center=False, main_menu=True)
Pause_Menu = Menu(['Resume Game', 'Save Game', 'Load Game', 'Main Menu', 'Quit Game'])
Are_You_Sure_Menu = Menu(['Yes', 'No'], center=False, text=['Are you sure you want to quit the game?',
                                                            'All unsaved progress will be lost.'])
Save_File_Menu = File_Menu('save')
Load_File_Menu = File_Menu('load')

# Main game loop
running = True
while running:

    dt = clock.tick(30)

    # Gathering user input
    clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if game:
                previous_window = window
                window = 5
                end_window = 'Quit'
            else:
                running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                if window == 0:
                    window = 2
                elif window == 2:
                    window = 0

    # Updates and draws the windows
    if window == 0:
        board.update(clicked, dt)
        board.draw(screen)

    elif window == 1:
        Main_Menu.draw(screen)
        selected_button = Main_Menu.check_button_press(clicked)

        if selected_button == 'New Game':
            board = Board(lookup_tables, False)
            game = True
            window = 0

        elif selected_button == 'Load Game':
            window = 4
            previous_window = 1

        elif selected_button == 'Quit Game':
            running = False

    elif window == 2:
        Pause_Menu.draw(screen)
        selected_button = Pause_Menu.check_button_press(clicked)

        if selected_button == 'Resume Game':
            window = 0

        elif selected_button == 'Main Menu':
            window = 5
            previous_window = 2
            end_window = 'Main'

        elif selected_button == 'Quit Game':
            window = 5
            previous_window = 2
            end_window = 'Quit'

    elif window == 3:
        Save_File_Menu.draw(screen)

    elif window == 4:
        Load_File_Menu.draw(screen)
        selected_button = Load_File_Menu.check_button_press(clicked)

        if selected_button == 'Cancel':
            window = previous_window

    elif window == 5:
        Are_You_Sure_Menu.draw(screen)
        selected_button = Are_You_Sure_Menu.check_button_press(clicked)

        if selected_button == 'Yes':
            if end_window == 'Main':
                window = 1
                game = False

            elif end_window == 'Quit':
                running = False

        elif selected_button == 'No':
            window = previous_window


    pygame.display.flip()

pygame.quit()
