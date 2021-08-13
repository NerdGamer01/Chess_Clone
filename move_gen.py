from bitboard_functions import print_bb, shift_bb
from constants import anti_diagonal, files, ranks, diagonal
import numpy as np

# Creates diagonal masks, use the index (x+y) to find mask corresponding to a tile
diag = diagonal
diag_mask = np.zeros(15, dtype=np.uint64)
for i in range(8):
    diag_mask[7 - i] = diag
    diag = shift_bb(diag, 'w')

diag = diagonal
for i in range(7):
    diag = shift_bb(diag, 'e')
    diag_mask[8 + i] = diag

# Creates anti diagonal masks, use the index (x-y) to find mask corresponding to a tile
anti_diag = anti_diagonal
anti_diag_mask = np.zeros(15, dtype=np.uint64)
for i in range(8):
    anti_diag_mask[i] = anti_diag
    anti_diag = shift_bb(anti_diag, 'e')

anti_diag = anti_diagonal
for i in range(7):
    anti_diag = shift_bb(anti_diag, 'w')
    anti_diag_mask[14 - i] = anti_diag


# Generates moves for sliding pieces in vertical and horizontal direction
# Movements for sliding pieces are found using kindergarten procedure
def straight_moves(piece, occupied_tiles, lookup_tables):
    file_moves = occupied_tiles & files[piece.tile[0]]

    for i in range(piece.tile[0]):
        file_moves = shift_bb(file_moves, 'w')

    file_moves = (file_moves * diagonal) >> np.uint8(56)
    file_moves = lookup_tables['Bottom_Rank_Moves'][piece.tile[1]][file_moves]
    file_moves = ((file_moves * diagonal) >> np.uint8(7)) & files[0]

    for i in range(piece.tile[0]):
        file_moves = shift_bb(file_moves, 'e')

    rank_moves = occupied_tiles & ranks[piece.tile[1]]

    for i in range(7 - piece.tile[1]):
        rank_moves = shift_bb(rank_moves, 's')

    rank_moves = lookup_tables['Bottom_Rank_Moves'][piece.tile[0]][rank_moves]

    for i in range(7 - piece.tile[1]):
        rank_moves = shift_bb(rank_moves, 'n')

    return rank_moves | file_moves


# Generates diagonal movements
def diagonal_moves(piece, occupied_tiles, lookup_tables):
    diag_moves = occupied_tiles & diag_mask[piece.tile[0] + piece.tile[1]]
    diag_moves = (diag_moves * files[7]) >> np.uint8(56)
    diag_moves = lookup_tables['Bottom_Rank_Moves'][piece.tile[0]][diag_moves]
    diag_moves = (diag_moves * files[7]) & diag_mask[piece.tile[0] + piece.tile[1]]

    anti_diag_moves = occupied_tiles & anti_diag_mask[piece.tile[0] - piece.tile[1]]
    anti_diag_moves = (anti_diag_moves * files[7]) >> np.uint8(56)
    anti_diag_moves = lookup_tables['Bottom_Rank_Moves'][piece.tile[0]][anti_diag_moves]
    anti_diag_moves = (anti_diag_moves * files[7]) & anti_diag_mask[piece.tile[0] - piece.tile[1]]

    return diag_moves | anti_diag_moves


def attack_moves(piece, occupied_tiles, lookup_tables, type=0):
    if type == 0:
        type = piece.type

    if type == 'Pawn':
        bb = lookup_tables[piece.color + '_Pawn_Attacks'][piece.bb_pos_index()]

    elif type == 'King' or type == 'Knight':
        bb = lookup_tables[type + '_Moves'][piece.bb_pos_index()]

    else:
        bb = np.uint64(0)
        if type == 'Rook' or type == 'Queen':
            bb = bb | straight_moves(piece, occupied_tiles, lookup_tables)

        if type == 'Bishop' or type == 'Queen':
            bb = bb | diagonal_moves(piece, occupied_tiles, lookup_tables)

    return bb


