from constants import Tile_Size, Tile_Color, Window_Size, button_width, slot_width
import pygame
import os
import csv


class Menu:
    def __init__(self, buttons, center=True, main_menu=False, text=None):
        # Creates Buttons
        self.buttons = []
        num_of_buttons = len(buttons)
        buttons_spacing = (button_width // 3) + button_width
        width = (buttons_spacing * num_of_buttons) // 2

        # Determines weather buttons are at the center of bottom of the window
        if center:
            button_location = Window_Size // 2
        else:
            button_location = (Window_Size // 3) * 2

        for i in range(num_of_buttons):
            pos = ((Window_Size // 2) - ((Tile_Size * 3) // 2), (button_location - width + (i * buttons_spacing)))
            self.buttons.append(Button(buttons[i], pos))

        # Creates the header image of the main menu
        if main_menu:
            Img = pygame.image.load('Chess_Pieces_Sprite.png')
            piece_size = Window_Size // 5
            Img = pygame.transform.scale(Img, (piece_size * 6, piece_size * 2))

            self.header = pygame.Surface((Window_Size, Window_Size // 5))
            self.header.fill((255, 255, 255))

            font = pygame.font.SysFont('arial', Window_Size // 5, bold=True)
            textsurface = font.render('CHESS', False, Tile_Color)

            width = textsurface.get_size()[0]

            side = (Window_Size // 2) - (width // 2)

            self.header.blit(textsurface, (side, 0))

            self.header.blit(Img, ((side // 2) - (piece_size // 2), 0), (0, 0, piece_size, piece_size))
            self.header.blit(Img, (Window_Size - (side // 2) - (piece_size // 2), 0),
                             (0, piece_size, piece_size, piece_size))

            self.title = 0

        # Creates header text
        elif text != None:
            self.header = pygame.Surface((Window_Size, (Window_Size // 16) * len(text)))
            self.header.fill((255, 255, 255))
            font = pygame.font.SysFont('arial', Window_Size // 20, bold=True)

            for i in range(len(text)):
                textsurface = font.render(text[i], False, Tile_Color)
                size = textsurface.get_size()
                self.header.blit(textsurface, ((Window_Size // 2) - (size[0] // 2), (Window_Size // 18) * i))

            self.title = 1

        else:
            self.title = 2

    def check_button_press(self, clicked):
        # Checks if the player clicked on of the buttons and if yes returns which one
        if clicked:
            for button in self.buttons:
                if button.mouse_on_button():
                    return button.text

    def draw(self, screen):
        screen.fill((255, 255, 255))
        for button in self.buttons:
            button.draw(screen)

        if self.title == 0:
            screen.blit(self.header, (0, (Window_Size // 4) - (Window_Size // 10)))

        elif self.title == 1:
            size = self.header.get_size()
            screen.blit(self.header, (0, (Window_Size // 3) - (size[1] // 2)))


class Button:
    def __init__(self, text, pos, length=3):
        # Creates the images of the button
        self.pos = pos
        self.text = text
        self.length = Tile_Size * length

        border_width = button_width // 10
        font = pygame.font.SysFont('arial', button_width - (border_width * 4), bold=False)

        self.mouse_not_over_button_image = pygame.Surface((self.length, button_width))
        self.mouse_not_over_button_image.fill((255, 150, 0))
        pygame.draw.rect(self.mouse_not_over_button_image, Tile_Color, (
            border_width, border_width, self.length - (border_width * 2), button_width - (border_width * 2)))
        textsurface = font.render(text, False, (255, 150, 0))
        size = textsurface.get_size()
        self.mouse_not_over_button_image.blit(textsurface, (
            (self.length // 2) - (size[0] // 2), (button_width // 2) - (size[1] // 2)))

        self.mouse_over_button_image = pygame.Surface((self.length, button_width))
        self.mouse_over_button_image.fill((255, 255, 0))
        pygame.draw.rect(self.mouse_over_button_image, Tile_Color, (
            border_width, border_width, self.length - (border_width * 2), button_width - (border_width * 2)))
        textsurface = font.render(text, False, (255, 255, 0))
        size = textsurface.get_size()
        self.mouse_over_button_image.blit(textsurface, (
            (self.length // 2) - (size[0] // 2), (button_width // 2) - (size[1] // 2)))

    def mouse_on_button(self):
        # Checks of the cursor is on the button
        cursor_pos = pygame.mouse.get_pos()

        if self.pos[0] < cursor_pos[0] < self.pos[0] + self.length and \
                self.pos[1] < cursor_pos[1] < self.pos[1] + button_width:
            return True
        else:
            return False

    def draw(self, screen):
        if self.mouse_on_button():
            screen.blit(self.mouse_over_button_image, self.pos)
        else:
            screen.blit(self.mouse_not_over_button_image, self.pos)


class File_Menu:
    def __init__(self, type):
        self.save_slots = []
        self.buttons = []

        self.button_bar_width = button_width + (button_width // 2)

        button_spacing = (Window_Size - (Tile_Size * 6)) // 4

        print((Window_Size - self.button_bar_width) // 3)

        if type == 'save':
            buttons = ('Save', 'Delete', 'Cancel')
        else:
            buttons = ('Load', 'Delete', 'Cancel')

        for i in range(len(buttons)):
            self.buttons.append(Button(buttons[i], (
            button_spacing + i * (Tile_Size * 2 + button_spacing), Window_Size - button_width - (button_width // 4)),
                                       length=2))

        slot_x_border = (Window_Size - (Tile_Size * 8)) // 3
        slot_y_border = ((Window_Size - self.button_bar_width) - (slot_width * 3)) // 3
        slot_spacing = slot_x_border + slot_width

        for i in range(3):
            self.save_slots.append(Save_Slot(2 * i + 1, (slot_x_border, slot_y_border + i * slot_spacing)))
            self.save_slots.append(Save_Slot(2 * i + 2,
                                             ((slot_x_border * 2) + (Tile_Size * 4), slot_y_border + i * slot_spacing)))

    def check_button_press(self, clicked):
        # Checks if the player clicked on of the buttons and if yes returns which one
        if clicked:
            for button in self.buttons:
                if button.mouse_on_button():
                    if button.text == 'Cancel':
                        return button.text

    def draw(self, screen):
        screen.fill((255, 255, 255))

        for slot in self.save_slots:
            slot.draw(screen)

        for button in self.buttons:
            button.draw(screen)


class Save_Slot:
    def __init__(self, num, pos):
        self.pos = pos
        self.num = num
        border_width = slot_width // 20

        self.image_not_selected = pygame.Surface((Tile_Size * 4, slot_width))
        self.image_not_selected.fill(Tile_Color)
        pygame.draw.rect(self.image_not_selected, (255, 255, 255), (
        border_width, border_width, Tile_Size * 4 - (border_width * 2), slot_width - (border_width * 2)))


    def draw(self, screen):
        screen.blit(self.image_not_selected, self.pos)
