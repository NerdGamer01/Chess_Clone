from constants import Tile_Size, Origin, Tile_Color, Window_Size, Boarder_Width
from move_gen import generate_legal_moves
import numpy as np
import pygame

# Creates background
background = pygame.Surface((Window_Size, Window_Size))
background.fill((255, 255, 255))
width = Boarder_Width // 10
pygame.draw.rect(background, (0, 0, 0), pygame.Rect(Origin[0] - width, Origin[1] - width, Tile_Size * 8 + width * 2,
                                                    Tile_Size * 8 + width * 2))
pygame.draw.rect(background, (255, 255, 255), pygame.Rect(Origin[0], Origin[1], Tile_Size * 8, Tile_Size * 8))
pygame.font.init()
myfont = pygame.font.SysFont('arial', Boarder_Width - width * 3, bold=True)
letters = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')

for i in range(8):
    textsurface = myfont.render(letters[i], False, (0, 0, 0))
    size = textsurface.get_size()
    background.blit(textsurface, ((Tile_Size // 2) - (size[0] // 2) + Origin[0] + Tile_Size * i, width))
    background.blit(textsurface, (
    (Tile_Size // 2) - (size[0] // 2) + Origin[0] + Tile_Size * i, Boarder_Width + width + Tile_Size * 8))

    textsurface = myfont.render(str(i + 1), False, (0, 0, 0))
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


class Board:
    def __init__(self, lookup_tables, AI, save_file=None):
        self.turn = 'White'  # Which turn it is
        self.selected_piece = None  # The piece currently selected by the player
        self.AI = AI  # Is this a round with or without ai
        self.moving_piece = False  # Is a piece currently moving
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

        generate_legal_moves(self.tiles, self.turn, lookup_tables)

    def update(self, clicked, dt):
        if clicked and not self.moving_piece:
            self.select_piece()

        elif self.moving_piece:
            self.update_move(dt)

    def select_piece(self):
        # Process the player clicking on the board and select/deselects pieces
        # Also initiates a move if applicable
        if not self.AI or (self.AI and self.turn == 'White'):
            pos = pygame.mouse.get_pos()
            pos = ((pos[0] - Origin[0]) // Tile_Size, (pos[1] - Origin[1]) // Tile_Size)

            if self.selected_piece != None and self.selected_piece.type == 'King' and pos in self.selected_piece.legal_moves and \
                    self.tiles[pos] != None and self.tiles[pos].color == self.turn:
                self.moving_piece = True
                self.castling = True
                self.castling_rook = self.tiles[pos]
                self.castling_rook.castle = False
                self.selected_piece.castle = False

                if self.castling_rook.tile[0] == 0:
                    self.target = (2, self.selected_piece.tile[1])
                    self.castling_rook_target = (3, self.castling_rook.tile[1])
                else:
                    self.target = (6, self.selected_piece.tile[1])
                    self.castling_rook_target = (5, self.castling_rook.tile[1])

                self.target = (self.target[0] * Tile_Size + Origin[0], self.target[1] * Tile_Size + Origin[1])
                self.castling_rook_target = (self.castling_rook_target[0] * Tile_Size + Origin[0],
                                             self.castling_rook_target[1] * Tile_Size + Origin[1])

            elif self.tiles[pos] != None and self.tiles[pos].color == self.turn:
                self.selected_piece = self.tiles[pos]

            elif self.selected_piece != None and pos in self.selected_piece.legal_moves:
                self.moving_piece = True
                self.target = (pos[0] * Tile_Size + Origin[0], pos[1] * Tile_Size + Origin[1])
                self.selected_piece.castle = False

            else:
                self.selected_piece = None

    def update_move(self, dt):
        # Updates movement animation and when done updates the tiles with the boards new configuration and ends turn
        self.selected_piece.move(self.target, dt)

        if self.castling:
            self.castling_rook.move(self.castling_rook_target, dt)

            if self.castling_rook.completed_movement(self.castling_rook_target):
                self.castling_rook_target = ((self.castling_rook_target[0] - Origin[0]) // Tile_Size,
                                             (self.castling_rook_target[1] - Origin[1]) // Tile_Size)
                self.castling = False
                self.update_tiles(self.castling_rook, self.castling_rook_target)

        if self.selected_piece.completed_movement(self.target) and not self.castling:
            self.target = ((self.target[0] - Origin[0]) // Tile_Size, (self.target[1] - Origin[1]) // Tile_Size)

            if self.tiles[self.target] != None:
                self.tiles[self.target].kill()

            self.update_tiles(self.selected_piece, self.target)
            self.end_turn()

    def end_turn(self):
        self.selected_piece = None
        self.moving_piece = False

        if self.turn == 'White':
            self.turn = 'Black'
        else:
            self.turn = 'White'

        generate_legal_moves(self.tiles, self.turn, self.lookup_tables)

    def update_tiles(self, piece, target):
        self.tiles[target] = piece
        self.tiles[piece.tile] = None
        piece.tile = target

    def draw(self, screen):
        # Draws Background
        screen.blit(background, (0, 0))

        # Highlights selected piece
        if self.selected_piece != None:
            screen.blit(selected_indicator, (
                self.selected_piece.tile[0] * Tile_Size + Origin[0],
                self.selected_piece.tile[1] * Tile_Size + Origin[1]))

        # Draws Chess Pieces
        self.sprites.draw(screen)

        # Draws movement indicators
        if self.selected_piece != None:
            for tile in self.selected_piece.legal_moves:
                if self.tiles[tile] == None:
                    screen.blit(tile_indicator, (tile[0] * Tile_Size + Origin[0], tile[1] * Tile_Size + Origin[1]))
                else:
                    screen.blit(target_indicator, (tile[0] * Tile_Size + Origin[0], tile[1] * Tile_Size + Origin[1]))


# Class for individual chess pieces
class Piece(pygame.sprite.Sprite):
    def __init__(self, type, color, tile):
        super(Piece, self).__init__()
        self.type = type
        self.color = color
        self.tile = tile
        self.castle = True  # Is true if the piece hasent moved yet as only  if the pieces havent move can they castle
        self.legal_moves = [(3, 3), (0, 1), (6, 5), (4, 4), (1, 3)]

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

        if (target[0] - Tile_Size * error <= self.rect.x and target[0] + Tile_Size * error >= self.rect.x) and (
                target[1] - Tile_Size * error <= self.rect.y and target[1] + Tile_Size * error >= self.rect.y):
            self.rect.x = target[0]
            self.rect.y = target[1]
            return True

        else:
            return False

    def update_bb(self):
        bb = ['0'] * 64
        bb[self.bb_pos_index()] = '1'
        bb = ''.join(bb)
        self.bb = np.uint64(int(bb, 2))
        self.pinned_mask = ~np.uint64(0)

    # Return index for pieces position on a bitboard
    def bb_pos_index(self):
        return self.tile[1] * 8 + self.tile[0]

    def update_legal_moves(self, bb):
        bb = '{0:064b}'.format(bb)
        self.legal_moves = []
        for i in range(64):
            if bb[i] == '1':
                self.legal_moves.append((i - (8 * (i // 8)), i // 8))
