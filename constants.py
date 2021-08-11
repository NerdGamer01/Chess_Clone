import numpy as np

Tile_Size = 80 # Size of chess tiles
Tile_Color = (100, 30, 30) # Color of chess tiles
Origin = (0, 0) # Orgin point of the chess board

# Creates arrays of bitborards where each bit board has a file/rank filled with ones
ranks = np.flip(np.array([np.uint64(0x00000000000000FF) << np.uint8(8 * i) for i in range(8)], dtype=np.uint64))
files = np.flip(np.array([np.uint64(0x0101010101010101) << np.uint8(i) for i in range(8)], dtype=np.uint64))

# Bitboards with the diagonal and anti-diagonal lines filled
diagonal = np.uint64(0x0102040810204080)
anti_diagional = np.uint64(0x0102040810204080)
