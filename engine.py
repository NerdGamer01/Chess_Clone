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

def attack_moves(piece, occupied_tiles, lookup_tables,type=0):
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

        if piece.type == 'Bishop' or type == 'Queen':
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
    enemy_pieces_bb = np.uint64(0)
    enemy_pieces_types_bb = {}
    for type in ('King', 'Queen', 'Bishop', 'Knight', 'Rook', 'Pawn'):
        enemy_pieces_types_bb[type] = np.uint64(0)

    for piece in friendly_pieces:
        piece.update_bb()
        friendly_pieces_bb = friendly_pieces_bb | piece.bb

        if piece.type != 'King':
            friendly_pieces_bb_no_king = friendly_pieces_bb_no_king | piece.bb
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

    for piece in enemy_pieces:
        king_danger_tiles = king_danger_tiles | attack_moves(piece,occupied_tiles_no_king,lookup_tables)

    # Finds legal moves for king
    moves = lookup_tables['King_Moves'][friendly_king.bb_pos_index()]
    moves = moves & (~king_danger_tiles) & (~friendly_pieces_bb)
    piece.update_legal_moves(moves)

    # Next it checks if the player king is in check as if it is the moves the player can make is very limited
    # Also creates bitboard of all pieces putting the king in check
    attackers = np.uint64(0)
    for type in ('King', 'Queen', 'Bishop', 'Knight', 'Rook', 'Pawn'):
        attack = attack_moves(piece, occupied_tiles, lookup_tables, type=type)
        attackers = attackers | (attack & enemy_pieces_types_bb[type])

    # Counts how many pieces are putting the king in check
    num_checks = 0
    for i in '{0:064b}'.format(attackers):
        if i == '1':
            num_checks += 1

    # If the king is in check by more the one piece only the king can move
    if num_checks > 1:
        return
    elif num_checks == 1:
        pass

    # Finds legal moves
    for piece in friendly_pieces:
        if piece.type == 'Knight':
            moves = lookup_tables['Knight_Moves'][piece.bb_pos_index()] & (~friendly_pieces_bb)
            piece.update_legal_moves(moves)

    print_bb(king_danger_tiles)
