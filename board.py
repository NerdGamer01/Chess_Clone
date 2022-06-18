from constants import bb_tiles
from bitboard_functions import tile2index
import numpy as np

# Tables for the value of a given position used in evaluation function
# These tables are for black pieces, for white the tables would be the flipped negative of these
black_pos_values = {}

black_pos_values['Pawn'] = np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    100, 100, 100, 100, 100, 100, 100, 100])

black_pos_values['Knight'] = np.array([
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50])

black_pos_values['Bishop'] = np.array([
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20])

black_pos_values['Rook'] = np.array([
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0])

black_pos_values['Queen'] = np.array([
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 5, 5, 5, 5, 5, 0, -10,
    0, 0, 5, 5, 5, 5, 0, -5,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20])

black_pos_values['King'] = np.array([
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30])

white_pos_values = {}
for type in black_pos_values:
    white_pos_values[type] = -np.flip(black_pos_values[type])

piece_values = {'Pawn': 50, 'Knight': 160, 'Bishop': 170, 'Rook': 250, 'Queen': 450, 'King': 5000}


# Representation of the board in terms of bitboards and indices needed for move generation and AI
class Board:
    def __init__(self, tiles, turn):
        self.white_bb = np.uint64(0)
        self.black_bb = np.uint64(0)
        self.white_types_bb = {}
        self.black_types_bb = {}
        self.white_indices = {}
        self.black_indices = {}
        self.turn = turn
        self.king_indices = {}

        for type in ('King', 'Queen', 'Bishop', 'Knight', 'Rook', 'Pawn'):
            self.white_types_bb[type] = np.uint64(0)
            self.black_types_bb[type] = np.uint64(0)

        for piece in tiles.values():
            if piece != None:
                if piece.color == 'White':
                    i = tile2index(piece.tile)
                    self.white_types_bb[piece.type] = self.white_types_bb[piece.type] | bb_tiles[i]
                    self.white_indices[i] = piece.type
                    self.white_bb = self.white_bb | bb_tiles[i]

                else:
                    i = tile2index(piece.tile)
                    self.black_types_bb[piece.type] = self.black_types_bb[piece.type] | bb_tiles[i]
                    self.black_indices[i] = piece.type
                    self.black_bb = self.black_bb | bb_tiles[i]

                if piece.type == 'King':
                    self.king_indices[piece.color] = tile2index(piece.tile)

    def apply_move(self, move):
        if self.turn == 'White':
            type = self.white_indices[move[0]]
            self.white_types_bb[type] = self.white_types_bb[type] & ~bb_tiles[move[0]]
            self.white_types_bb[type] = self.white_types_bb[type] | bb_tiles[move[1]]

            self.white_bb = self.white_bb & ~bb_tiles[move[0]]
            self.white_bb = self.white_bb | bb_tiles[move[1]]

            self.white_indices[move[1]] = type
            del self.white_indices[move[0]]

            if self.black_bb & ~bb_tiles[move[1]] != self.black_bb:
                self.black_types_bb[self.black_indices[move[1]]] = \
                    self.black_types_bb[self.black_indices[move[1]]] & ~bb_tiles[move[1]]
                self.black_bb = self.black_bb & ~bb_tiles[move[1]]
                del self.black_indices[move[1]]

        else:
            type = self.black_indices[move[0]]
            self.black_types_bb[type] = self.black_types_bb[type] & ~bb_tiles[move[0]]
            self.black_types_bb[type] = self.black_types_bb[type] | bb_tiles[move[1]]

            self.black_bb = self.black_bb & ~bb_tiles[move[0]]
            self.black_bb = self.black_bb | bb_tiles[move[1]]

            self.black_indices[move[1]] = type
            del self.black_indices[move[0]]

            if self.white_bb & ~bb_tiles[move[1]] != self.white_bb:
                self.white_bb = self.white_bb & ~bb_tiles[move[1]]
                self.white_types_bb[self.white_indices[move[1]]] = \
                    self.white_types_bb[self.white_indices[move[1]]] & ~bb_tiles[move[1]]
                del self.white_indices[move[1]]

    # evaluation function based on: https://medium.com/dscvitpune/lets-create-a-chess-ai-8542a12afef
    def evaluation(self):
        score = 0

        for i in self.black_indices:
            type = self.black_indices[i]
            score += (piece_values[type] + black_pos_values[type][i])

        for i in self.white_indices:
            type = self.white_indices[i]
            score += (white_pos_values[type][i] - piece_values[type])

        return score
