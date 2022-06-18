from constants import files, bb_tiles
import numpy as np

debruijn = np.uint64(0x03f79d71b4cb0a89)

lookup = np.array(
        [ 0,  1, 48,  2, 57, 49, 28,  3,
         61, 58, 50, 42, 38, 29, 17,  4,
         62, 55, 59, 36, 53, 51, 43, 22,
         45, 39, 33, 30, 24, 18, 12,  5,
         63, 47, 56, 27, 60, 41, 37, 16,
         54, 35, 52, 21, 44, 32, 23, 11,
         46, 26, 40, 15, 34, 20, 31, 10,
         25, 14, 19,  9, 13,  8,  7,  6],
        dtype=np.uint8)

# Shifts a bitboard by one in a given direction
def shift_bb(bb, d):
    if d == 'ne':
        return (bb & ~files[7]) << np.uint8(7)
    elif d == 'n':
        return bb << np.uint8(8)
    elif d == 'nw':
        return (bb & ~files[0]) << np.uint8(9)
    elif d == 'w':
        return (bb & ~files[0]) << np.uint8(1)
    elif d == 'sw':
        return (bb & ~files[0]) >> np.uint8(7)
    elif d == 's':
        return bb >> np.uint8(8)
    elif d == 'se':
        return (bb & ~files[7]) >> np.uint8(9)
    elif d == 'e':
        return (bb & ~files[7]) >> np.uint8(1)

def bitscan(bb):
    return 63 - lookup[((bb & -bb) * debruijn) >> np.uint8(58)]

def extract_indices(bb):
    indices = []
    while bb != np.uint64(0):
        indices.append(bitscan(bb))
        bb = bb & ~bb_tiles[indices[-1]]

    return indices

# Counts the number of 1s in a bitboard
def bit_counter(bb, n = 0):
    if bb != np.uint64(0):
        n = bit_counter(bb & ~bb_tiles[bitscan(bb)], n + 1)
    return n

# Converts a tile coordinate to a bitboard index
def tile2index(tile):
    return tile[0] + (tile[1] * 8)

# Converts a bitboard index to a tile coordinate
def index2tile(i):
    y = i // 8
    return (i - (y * 8), y)

# Prints a bitboard as a 8x8 board
def print_bb(bb):
    bb = '{0:064b}'.format(bb)
    for i in range(8):
        row = ''
        for j in bb[i * 8:(i * 8 + 8)]:
            row += ' ' + j
        print(row)
    print(' ')