from bitboard_functions import print_bb, shift_bb
from constants import anti_diagonal, files, ranks, diagonal
import numpy as np

# Generates moves for sliding pieces in vertical and horizontal direction
# Movements for sliding pieces are found using kindergarten procedure
def straight_moves(piece, occupied_tiles, lookup_tables):
    file_moves = occupied_tiles & files[piece.tile[0]]

    for i in range(piece.tile[0]):
        file_moves = shift_bb(file_moves, 'w')

    file_moves = (file_moves * anti_diagonal) >> np.uint8(56)
    file_moves = lookup_tables['Bottom_Rank_Moves'][piece.tile[1]][file_moves]
    file_moves = ((file_moves * anti_diagonal) >> np.uint8(7)) & files[0]

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

    diag_moves = occupied_tiles & diag_mask[piece.tile[0] + piece.tile[1]]
    diag_moves = (diag_moves * files[7]) >> np.uint8(56)
    diag_moves = lookup_tables['Bottom_Rank_Moves'][piece.tile[0]][diag_moves]
    diag_moves = (diag_moves * files[7]) & diag_mask[piece.tile[0] + piece.tile[1]]

    return diag_moves



def generate_legal_moves(tiles, turn, lookup_tables):
    # This code extracts the pieces from the tiles libary and sorts well into two lists
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

    for piece in friendly_pieces:
        piece.update_bb()
        friendly_pieces_bb = friendly_pieces_bb | piece.bb

        if piece.type != 'King':
            friendly_pieces_bb_no_king = friendly_pieces_bb_no_king | piece.bb

    for piece in enemy_pieces:
        piece.update_bb()
        enemy_pieces_bb = enemy_pieces_bb | piece.bb

    occupied_tiles_no_king = enemy_pieces_bb | friendly_pieces_bb_no_king

    # Creates bitboard of all tiles attacked by the enemy ignoring the friendly king
    # These are then the tiles the king can't move to or it would be in check
    king_danger_tiles = np.uint64(0)

    for piece in enemy_pieces:
        if piece.type == 'Pawn':
            king_danger_tiles = king_danger_tiles | lookup_tables[piece.color + '_' + piece.type + '_Attacks'][piece.bb_pos_index()]

        elif piece.type == 'King' or piece.type == 'Knight':
            king_danger_tiles = king_danger_tiles | lookup_tables[piece.type + '_Moves'][piece.bb_pos_index()]

        elif piece.type == 'Rook' or piece.type == 'Queen':
            king_danger_tiles = king_danger_tiles | straight_moves(piece, occupied_tiles_no_king, lookup_tables)

        elif piece.type == 'Bishop' or piece.type == 'Queen':
            king_danger_tiles = king_danger_tiles | diagonal_moves(piece, occupied_tiles_no_king, lookup_tables)



    # Finds legal moves
    for piece in friendly_pieces:
        moves = np.uint64(0)

        if piece.type == 'King':
            moves = lookup_tables['King_Moves'][piece.bb_pos_index()]
            moves = moves & (~king_danger_tiles) & (~friendly_pieces_bb)

            piece.update_legal_moves(moves)

        elif piece.type == 'Knight':
            moves = lookup_tables['Knight_Moves'][piece.bb_pos_index()] & (~friendly_pieces_bb)
            piece.update_legal_moves(moves)

    print_bb(king_danger_tiles)
