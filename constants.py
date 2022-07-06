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
KNIGHT_SPAN = np.uint64(43234889994)
KING_SPAN = np.uint64(460039)
HILLS = np.uint64(103481868288)

CASTLE_ROOKS = [63,56,7,0]

CASTLE_K = np.uint64(6917529027641081856)
CASTLE_Q = np.uint64(1008806316530991104)
CASTLE_k = np.uint64(96)
CASTLE_q = np.uint64(14)

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

ZERO = np.uint64(0)
ONE = np.uint64(1)
TWO = np.uint64(2)

square = {
    1:'a8',                 2:'b8',                  4:'c8',                  8:'d8',                  16:'e8',                  32:'f8',                  64:'g8',                  128:'h8', 
    256:'a7',               512:'b7',                1024:'c7',               2048:'d7',               4096:'e7',                8192:'f7',                16384:'g7',               32768:'h7', 
    65536:'a6',             131072:'b6',             262144:'c6',             524288:'d6',             1048576:'e6',             2097152:'f6',             4194304:'g6',             8388608:'h6', 
    16777216:'a5',          33554432:'b5',           67108864:'c5',           134217728:'d5',          268435456:'e5',           536870912:'f5',           1073741824:'g5',          2147483648:'h5', 
    4294967296:'a4',        8589934592:'b4',         17179869184:'c4',        34359738368:'d4',        68719476736:'e4',         137438953472:'f4',        274877906944:'g4',        549755813888:'h4', 
    1099511627776:'a3',     2199023255552:'b3',      4398046511104:'c3',      8796093022208:'d3',      17592186044416:'e3',      35184372088832:'f3',      70368744177664:'g3',      140737488355328:'h3', 
    281474976710656:'a2',   562949953421312:'b2',    1125899906842624:'c2',   2251799813685248:'d2',   4503599627370496:'e2',    9007199254740992:'f2',    18014398509481984:'g2',   36028797018963968:'h2', 
    72057594037927936:'a1', 144115188075855872:'b1', 288230376151711744:'c1', 576460752303423488:'d1', 1152921504606846976:'e1', 2305843009213693952:'f1', 4611686018427387904:'g1', 9223372036854775808:'h1' 
}    