# The legal moves are generated via the procedure described here:
# https://peterellisjones.com/posts/generating-legal-chess-moves-efficiently/
def generate_legal_moves(tiles, turn, lookup_tables):
    # The first section extracts the pieces from the tiles libary and sorts well into two lists
    # One for the pieces belonging to whomever turn it is (friendly pieces) and the others (enemy pieces)
    # It also creates all necessary bitboards showing occupied tiles
    white_pieces = []
    black_pieces = []

    for tile in tiles.values():
        if tile != None:
            if tile.color == 'White':
                white_pieces.append(tile)
            else:
                black_pieces.append(tile)

    if turn == 'White':
        friendly_pieces = white_pieces
        enemy_pieces = black_pieces
    else:
        friendly_pieces = black_pieces
        enemy_pieces = white_pieces

    del black_pieces
    del white_pieces

    friendly_pieces_bb = np.uint64(0)
    friendly_pieces_bb_no_king = np.uint64(0)
    friendly_rooks = []
    enemy_pieces_bb = np.uint64(0)
    enemy_pieces_types_bb = {}
    for type in ('King', 'Queen', 'Bishop', 'Knight', 'Rook', 'Pawn'):
        enemy_pieces_types_bb[type] = np.uint64(0)

    for piece in friendly_pieces:
        piece.update_bb()
        friendly_pieces_bb = friendly_pieces_bb | piece.bb

        if piece.type != 'King':
            friendly_pieces_bb_no_king = friendly_pieces_bb_no_king | piece.bb

            if piece.type == 'Rook':
                friendly_rooks.append(piece)

        else:
            friendly_king = piece

    for piece in enemy_pieces:
        piece.update_bb()
        enemy_pieces_bb = enemy_pieces_bb | piece.bb
        enemy_pieces_types_bb[piece.type] = enemy_pieces_types_bb[piece.type] | piece.bb

    occupied_tiles = enemy_pieces_bb | friendly_pieces_bb
    occupied_tiles_no_king = enemy_pieces_bb | friendly_pieces_bb_no_king

    # Creates bitboard of all tiles attacked by the enemy ignoring the friendly king
    # These are then the tiles the king can't move to or it would be in check
    king_danger_tiles = np.uint64(0)
    attacked_tiles = np.uint64(0)

    for piece in enemy_pieces:
        king_danger_tiles = king_danger_tiles | attack_moves(piece, occupied_tiles_no_king, lookup_tables)
        attacked_tiles = attacked_tiles | attack_moves(piece, occupied_tiles, lookup_tables)

    # Next it checks if the player king is in check as if it is the moves the player can make is very limited
    # Also creates bitboard of all pieces putting the king in check
    attackers = np.uint64(0)
    for type in ('King', 'Queen', 'Bishop', 'Knight', 'Rook', 'Pawn'):
        attack = attack_moves(friendly_king, occupied_tiles, lookup_tables, type=type)
        attackers = attackers | (attack & enemy_pieces_types_bb[type])

    # Counts how many pieces are putting the king in check
    num_checks = 0
    for i in '{0:064b}'.format(attackers):
        if i == '1':
            num_checks += 1

    # If the king is in check by more the one piece only the king can move
    if num_checks > 1:
        for piece in friendly_pieces:
            piece.legal_moves = []

        moves = lookup_tables['King_Moves'][friendly_king.bb_pos_index()]
        moves = moves & (~king_danger_tiles) & (~friendly_pieces_bb)
        piece.update_legal_moves(moves)
        return

    elif num_checks == 1:
        check_mask = attackers
        attacking_sliders = attackers & (enemy_pieces_types_bb['Queen'] | enemy_pieces_types_bb['Rook'] | enemy_pieces_types_bb['Bishop'])
        attacking_sliders = '{0:064b}'.format(attacking_sliders)

        for i in range(64):
            if attacking_sliders[i] == '1':
                pos = (i - ((i // 8) * 8), i // 8)
                difference = (pos[0] - friendly_king.tile[0], pos[1] - friendly_king.tile[1])
                direction = ''

                if difference[1] > 0:
                    direction += 'n'
                elif difference[1] < 0:
                    direction += 's'

                if difference[0] < 0:
                    direction += 'e'
                elif difference[0] > 0:
                    direction += 'w'

                if difference[0] >= difference[1]:
                    difference = np.abs(difference[0]) - 1
                else:
                    difference = np.abs(difference[1]) - 1

                bb = tiles[pos].bb()
                for x in range(difference):
                    bb = shift_bb(bb, direction)
                    check_mask = check_mask | bb

    else:
        check_mask = ~np.uint64(0)

    # Finds legal moves
    for piece in friendly_pieces:
        if piece.type == 'Knight':
            moves = lookup_tables['Knight_Moves'][piece.bb_pos_index()] & (~friendly_pieces_bb)
            piece.update_legal_moves(moves)

        elif piece.type == 'King':
            moves = lookup_tables['King_Moves'][friendly_king.bb_pos_index()]
            moves = moves & (~king_danger_tiles) & (~friendly_pieces_bb)

            # Implements castle moves if applicable
            if piece.castle:
                for rook in friendly_rooks:
                    if rook.castle:
                        if rook.tile[0] == 0:
                            gap = (files[1] | files[2] | files[3])

                        else:
                            gap = files[5] | files[6]

                        bb = ((friendly_pieces_bb & gap) | (gap & attacked_tiles)) & ranks[piece.tile[1]]
                        print_bb(gap)
                        if bb == np.uint64(0):
                            moves = moves | rook.bb

            piece.update_legal_moves(moves)
    print_bb(king_danger_tiles)