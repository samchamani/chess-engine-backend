import numpy as np
from moves import *

def fieldToString(field: np.uint64):
    field = np.ceil(np.log2(field)).astype(int)
    y = field%8
    x = (field - y) / 8
    print(y)
    txt = 'abcdefgh'[int(7-x)] + '12345678'[int(y)]
    return txt

def toNumber(field: np.ndarray | np.uint64) -> np.ndarray | np.uint64:
    field = np.ceil(np.log2(field)).astype(int)
    return field

def bits(fields: np.uint64):
    while fields:
        b = fields & (~fields+np.uint64(1))
        yield toNumber(b) - np.uint64(1)
        fields ^= b

def attacked(board, enemy: np.ndarray,white: np.ndarray,field: np.uint64):
    if np.any(enemy & board.knight & allMoves[5][field][2]):
        return True
    if np.any(enemy & board.king & allMoves[4][field][2]):
        return True
    if np.any(white and np.any(enemy & board.pawn & allMoves[0][field][2][1])):
        return True
    if np.any(not white and np.any(enemy & board.pawn & allMoves[1][field][2][1])):
        return True
    attackerPieces = (allMoves[2][field][2] & (np.bitwise_or.reduce(board.queen) | np.bitwise_or.reduce(board.rook)) & enemy) | (allMoves[3][field][2] & (np.bitwise_or.reduce(board.queen) | np.bitwise_or.reduce(board.bishop)) & enemy) 
    if np.any(attackerPieces):
        for n in bits(attackerPieces):
            blockers = between[field][n] & board.all
            if not blockers:
                return True
    return False

def inCheck(board, color: np.uint64,enemy: np.uint64,white: bool):
    kingN = nonzeroElements(board.king & color)
    return attacked(board,enemy,white,toNumber(kingN))

def attackers():
    return np.uint64(0)

def toFen(board):
    boardTxt = ['-']*64
    for n in board.pawn:
        boardTxt[toNumber(n)] = 'p'
    for n in board.rook:
        boardTxt[toNumber(n)] = 'r'
    for n in board.knight:
        boardTxt[toNumber(n)] = 'n'
    for n in board.bishop:
        boardTxt[toNumber(n)] = 'b'
    for n in board.queen:
        boardTxt[toNumber(n)] = 'q'
    for n in board.king:
        boardTxt[toNumber(n)] = 'k'
    for n in bits(board.white):
        boardTxt[n] = boardTxt[n].upper()
    fen = ''
    x = 0
    i = 0
    while x < 8:
        y = 0
        while y < 8:
            if boardTxt[x*8+y] == '-':
                i += 1
            else:
                if i != 0:
                    fen += str(i)
                fen += boardTxt[x*8+y]
                i = 0
            if y == 7 and i != 0:
                fen += str(i)
                i = 0
            y += 1
        if x != 7:
            fen += '/'
        x += 1
    fen += ' '

    if board.player:
        fen += 'w'
    else:
        fen += 'b'
    fen += ' '

    if board.castle:
        if 1 & board.castle:
            fen += 'K'
        if 2 & board.castle:
            fen += 'Q'
        if 4 & board.castle:
            fen += 'k'
        if 8 & board.castle:
            fen += 'q'
    else:
        fen += '-'
    fen += ' '

    if board.en_passant:
        i = toNumber(board.en_passant)
        y = (i % 8)
        x = 8 - ((i - y) / 8)
        fen += chr(y + 97) + str(x)
    else:
        fen += '-'
    fen += ' '

    fen += str(board.halfmove) + ' ' + str(board.fullmove)
    return fen

def nonzeroElements(array: np.ndarray):
    return array[np.nonzero(array)]

def pinned(board, color: np.uint64, enemy: np.uint64):
    king = nonzeroElements(board.king & color)
    kNumber = toNumber(king)
    attackers = np.append(allMoves[2][kNumber][1] & (np.bitwise_or.reduce(board.queen) | np.bitwise_or.reduce(board.rook)) & enemy), (allMoves[3][kNumber][1] & (np.bitwise_or.reduce(board.queen) | np.bitwise_or.reduce(board.bishop)) & enemy) 
    pinned = 0
    for n in nonzeroElements(attackers):
        blockers = between[kNumber][toNumber(n)] & board.all
        if blockers.bit_count() == 1:
            pinned |= blockers & color
    return pinned