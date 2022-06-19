from constants import Tile_Size, Origin, Tile_Color, Window_Size, Boarder_Width
from move_gen import generate_legal_moves
from bitboard_functions import index2tile, tile2index
from board import Board
from minimax import AI
import numpy as np
import pygame

# Creates game background
background = pygame.Surface((Window_Size, Window_Size))
background.fill((255, 255, 255))
width = Boarder_Width // 10
pygame.draw.rect(background, (0, 0, 0), pygame.Rect(Origin[0] - width, Origin[1] - width, Tile_Size * 8 + width * 2,
                                                    Tile_Size * 8 + width * 2))
pygame.draw.rect(background, (255, 255, 255), pygame.Rect(Origin[0], Origin[1], Tile_Size * 8, Tile_Size * 8))
pygame.font.init()
font = pygame.font.SysFont('arial', Boarder_Width - width * 3, bold=True)
letters = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')

for i in range(8):
    textsurface = font.render(letters[i], False, (0, 0, 0))
    size = textsurface.get_size()
    background.blit(textsurface, ((Tile_Size // 2) - (size[0] // 2) + Origin[0] + Tile_Size * i, width))
    background.blit(textsurface, (
        (Tile_Size // 2) - (size[0] // 2) + Origin[0] + Tile_Size * i, Boarder_Width + width + Tile_Size * 8))

    textsurface = font.render(str(i + 1), False, (0, 0, 0))
    size = textsurface.get_size()
    background.blit(textsurface, (
        ((Boarder_Width - width) // 2) - (size[0] // 2), (Tile_Size // 2) - (size[1] // 2) + Origin[1] + Tile_Size * i))
    background.blit(textsurface, (((Boarder_Width - width) // 2) - (size[0] // 2) + Origin[0] + Tile_Size * 8 + width,
                                  (Tile_Size // 2) - (size[1] // 2) + Origin[1] + Tile_Size * i))

x = 1
y = 0
while y < 8:
    while x < 8:
        if x >= 0:
            pygame.draw.rect(background, Tile_Color,
                             pygame.Rect(x * Tile_Size + Origin[0], y * Tile_Size + Origin[1], Tile_Size, Tile_Size))
        x += 2
    y += 1
    x -= 9

# Creates movement indicators
target_indicator = pygame.Surface((Tile_Size, Tile_Size), pygame.SRCALPHA, 32)
target_indicator.set_alpha(150)
pygame.draw.circle(target_indicator, (0, 0, 0), (Tile_Size / 2, Tile_Size / 2), (Tile_Size / 2) - (Tile_Size / 40),
                   width=Tile_Size // 10)

tile_indicator = pygame.Surface((Tile_Size, Tile_Size), pygame.SRCALPHA, 32)
tile_indicator.set_alpha(150)
pygame.draw.circle(tile_indicator, (0, 0, 0), (Tile_Size / 2, Tile_Size / 2), Tile_Size // 5)

selected_indicator = pygame.Surface((Tile_Size, Tile_Size), pygame.SRCALPHA, 32)
selected_indicator.fill((255, 255, 0))
selected_indicator.set_alpha(100)


def tile2cor(tile):
    return (tile[0] * Tile_Size + Origin[0], tile[1] * Tile_Size + Origin[1])


def cor2tile(cor):
    return ((cor[0] - Origin[0]) // Tile_Size, (cor[1] - Origin[1]) // Tile_Size)


class Game:
    def __init__(self, lookup_tables, vs_computer, save_file=None):
        self.turn = 'White'  # Which turn it is
        self.selected_piece = None  # The piece currently selected by the player
        self.vs_computer = vs_computer  # Is this a round with or without ai
        self.moving_pieces = []  # All the pieces currently moving and where they are moving to
        self.tiles = {}  # A dictionary containing all the pieces with the tile coordinate as the key
        self.sprites = pygame.sprite.Group()
        self.lookup_tables = lookup_tables
        self.castling = False

        for x in range(8):
            for y in range(8):
                self.tiles[(x, y)] = None

        # Creates a new board if no save_file is loaded
        if save_file == None:
            # Initiates Black Chess Pieces
            piece_order = ['Rook', 'Knight', 'Bishop', 'Queen', 'King', 'Bishop', 'Knight', 'Rook']

            for x in range(8):
                self.tiles[(x, 0)] = Piece(piece_order[x], 'Black', (x, 0))
                self.tiles[(x, 1)] = Piece('Pawn', 'Black', (x, 1))

                self.sprites.add(self.tiles[(x, 0)])
                self.sprites.add(self.tiles[(x, 1)])

            # Initiates White Chess Pieces
            for x in range(8):
                self.tiles[(x, 7)] = Piece(piece_order[x], 'White', (x, 7))
                self.tiles[(x, 6)] = Piece('Pawn', 'White', (x, 6))

                self.sprites.add(self.tiles[(x, 7)])
                self.sprites.add(self.tiles[(x, 6)])

        self.generate_moves()
        self.b = Board(self.tiles, self.turn)

    def update(self, clicked, dt):
        if len(self.moving_pieces) > 0:
            self.update_move(dt)
        else:
            if self.vs_computer and self.turn == 'Black':
                if self.AI.move is not None:
                    self.intiate_movement(self.tiles[index2tile(self.AI.move[0])],
                                          index2tile(self.AI.move[1]), self.AI.move[2])

            elif clicked:
                self.process_player_click()

    def process_player_click(self):
        # Process the player clicking on the board and select/deselects pieces
        if not self.vs_computer or (self.vs_computer and self.turn == 'White'):
            pos = pygame.mouse.get_pos()
            pos = ((pos[0] - Origin[0]) // Tile_Size, (pos[1] - Origin[1]) // Tile_Size)

            if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
                return

            if self.selected_piece is not None and pos in self.selected_piece.legal_moves['Target']:
                i = self.selected_piece.legal_moves['Target'].index(pos)
                self.intiate_movement(self.selected_piece, pos, self.selected_piece.legal_moves['Type'][i])

            elif self.tiles[pos] is not None and self.tiles[pos].color == self.turn:
                self.selected_piece = self.tiles[pos]

            else:
                self.selected_piece = None

    # Starts the movement animation
    def intiate_movement(self, piece, target, type):
        # If the computer is next it already starts calculating its move during animation to save time
        if self.vs_computer and self.turn == 'White':
            self.AI = AI()
            self.AI.board = Board(self.tiles, self.turn)
            self.AI.board.apply_move((tile2index(piece.tile), tile2index(target), type))
            self.AI.start()

        if piece.type == 'Pawn':
            if np.abs(target[1] - piece.tile[1]) == 2:
                piece.en_passant_target = True
            else:
                piece.en_passant_target = False

        if type == 'Standard' or type == 'en passant':
            if type == 'en passant':
                if piece.tile[1] == 3:
                    target = tile2cor((target[0], target[1] - 1))
                else:
                    target = tile2cor((target[0], target[1] + 1))
            else:
                target = tile2cor(target)

            self.moving_pieces.append((piece, target, type))

    # Updates movement animation and when done updates the tiles with the boards new configuration and ends turn
    def update_move(self, dt):
        for p in self.moving_pieces:
            p[0].move(p[1], dt)
            if p[0].completed_movement(p[1]):
                target = cor2tile(p[1])

                if p[2] == 'en passant':
                    if p[0].tile[1] == 3:
                        captured_piece = (target[0], target[1] + 1)
                    else:
                        captured_piece = (target[0], target[1] - 1)

                    self.tiles[captured_piece].kill()
                    self.tiles[captured_piece] = None

                self.moving_pieces.remove(p)
                self.update_tiles(p[0], target)

        if len(self.moving_pieces) == 0:
            self.end_turn()

    def end_turn(self):
        self.selected_piece = None
        self.moving_pieces = []

        if self.turn == 'White':
            self.turn = 'Black'
        else:
            self.turn = 'White'

        self.generate_moves()

    def update_tiles(self, piece, target):
        if self.tiles[target] is not None:
            self.tiles[target].kill()

        self.tiles[target] = piece
        self.tiles[piece.tile] = None
        piece.tile = target

    def generate_moves(self):
        if self.vs_computer and self.turn == 'Black':
            return

        moves = generate_legal_moves(Board(self.tiles, self.turn))

        for piece in self.tiles.values():
            if piece is not None:
                piece.legal_moves = {'Target': [], 'Type': []}

        for m in moves:
            pos = index2tile(m[0])
            self.tiles[pos].legal_moves['Target'].append(index2tile(m[1]))
            self.tiles[pos].legal_moves['Type'].append(m[2])

    def draw(self, screen):
        # Draws Background
        screen.blit(background, (0, 0))

        # Highlights selected piece
        if self.selected_piece is not None:
            screen.blit(selected_indicator, (
                self.selected_piece.tile[0] * Tile_Size + Origin[0],
                self.selected_piece.tile[1] * Tile_Size + Origin[1]))

            # Draws movement indicators
            for tile in self.selected_piece.legal_moves['Target']:
                if self.tiles[tile] == None:
                    screen.blit(tile_indicator, tile2cor(tile))
                else:
                    screen.blit(target_indicator, tile2cor(tile))

        # Draws Chess Pieces
        self.sprites.draw(screen)


# Class for individual chess pieces
class Piece(pygame.sprite.Sprite):
    def __init__(self, type, color, tile):
        super(Piece, self).__init__()
        self.type = type
        self.color = color
        self.tile = tile
        self.castle = True  # Is true if the piece hasent moved yet as only if the pieces havent move can they castle
        self.legal_moves = {'Target': [], 'Type': []}
        self.en_passant_target = False

        # Creates piece image from sprite sheet
        surf = pygame.Surface((Tile_Size, Tile_Size), pygame.SRCALPHA, 32)
        surf = surf.convert_alpha(surf)

        Img = pygame.image.load('Chess_Pieces_Sprite.png')
        Img = pygame.transform.scale(Img, (Tile_Size * 6, Tile_Size * 2))
        i = ['King', 'Queen', 'Bishop', 'Knight', 'Rook', 'Pawn'].index(type)

        if color == 'White':
            surf.blit(Img, (0, 0), (Tile_Size * i, 0, Tile_Size, Tile_Size))
        else:
            surf.blit(Img, (0, 0), (Tile_Size * i, Tile_Size, Tile_Size, Tile_Size))

        self.image = surf
        self.rect = surf.get_rect()
        self.rect.topleft = (tile[0] * Tile_Size + Origin[0], tile[1] * Tile_Size + Origin[1])

    def move(self, target, dt):
        if self.rect.x != target[0] or self.rect.y != target[1]:
            direction_x = target[0] - self.rect.x
            direction_y = target[1] - self.rect.y
            modulus = np.sqrt((direction_y ** 2) + (direction_x ** 2))
            speed = 0.3
            self.rect.x = self.rect.x + ((direction_x * speed * dt) / modulus)
            self.rect.y = self.rect.y + ((direction_y * speed * dt) / modulus)

    def completed_movement(self, target):
        error = 0.06

        if (target[0] - Tile_Size * error <= self.rect.x <= target[0] + Tile_Size * error) and (
                target[1] - Tile_Size * error <= self.rect.y <= target[1] + Tile_Size * error):
            self.rect.x = target[0]
            self.rect.y = target[1]
            return True

        else:
            return False
