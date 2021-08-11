import numpy as np

# Creates arrays of bitborards where each bit board has a file/rank filled with ones
ranks = np.flip(np.array([np.uint64(0x00000000000000FF) << np.uint8(8 * i) for i in range(8)], dtype=np.uint64))
files = np.array([np.uint64(0x0101010101010101) << np.uint8(i) for i in range(8)], dtype=np.uint64)


# Prints a bitboard as a 8x8 board
def print_bb(bb):
    bb = '{0:064b}'.format(bb)
    for i in range(8):
        row = ''
        for j in bb[i * 8:(i * 8 + 8)]:
            row += ' ' + j
        print(row)
    print(' ')


# Shifts a bitboard by one in a given direction
def shift_bb(bb, d):
    if d == 'ne':
        return (bb & ~files[0]) << np.uint8(7)
    elif d == 'n':
        return bb << np.uint8(8)
    elif d == 'nw':
        return (bb & ~files[7]) << np.uint8(9)
    elif d == 'w':
        return (bb & ~files[7]) << np.uint8(1)
    elif d == 'sw':
        return (bb & ~files[7]) >> np.uint8(7)
    elif d == 's':
        return bb >> np.uint8(8)
    elif d == 'se':
        return (bb & ~files[0]) >> np.uint8(9)
    elif d == 'e':
        return (bb & ~files[0]) >> np.uint8(1)


def generate_legal_moves(tiles, turn):
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

    # Creates bitboard of all tiles attacked by the enemy ingorning the friendly king
    # These are then the tiles the king can't move to or it would be in check
    king_danger_tiles = np.uint64(0)

    for piece in enemy_pieces:
        if piece.type == 'Pawn':
            if piece.color == 'White':
                king_danger_tiles = king_danger_tiles | shift_bb(piece.bb, 'n')
                if piece.tile[1] == 6:
                    king_danger_tiles = king_danger_tiles | shift_bb(shift_bb(piece.bb, 'n'), 'n')
            else:
                king_danger_tiles = king_danger_tiles | shift_bb(piece.bb, 's')
                if piece.tile[1] == 1:
                    king_danger_tiles = king_danger_tiles | shift_bb(shift_bb(piece.bb, 's'), 's')

        elif piece.type == 'King':
            for d in ('n', 's', 'e', 'w', 'ne', 'nw', 'sw', 'se'):
                king_danger_tiles = king_danger_tiles | shift_bb(piece.bb, d)

        elif piece.type == 'Knight':
            for d in ('ne', 'se', 'nw', 'se'):
                bb = shift_bb(piece.bb, d)
                king_danger_tiles = king_danger_tiles | shift_bb(bb, d[0]) | shift_bb(bb, d[1])

    # Finds legal moves
    for piece in friendly_pieces:
        moves = np.uint(0)

        if piece.type == 'King':
            for d in ('n', 's', 'e', 'w', 'ne', 'nw', 'sw', 'se'):
                moves = moves | shift_bb(piece.bb, d)
            moves = moves & ~(king_danger_tiles | friendly_pieces_bb)

            piece.update_legal_moves(moves)

    print_bb(king_danger_tiles)
