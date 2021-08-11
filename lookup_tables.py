import numpy as np

# Creates arrays of bitborards where each bit board has a file/rank filled with ones
ranks = np.flip(np.array([np.uint64(0x00000000000000FF) << np.uint8(8 * i) for i in range(8)], dtype=np.uint64))
files = np.flip(np.array([np.uint64(0x0101010101010101) << np.uint8(i) for i in range(8)], dtype=np.uint64))

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

    # Generates rook blocker masks
    lookup_tables['Rook_Blocker_Masks'] = np.zeros(64, dtype=np.uint64)
    for y in range(8):
        for x in range(8):
            lookup_tables['Rook_Blocker_Masks'][y * 8 + x] = ranks[y] ^ files[x]

    # Generates bishop blocker masks
    lookup_tables['Bishop_Blocker_Masks'] = np.zeros(64, dtype=np.uint64)
    diagonal = np.uint64(0x8040201008040201)
    diag_mask = np.zeros(15, dtype=np.uint64)

    for i in range(8):
        diag_mask[i] = diagonal
        diagonal = shift_bb(diagonal, 'e')

    diagonal = np.uint64(0x8040201008040201)
    for i in range(7):
        diagonal = shift_bb(diagonal, 'w')
        diag_mask[14 - i] = diagonal

    anti_diag_mask = np.zeros(15, dtype=np.uint64)
    anti_diagonal = np.uint64(0x0102040810204080)
    for i in range(8):
        anti_diag_mask[7 - i] =  anti_diagonal
        anti_diagonal = shift_bb(anti_diagonal, 'w')

    anti_diagonal = np.uint64(0x0102040810204080)
    for i in range(7):
        anti_diagonal = shift_bb(anti_diagonal, 'e')
        anti_diag_mask[8 + i] = anti_diagonal

    for y in range(8):
        for x in range(8):
            lookup_tables['Bishop_Blocker_Masks'][y * 8 + x] = diag_mask[x - y] ^ anti_diag_mask[x + y]

    # Generates white pawn attack moves
    lookup_tables['White_Pawn_Attacks'] = np.zeros(64, dtype=np.uint64)
    pos = bb_first()

    for i in range(64):
        lookup_tables['White_Pawn_Attacks'][i] = shift_bb(pos,'ne') | shift_bb(pos, 'nw')
        pos = pos >> np.uint8(1)

    # Generates black pawn attack moves
    lookup_tables['Black_Pawn_Attacks'] = np.zeros(64, dtype=np.uint64)
    pos = bb_first()

    for i in range(64):
        lookup_tables['Black_Pawn_Attacks'][i] = shift_bb(pos, 'se') | shift_bb(pos, 'sw')
        pos = pos >> np.uint8(1)


    for i in anti_diag_mask:
        print_bb(i)


    return lookup_tables
