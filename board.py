from constants import bb_tiles
from bitboard_functions import tile2index, index2tile
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
        self.sides_bb = {'White': np.uint64(0), 'Black': np.uint64(0)}
        self.types_bb = {'White': {}, 'Black': {}}
        self.indices = {'White': {}, 'Black': {}}
        self.turn = turn
        self.en_passant_targets = np.uint64(0)

        for type in ('King', 'Queen', 'Bishop', 'Knight', 'Rook', 'Pawn'):
            self.types_bb['White'][type] = np.uint64(0)
            self.types_bb['Black'][type] = np.uint64(0)

        for piece in tiles.values():
            if piece is not None:
                i = tile2index(piece.tile)

                self.types_bb[piece.color][piece.type] = self.types_bb[piece.color][piece.type] | bb_tiles[i]
                self.indices[piece.color][i] = piece.type
                self.sides_bb[piece.color] = self.sides_bb[piece.color] | bb_tiles[i]

                if piece.type == 'Pawn' and piece.en_passant_target:
                    self.en_passant_targets = self.en_passant_targets | bb_tiles[i]

    def apply_move(self, move):
        if self.turn == 'White':
            enemy_color = 'Black'
        else:
            enemy_color = 'White'

        # removes piece from current position
        type = self.indices[self.turn][move[0]]
        self.types_bb[self.turn][type] = self.types_bb[self.turn][type] & ~bb_tiles[move[0]]
        self.sides_bb[self.turn] = self.sides_bb[self.turn] & ~bb_tiles[move[0]]
        del self.indices[self.turn][move[0]]

        # Deletes caputred enemy pieces
        if self.sides_bb[enemy_color] & ~bb_tiles[move[1]] != self.sides_bb[enemy_color]:
            self.types_bb[enemy_color][self.indices[enemy_color][move[1]]] = \
                self.types_bb[enemy_color][self.indices[enemy_color][move[1]]] & ~bb_tiles[move[1]]
            self.sides_bb[enemy_color] = self.sides_bb[enemy_color] & ~bb_tiles[move[1]]
            del self.indices[enemy_color][move[1]]

        # Puts the piece in its new position
        if move[2] == 'en passant':
            tile = index2tile(move[1])
            if tile[1] == 3:
                destination = tile2index((tile[0], tile[1] - 1))
            else:
                destination = tile2index((tile[0], tile[1] + 1))
        else:
            destination = move[1]

        self.types_bb[self.turn][type] = self.types_bb[self.turn][type] | bb_tiles[destination]
        self.sides_bb[self.turn] = self.sides_bb[self.turn] | bb_tiles[destination]
        self.indices[self.turn][destination] = type

        if type == 'Pawn':
            if np.abs(index2tile(destination)[1] - index2tile(move[0])[1]) == 2:
                self.en_passant_targets = self.en_passant_targets | bb_tiles[move[1]]
            else:
                self.en_passant_targets = self.en_passant_targets & ~bb_tiles[move[1]]

        if self.turn == 'White':
            self.turn = 'Black'
        else:
            self.turn = 'White'

    # evaluation function based on: https://medium.com/dscvitpune/lets-create-a-chess-ai-8542a12afef
    def evaluation(self):
        score = 0

        for i in self.indices['Black']:
            type = self.indices['Black'][i]
            score += (piece_values[type] + black_pos_values[type][i])

        for i in self.indices['White']:
            type = self.indices['White'][i]
            score += (white_pos_values[type][i] - piece_values[type])

        return score
