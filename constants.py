import numpy as np
from helpers import *

ZERO_STRING = "0000000000000000000000000000000000000000000000000000000000000000"
FILE_A=np.uint64(72340172838076673)
FILE_H=np.uint64(-9187201950435737472)
FILE_AB=np.uint64(217020518514230019)
FILE_GH=np.uint64(-4557430888798830400)
RANK_1=np.uint64(-72057594037927936)
RANK_4=np.uint64(1095216660480)
RANK_5=np.uint64(4278190080)
RANK_8=np.uint64(255)
KNIGHT_SPAN = strBBtoBB("""
                        00000000
                        00000000
                        00000000
                        00001010
                        00010001
                        00000000
                        00010001
                        00001010
                        """)
KING_SPAN = strBBtoBB("""
                      00000000
                      00000000
                      00000000
                      00000000
                      00000000
                      00000111
                      00000101
                      00000111
                      """)
CASTLE_ROOKS = [63,56,7,0]

RankMasks8 = [np.uint64(0xFF),np.uint64(0xFF00), np.uint64(0xFF0000), np.uint64(0xFF000000), np.uint64(
    0xFF00000000), np.uint64(0xFF0000000000), np.uint64(0xFF000000000000), np.uint64(0xFF00000000000000)]

FileMasks8 = {
    'a': np.uint64(0x101010101010101), 'b': np.uint64(0x202020202020202), 'c': np.uint64(0x404040404040404), 'd': np.uint64(0x808080808080808),
    'e': np.uint64(0x1010101010101010), 'f': np.uint64(0x2020202020202020), 'g': np.uint64(0x4040404040404040), 'h': np.uint64(0x8080808080808080)}

FileMasks82 = [
        np.uint64(0x101010101010101),  np.uint64(0x202020202020202), np.uint64(0x404040404040404), np.uint64(0x808080808080808),
        np.uint64(0x1010101010101010),  np.uint64(0x2020202020202020),  np.uint64(0x4040404040404040),np.uint64(0x8080808080808080)]

DiagonalMasks8 = [np.uint64(0x1), np.uint64(0x102), np.uint64(0x10204), np.uint64(0x1020408), np.uint64(0x102040810), np.uint64(0x10204081020), np.uint64(0x1020408102040),np.uint64(0x102040810204080), np.uint64(0x204081020408000), np.uint64(0x408102040800000), np.uint64(0x810204080000000),np.uint64(0x1020408000000000), np.uint64(0x2040800000000000), np.uint64(0x4080000000000000), np.uint64(0x8000000000000000)]

AntiDiagonalMasks8 = [np.uint64(0x80), np.uint64(0x8040), np.uint64(0x804020), np.uint64(0x80402010), np.uint64(0x8040201008), np.uint64(0x804020100804), np.uint64(0x80402010080402),np.uint64(0x8040201008040201), np.uint64(0x4020100804020100), np.uint64(0x2010080402010000), np.uint64(0x1008040201000000),np.uint64(0x804020100000000), np.uint64(0x402010000000000), np.uint64(0x201000000000000), np.uint64(0x100000000000000)]