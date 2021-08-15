from constants import files
import numpy as np

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


# Prints a bitboard as a 8x8 board
def print_bb(bb):
    bb = '{0:064b}'.format(bb)
    for i in range(8):
        row = ''
        for j in bb[i * 8:(i * 8 + 8)]:
            row += ' ' + j
        print(row)
    print(' ')
