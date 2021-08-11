from lookup_tables import print_bb
import numpy as np

A1H8_diag = np.uint64(0x8040201008040201)
H1A8_antidiag = np.uint64(0x0102040810204080)


def generate_legal_moves(tiles, turn, lookup_tables):
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

    occupied_tiles_bb = enemy_pieces_bb | friendly_pieces_bb

    # Creates bitboard of all tiles attacked by the enemy ingorning the friendly king
    # These are then the tiles the king can't move to or it would be in check
    king_danger_tiles = np.uint64(0)

    for piece in enemy_pieces:
        if piece.type == 'Pawn':
            king_danger_tiles = king_danger_tiles | lookup_tables[piece.color + '_' + piece.type + '_Attacks'][piece.bb_pos_index()]

        elif piece.type == 'King' or piece.type == 'Knight':
            king_danger_tiles = king_danger_tiles | lookup_tables[piece.type + '_Moves'][piece.bb_pos_index()]



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
