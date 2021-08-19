from constants import Tile_Size, Tile_Color, Window_Size, button_width
import pygame


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
    def __init__(self, text, pos):
        # Creates the images of the button
        self.pos = pos
        self.text = text

        border_width = button_width // 10
        font = pygame.font.SysFont('arial', button_width - (border_width * 4), bold=False)

        self.mouse_not_over_button_image = pygame.Surface((Tile_Size * 3, button_width))
        self.mouse_not_over_button_image.fill((255, 150, 0))
        pygame.draw.rect(self.mouse_not_over_button_image, Tile_Color, (
            border_width, border_width, Tile_Size * 3 - (border_width * 2), button_width - (border_width * 2)))
        textsurface = font.render(text, False, (255, 150, 0))
        size = textsurface.get_size()
        self.mouse_not_over_button_image.blit(textsurface, (
            ((Tile_Size * 3) // 2) - (size[0] // 2), (button_width // 2) - (size[1] // 2)))

        self.mouse_over_button_image = pygame.Surface((Tile_Size * 3, button_width))
        self.mouse_over_button_image.fill((255, 255, 0))
        pygame.draw.rect(self.mouse_over_button_image, Tile_Color, (
            border_width, border_width, Tile_Size * 3 - (border_width * 2), button_width - (border_width * 2)))
        textsurface = font.render(text, False, (255, 255, 0))
        size = textsurface.get_size()
        self.mouse_over_button_image.blit(textsurface, (
            ((Tile_Size * 3) // 2) - (size[0] // 2), (button_width // 2) - (size[1] // 2)))

    def mouse_on_button(self):
        # Checks of the cursor is on the button
        cursor_pos = pygame.mouse.get_pos()

        if cursor_pos[0] > self.pos[0] and cursor_pos[0] < self.pos[0] + (Tile_Size * 3) and \
                cursor_pos[1] > self.pos[1] and cursor_pos[1] < self.pos[1] + button_width:
            return True
        else:
            return False

    def draw(self, screen):
        if self.mouse_on_button():
            screen.blit(self.mouse_over_button_image, self.pos)
        else:
            screen.blit(self.mouse_not_over_button_image, self.pos)
