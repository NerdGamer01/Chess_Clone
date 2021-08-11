from constants import files, ranks
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


# Return bitboard with first bit being one and the rest being zero
def bb_first():
    pos = ['0'] * 64
    pos[0] = '1'
    return np.uint64(int(''.join(pos), 2))


# Generates the attack bitboards for every piece for every possible location
def generate_lookup_tables():
    lookup_tables = {}

    # First generates king moves
    lookup_tables['King_Moves'] = np.zeros(64, dtype=np.uint64)
    pos = bb_first()

    for i in range(64):
        bb = np.uint64(0)
        for d in ('n', 's', 'e', 'w', 'ne', 'nw', 'sw', 'se'):
            bb = bb | shift_bb(pos, d)
        pos = pos >> np.uint8(1)
        lookup_tables['King_Moves'][i] = bb

    # Next generates knight moves
    lookup_tables['Knight_Moves'] = np.zeros(64, dtype=np.uint64)
    pos = bb_first()

    for i in range(64):
        bb = np.uint64(0)
        for d in ('ne', 'se', 'nw', 'sw'):
            a = shift_bb(pos, d)
            bb = bb | shift_bb(a, d[0]) | shift_bb(a, d[1])
        pos = pos >> np.uint8(1)
        lookup_tables['Knight_Moves'][i] = bb

    # Generates white pawn attack moves
    lookup_tables['White_Pawn_Attacks'] = np.zeros(64, dtype=np.uint64)
    pos = bb_first()

    for i in range(64):
        lookup_tables['White_Pawn_Attacks'][i] = shift_bb(pos, 'ne') | shift_bb(pos, 'nw')
        pos = pos >> np.uint8(1)

    # Generates black pawn attack moves
    lookup_tables['Black_Pawn_Attacks'] = np.zeros(64, dtype=np.uint64)
    pos = bb_first()

    for i in range(64):
        lookup_tables['Black_Pawn_Attacks'][i] = shift_bb(pos, 'se') | shift_bb(pos, 'sw')
        pos = pos >> np.uint8(1)

    # Generates bottom rank moves for kindergarten approach for sliding pieces
    lookup_tables['Bottom_Rank_Moves'] = np.zeros((8, 256), dtype=np.uint64)
    empty = np.uint8(0)
    one = np.uint8(1)

    for occupied in range(256):
        for i in range(8):
            occupied = np.uint8(occupied)
            i = np.uint8(i)
            x = one << np.uint8(7) - i
            if (x & occupied) == empty:
                continue

            left_attack = x
            left_move = empty

            while left_attack != empty:
                left_attack = left_attack << one
                left_move = left_attack | left_move
                if (left_attack & occupied) != empty:
                    break

            right_attack = x
            right_move = empty

            while right_attack != empty:
                right_attack = right_attack >> one
                right_move = right_move | right_attack
                if (right_attack & occupied) != empty:
                    break

            lookup_tables['Bottom_Rank_Moves'][i][occupied] = left_move | right_move

    return lookup_tables
