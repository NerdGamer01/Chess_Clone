from bitboard_functions import shift_bb, index2tile, bit_counter, extract_indices, bitscan, print_bb
from constants import anti_diagonal, files, ranks, diagonal, bb_tiles
from lookup_tables import lookup_tables
from copy import copy
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


def diagonal_moves(i, occupied_bb):
    tile = index2tile(i)

    diag_moves = occupied_bb & diag_mask[tile[0] + tile[1]]
    diag_moves = (diag_moves * files[7]) >> np.uint8(56)
    diag_moves = lookup_tables['Bottom_Rank_Moves'][tile[0]][diag_moves]
    diag_moves = (diag_moves * files[7]) & diag_mask[tile[0] + tile[1]]

    anti_diag_moves = occupied_bb & anti_diag_mask[tile[0] - tile[1]]
    anti_diag_moves = (anti_diag_moves * files[7]) >> np.uint8(56)
    anti_diag_moves = lookup_tables['Bottom_Rank_Moves'][tile[0]][anti_diag_moves]
    anti_diag_moves = (anti_diag_moves * files[7]) & anti_diag_mask[tile[0] - tile[1]]

    return diag_moves | anti_diag_moves

def straight_moves(i, occupied_bb):
    tile = index2tile(i)

    k1 = np.uint64(0xaa00aa00aa00aa00)
    k2 = np.uint64(0xcccc0000cccc0000)
    k3 = np.uint64(0xf0f0f0f00f0f0f0f)

    file_moves = files[0] & (occupied_bb << np.uint8(tile[0]))
    file_moves = (diagonal * file_moves) >> np.uint8(56)
    file_moves = lookup_tables['Bottom_Rank_Moves'][tile[1]][file_moves]

    # FLips it around the anti_diagonal
    t = file_moves ^ (file_moves << np.uint8(36))
    file_moves ^= k3 & (t ^ (file_moves >> np.uint8(36)))
    t = k2 & (file_moves ^ (file_moves << np.uint8(18)))
    file_moves ^= t ^ (t >> np.uint8(18))
    t = k1 & (file_moves ^ (file_moves << np.uint8(9)))
    file_moves ^= t ^ (t >> np.uint8(9))

    # FLips around vertical and moves it back to the correct file
    file_moves = (file_moves << np.uint8(56)) | ((file_moves << np.uint8(40)) & np.uint64(0x00ff000000000000)) \
                 | ((file_moves << np.uint8(24)) & np.uint64(0x0000ff0000000000)) \
                 | ((file_moves << np.uint8(8)) & np.uint64(0x000000ff00000000)) \
                 | ((file_moves >> np.uint8(8)) & np.uint64(0x00000000ff000000)) \
                 | ((file_moves >> np.uint8(24)) & np.uint64(0x0000000000ff0000)) \
                 | ((file_moves >> np.uint8(40)) & np.uint64(0x000000000000ff00)) | (file_moves >> np.uint8(56))

    file_moves = file_moves >> np.uint8(tile[0])

    rank_moves = occupied_bb & ranks[tile[1]]
    rank_moves = rank_moves >> np.uint8(8 * (7 - tile[1]))
    rank_moves = lookup_tables['Bottom_Rank_Moves'][tile[0]][rank_moves]
    rank_moves = rank_moves << np.uint8(8 * (7 - tile[1]))

    return rank_moves | file_moves

# Finds tiles a piece can attack
def attack_moves(i, type, color, occupied_bb):
    if type == 'Pawn':
        bb = lookup_tables[color + '_Pawn_Attacks'][i]

    elif type == 'King' or type == 'Knight':
        bb = lookup_tables[type + '_Moves'][i]

    else:
        bb = np.uint64(0)
        if type != 'Bishop':
            bb = bb | straight_moves(i, occupied_bb)

        if type != 'Rook':
            bb = bb | diagonal_moves(i, occupied_bb)

    return bb

# The legal moves are generated via the procedure described here:
# https://peterellisjones.com/posts/generating-legal-chess-moves-efficiently/
def generate_legal_moves(board):
    moves = []

    # Extracts necessary information
    if board.turn == 'White':
        friendly_index = copy(board.white_indices)
        friendly_bb = board.white_bb
        enemy_index = board.black_indices
        enemy_bb = board.black_bb
        friendly_king_index = board.king_indices['White']
        enemy_color = 'Black'
        enemy_types_bb = board.black_types_bb

    else:
        friendly_index = copy(board.black_indices)
        friendly_bb = board.black_bb
        enemy_index = board.white_indices
        enemy_bb = board.white_bb
        friendly_king_index = board.king_indices['Black']
        enemy_color = 'White'
        enemy_types_bb = board.white_types_bb

    # Creates bitboard of all tiles attacked by the enemy ignoring the friendly king
    # These are then the tiles the king can't move to or it would be in check
    occupied_bb = friendly_bb | enemy_bb
    occupied_no_king_bb = occupied_bb & ~bb_tiles[friendly_king_index]
    king_danger_bb = np.uint64(0)

    for i in enemy_index:
        king_danger_bb = king_danger_bb | attack_moves(i, enemy_index[i], enemy_color, occupied_no_king_bb)

    # Next it checks if the player king is in check as if it is the moves the player can make is very limited
    # Also creates bitboard of all pieces putting the king in check
    checkers = np.uint64(0)
    for type in ('King', 'Queen', 'Bishop', 'Knight', 'Rook', 'Pawn'):
        attack = attack_moves(friendly_king_index, type, enemy_color, occupied_bb)
        checkers = checkers | (attack & enemy_types_bb[type])

    # If the king is in check by more the one piece only the king can move
    num_checkers = bit_counter(checkers)
    if num_checkers > 1:
        moves_bb = lookup_tables['King_Moves'][friendly_king_index] & (~king_danger_bb) & (~friendly_bb)

        for i in extract_indices(moves_bb):
            moves.append((friendly_king_index, i, 'Standard'))

        return moves

    # Being in check limits the number of moves one can make to caputing pieces that put the king in check
    # or blocking sliding pieces which put the king in check
    elif num_checkers == 1:
        i = bitscan(checkers)
        if enemy_index[i] in ('Queen', 'Rook', 'Bishop'):
            push_mask = attack_moves(i, enemy_index[i], enemy_color, occupied_bb)
        else:
            push_mask = np.uint64(0)

    else:
        push_mask = ~np.uint64(0)
        checkers = ~np.uint64(0)

    # Finds all pinned pieces
    pinned_pieces = np.uint64(0)
    sliders_from_king = attack_moves(friendly_king_index, 'Queen', board.turn, occupied_bb)
    king_tile = index2tile(friendly_king_index)

    for type in ('Queen', 'Rook', 'Bishop'):
        for i in extract_indices(enemy_types_bb[type]):
            attack = attack_moves(i, type, enemy_color, occupied_bb)
            attacker_tile = index2tile(i)

            file_pinned = files[attacker_tile[0]] & files[king_tile[0]] & friendly_bb & sliders_from_king & attack
            ranks_pinned = ranks[attacker_tile[1]] & ranks[king_tile[1]] & friendly_bb & sliders_from_king & attack
            diag_pinned = diag_mask[attacker_tile[0] + attacker_tile[1]] & diag_mask[king_tile[0] + king_tile[1]] \
                           & attack & friendly_bb & sliders_from_king
            anti_diag_pinned = anti_diag_mask[attacker_tile[0] - attacker_tile[1]] \
                               & anti_diag_mask[king_tile[0] - king_tile[1]] & attack & friendly_bb & sliders_from_king

            pinned_pieces = pinned_pieces | file_pinned | ranks_pinned | diag_pinned | anti_diag_pinned

    # Uses the now gathered information to find all the legal moves
    for i in friendly_index:
        type = friendly_index[i]
        m = attack_moves(i, type, board.turn, occupied_bb)

        if type == 'Pawn':
            tile = index2tile(i)
            m = m & enemy_bb
            if tile[1] == 1 or tile[1] == 6:
                m = m | (lookup_tables[board.turn + '_Pawn_Moves'][i] & straight_moves(i, occupied_bb) & ~enemy_bb)
            else:
                m = m | (lookup_tables[board.turn + '_Pawn_Moves'][i] & ~enemy_bb)

        if type == 'King':
            m = m & ~king_danger_bb

        else:
            m = m & (push_mask | checkers)

        m = m & ~friendly_bb

        if ~bb_tiles[i] & pinned_pieces != pinned_pieces:
            tile = index2tile(i)
            if ranks[tile[1]] & bb_tiles[friendly_king_index] == bb_tiles[friendly_king_index]:
                m = m & ranks[tile[1]]

            elif files[tile[0]] & bb_tiles[friendly_king_index] == bb_tiles[friendly_king_index]:
                m = m & files[tile[0]]

            elif diag_mask[tile[0] + tile[1]] & bb_tiles[friendly_king_index] == bb_tiles[friendly_king_index]:
                m = m & diag_mask[tile[0] + tile[1]]

            elif anti_diag_mask[tile[0] - tile[1]] & bb_tiles[friendly_king_index] == bb_tiles[friendly_king_index]:
                m = m & diag_mask[tile[0] - tile[1]]

        for j in extract_indices(m):
            moves.append((i, j, 'Standard'))

    return moves