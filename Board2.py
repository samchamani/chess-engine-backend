from array import array
from random import *
import re
import numpy as np
from helpers import *
from constants import *
from copy import copy
from algorithms import *


class Board:
    WP = np.uint64(0)
    WN = np.uint64(0)
    WB = np.uint64(0)
    WR = np.uint64(0)
    WQ = np.uint64(0)
    WK = np.uint64(0)
    BP = np.uint64(0)
    BN = np.uint64(0)
    BB = np.uint64(0)
    BR = np.uint64(0)
    BQ = np.uint64(0)
    BK = np.uint64(0)
    
    BLACK_PIECES = np.uint64(0)
    WHITE_PIECES = np.uint64(0)

    MY_PIECES = np.uint64(0)
    NOT_MY_PIECES =  np.uint64(0)

    EMPTY = np.uint64(0)
    OCCUPIED = np.uint64(0)

    hash = -1
    moves = []
    MOVE_HISTORY = []
    STATE_HISTORY = {} #später transpostion table?
    zobTable = [[np.uint64(randint(1,2**64 - 1)) for i in range(12)]for j in range(64)]
    zobEnPass = [np.uint64(randint(1,2**64 - 1)) for i in range(8)]
    zobCastle = [np.uint64(randint(1,2**64 - 1)) for i in range(4)]
    zobTurn = np.uint64(randint(1,2**64 - 1))
    ttable = {}

    isWhiteTurn = True
    castleRight = "KQkq"
    enPassant = "-"
    halfmoveClock = 0
    fullmoveCount = 1
    chessBoard = [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"],
    ]

    def __init__(self, fenString=None):
        self.fenString = fenString
        self.initBoard()
        self.convertArraysToBitboards()
        self.genZobHash()

    def initBoard(self):
        if not self.fenString is None:
            splittedFEN = self.fenString.split(' ')
            self.chessBoard = self.parseFEN(splittedFEN[0])
            self.isWhiteTurn = splittedFEN[1] == "w"
            self.castleRight = splittedFEN[2]
            self.enPassant = splittedFEN[3]
            self.halfmoveClock = int(splittedFEN[4])
            self.fullmoveCount = int(splittedFEN[5])

    def parseFEN(self, boardString):
        board = []
        rows = boardString.split("/")
        for row in rows:
            rowContent = []
            for cell in row:
                if re.match('\d', cell):
                    for n in range(int(cell)):
                        rowContent.append("")
                else:
                    rowContent.append(cell)
            board.append(rowContent)
        return board
        

    def convertArraysToBitboards(self):
        for i in range(64):
            binary = ZERO_STRING[i+1:] + "1" + ZERO_STRING[0:i]
            num = np.uint64(int(binary, 2))
            row = (i // 8)
            col = i % 8
            figure = self.chessBoard[row][col]
            if figure == "P":
                self.WP += num
            elif figure == "N":
                self.WN += num
            elif figure == "B":
                self.WB += num
            elif figure == "R":
                self.WR += num
            elif figure == "Q":
              self.WQ += num
            elif figure == "K":
              self.WK += num
            elif figure == "p":
              self.BP += num
            elif figure == "n":
              self.BN += num
            elif figure == "b":
              self.BB += num
            elif figure == "r":
              self.BR += num
            elif figure == "q":
              self.BQ += num
            elif figure == "k":
              self.BK += num

    def convertBitboardsToArray(self):
        newChessBoard = []
        for rowI in range(8):
            cellContent = []
            for cellJ in range(8):
                cellContent.append('')
            newChessBoard.append(cellContent)

        for i in range(64):
            row = (i // 8)
            col = i % 8
            if (self.WP >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "P"
            elif (self.WN >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "N"
            elif (self.WB >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "B"
            elif (self.WR >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "R"
            elif (self.WQ >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "Q"
            elif (self.WK >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "K"
            elif (self.BP >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "p"
            elif (self.BN >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "n"
            elif (self.BB >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "b"
            elif (self.BR >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "r"
            elif (self.BQ >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "q"
            elif (self.BK >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "k"

        return newChessBoard
    
    def genZobHash(self):
        hash = np.uint64(0)
        for i in range(64):
            if (self.WP >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][0]
            elif (self.BP >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][1]
            elif (self.WN >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][2]
            elif (self.BN >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][3]
            elif (self.WB >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][4]
            elif (self.BB >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][5]
            elif (self.WR >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][6]
            elif (self.BR >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][7]
            elif (self.WQ >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][8]
            elif (self.BQ >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][9]
            elif (self.WK >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][10]
            elif (self.BK >> np.uint64(i)) & ONE == ONE:
                hash ^= self.zobTable[i][11]
        # if self.enPassant in squareNames:
        #     hash ^= self.zobEnPass[int(self.enPassant[1])-1]
        # if "K" in self.castleRight:
        #     hash ^= self.zobCastle[0]
        # if "Q" in self.castleRight:
        #     hash ^= self.zobCastle[1]
        # if "k" in self.castleRight:
        #     hash ^= self.zobCastle[2]
        # if "q" in self.castleRight:
        #     hash ^= self.zobCastle[3]  
        # if not self.isWhiteTurn:
        #     hash ^= self.zobTurn

        self.hash = hash

# //////////////////////////////////////////////////////
#
#                    Move Generator
#
# //////////////////////////////////////////////////////

    def getMoves(self):
        self.moves.clear()
        if self.isWhiteTurn:
            return self.filterMoves(self.possibleMovesW())
        else:
            return self.filterMoves(self.possibleMovesB())

    def possibleMovesW(self):
        #added BK to avoid illegal capture
        self.NOT_MY_PIECES = ~(self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BK)
        #omitted WK to avoid illegal capture
        self.MY_PIECES = self.WP|self.WN|self.WB|self.WR|self.WQ
        self.OCCUPIED=self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        self.EMPTY=~self.OCCUPIED
        self.getMovesB(self.WB)
        self.getMovesN(self.WN)
        self.getMovesQ(self.WQ)
        self.getMovesR(self.WR)
        self.getMovesK(self.WK)
        self.getMovesP()
        return self.moves

        
    
    def possibleMovesB(self):
        #added WK to avoid illegal capture
        self.NOT_MY_PIECES=~(self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK|self.WK)
        #omitted BK to avoid illegal capture
        self.MY_PIECES=self.BP|self.BN|self.BB|self.BR|self.BQ
        self.OCCUPIED=self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        self.EMPTY=~self.OCCUPIED
        self.getMovesB(self.BB)
        self.getMovesN(self.BN)
        self.getMovesQ(self.BQ)
        self.getMovesR(self.BR)
        self.getMovesK(self.BK)
        self.getMovesP()
        return self.moves 

    
    def getMovesP(self):
        # exluding black king, because he can't be eaten
        self.BLACK_PIECES = self.BP | self.BN | self.BB | self.BR | self.BQ
        
        # same here
        self.WHITE_PIECES = self.WP | self.WN | self.WB | self.WR | self.WQ


        # beat right
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & ~FILE_A
            PAWN_MOVES_PROMO = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & RANK_8 & ~FILE_A
            color = 1
            type = 'P' 
        else: 
            PAWN_MOVES = (self.BP << np.uint64(7)) & self.WHITE_PIECES  &~ FILE_H
            PAWN_MOVES_PROMO = (self.BP << np.uint64(7)) & self.WHITE_PIECES & RANK_1 & ~FILE_H
            color = -1
            type = 'p'

        for i in range(64):
            isPromo = False 
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE  == ONE :
                move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x" + makeField((i//8), i % 8)
                move['from'] = np.uint64(((i//8)+(color*1))*8+((i % 8)-(color*1)))
                move['to'] = np.uint64((i//8)*8 + (i % 8))
                move['type'] = type
                if isPromo:
                    self.promoHelper(self.isWhiteTurn, move)
                else:
                    self.moves.append(move)

        # beat left
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> np.uint64(9)) & self.BLACK_PIECES  & ~ FILE_H
            PAWN_MOVES_PROMO = (self.WP >> np.uint64(9)) & self.BLACK_PIECES & RANK_8 & ~FILE_H
        else:
            PAWN_MOVES = (self.BP << np.uint64(9)) & self.WHITE_PIECES  & ~ FILE_A
            PAWN_MOVES_PROMO = (self.BP << np.uint64(9)) & self.WHITE_PIECES & RANK_1 & ~FILE_A

        for i in range(64):
            move = {}
            isPromo = False
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)+(color*1)) + "x"+makeField((i//8), i % 8)
                move['from'] = np.uint64(((i//8)+(color*1))*8+((i % 8)-(color*1))) 
                move['to'] = np.uint64((i//8)*8+(i % 8))
                move['type'] = type
                if isPromo:
                    self.promoHelper(self.isWhiteTurn, move)
                else:
                    self.moves.append(move)

        # move 1 forward
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> np.uint64(8)) & self.EMPTY 
            PAWN_MOVES_PROMO = (self.WP >> np.uint64(8)) & self.EMPTY & RANK_8
        else:
            PAWN_MOVES = (self.BP << np.uint64(8)) & self.EMPTY
            PAWN_MOVES_PROMO = (self.BP << np.uint64(8)) & self.EMPTY & RANK_1

        for i in range(64):
            move = {}
            isPromo = False
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['from'] = np.uint64(((i//8)+(color*1))*8+(i % 8))
                move['to'] = np.uint64((i//8)*8+(i%8))
                move['type'] = type
                if isPromo:
                    self.promoHelper(self.isWhiteTurn, move)
                else:
                    self.moves.append(move)

        # move 2 forward
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> np.uint64(16)) & self.EMPTY & (self.EMPTY >> np.uint64(8)) & RANK_4
        else:
            PAWN_MOVES = (self.BP << np.uint64(16)) & self.EMPTY & (self.EMPTY << np.uint64(8)) & RANK_5

        for i in range(64):
            move = {}
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*2), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['from'] = np.uint64(((i//8)+(color*2))*8+(i%8))
                move['to'] = np.uint64((i//8)*8+(i % 8))
                move['type'] = type
                move['double'] = makeField((i//8)+(color*1), i % 8)
                self.moves.append(move)

        if self.enPassant != '-':
            RANK = FileMasks8[self.enPassant[0]]

            # en passant right
            if self.isWhiteTurn:
                PAWN_MOVES = (self.WP << ONE) & self.BP & RANK_5 & ~FILE_A & RANK
            else:
                PAWN_MOVES = (self.BP >> ONE) & self.WP & RANK_4 & ~FILE_H & RANK
            
            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8-(color*1))+'x'+makeField((i//8)-(color*1), i % 8)
                    move['from'] = np.uint64(((i//8)*8)+(i%8-(color*1)))
                    move['to'] = np.uint64(((i//8)-(color*1))*8+(i % 8))
                    move['type'] = type
                    move['enPassant'] = True
                    if self.isWhiteTurn:
                        destination = np.uint64(((((i//8)-(color*1))+1)*8)+(i % 8))
                    else:
                        destination = np.uint64(((((i//8)-(color*1))-1)*8)+(i % 8))
                    move['enemy'] = destination
                    self.moves.append(move)

            # en passant left
            if self.isWhiteTurn:
                PAWN_MOVES = (self.WP >> ONE) & self.BP & RANK_5 & ~FILE_H & RANK
            else:
                PAWN_MOVES = (self.BP << ONE) & self.WP & RANK_4 & ~FILE_A & RANK

            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8+(color*1))+'x'+ makeField((i//8) -(color*1), i % 8)
                    move['from'] = np.uint64(((i//8)*8)+(i % 8+(color*1)))
                    move['to'] = np.uint64(((i//8)-(color*1))*8+(i % 8))
                    move['type'] = type
                    move['enPassant'] = True
                    if self.isWhiteTurn:
                        destination = np.uint64(((((i//8)-(color*1))+1)*8)+(i % 8))
                    else:
                        destination = np.uint64(((((i//8)-(color*1))-1)*8)+(i % 8))
                    move['enemy'] = destination
                    self.moves.append(move)

    
    def promoHelper(self, isWhiteTurn:bool ,move):
        moveR = copy(move)
        moveR['promoType'] = 'R' if isWhiteTurn else 'r'
        self.moves.append(moveR)
        moveQ = copy(move)
        moveQ['promoType'] = 'Q' if isWhiteTurn else 'q'
        self.moves.append(moveQ)
        moveB = copy(move)
        moveB['promoType'] = 'B' if isWhiteTurn else 'b'
        self.moves.append(moveB)
        moveN = copy(move)
        moveN['promoType'] = 'N' if isWhiteTurn else 'n'
        self.moves.append(moveN)

    def HAndVMoves(self, s, OCCUPIED_CUSTOM = None):
        OCCUPIED = OCCUPIED_CUSTOM if OCCUPIED_CUSTOM else self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        return self.get_rank_moves_bb(s, OCCUPIED) | self.get_file_moves_bb(s, OCCUPIED)
    
    def DAndAntiDMoves(self, s:int, OCCUPIED_CUSTOM = None):
        OCCUPIED = OCCUPIED_CUSTOM if OCCUPIED_CUSTOM else self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        return self.get_diag_moves_bb(s, OCCUPIED) | self.get_antidiag_moves_bb(s, OCCUPIED)

    def get_rank_moves_bb(self, i, occ):
        """
        i is index of square
        occ is the combined occupancy of the board
        """
        f = i & np.uint8(7)
        occ = RankMasks8[i//8] & occ # isolate rank occupancy
        occ = np.multiply(FILE_A, occ) >> np.uint8(56) # map to first rank
        occ = FILE_A * FIRST_RANK_MOVES[f][occ] # lookup and map back to rank
        return RankMasks8[i//8] & occ

    def get_file_moves_bb(self, i, occ):
        """
        i is index of square
        occ is the combined occupancy of the board
        """
        f = np.uint8(i) & np.uint8(7)
        # Shift to A file
        occ = FILE_A & (occ >> f)
        # Map occupancy and index to first rank
        occ = np.multiply(A1H8_DIAG, occ) >> np.uint8(56)
        first_rank_index = (i ^ np.uint8(56)) >> np.uint8(3)
        # Lookup moveset and map back to H file
        occ = np.multiply(A1H8_DIAG, FIRST_RANK_MOVES)[first_rank_index][occ]
        # Isolate H file and shift back to original file
        return (FILE_H & occ) >> (f ^ np.uint8(7))

    def get_diag_moves_bb(self, i, occ):
        """
        i is index of square
        occ is the combined occupancy of the board
        """
        f = i & np.uint8(7)
        occ = DiagonalMasks8[(i // 8) + (i % 8)] & occ # isolate diagonal occupancy
        occ = np.multiply(FILE_A , occ) >> np.uint8(56) # map to first rank
        occ = FILE_A * FIRST_RANK_MOVES[f][occ] # lookup and map back to diagonal
        return DiagonalMasks8[(i // 8) + (i % 8)] & occ

    def get_antidiag_moves_bb(self, i, occ):
        """
        i is index of square
        occ is the combined occupancy of the board
        """
        f = i & np.uint8(7)
        occ = AntiDiagonalMasks8[(i // 8) + 7 - (i % 8)] & occ # isolate antidiagonal occupancy
        occ = np.multiply(FILE_A, occ) >> np.uint8(56) # map to first rank
        occ = FILE_A * FIRST_RANK_MOVES[f][occ] # lookup and map back to antidiagonal
        return AntiDiagonalMasks8[(i // 8) + 7 - (i % 8)] & occ
    
    def getMovesB(self, B):
        if self.isWhiteTurn:
            type = 'B'
        else:
            type = 'b'
        i = B&~np.subtract(B,ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLocation) & self.NOT_MY_PIECES
            j = possibility & ~np.subtract(possibility,ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "B"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLocation//8)*8)+(iLocation%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                self.moves.append(move)

                possibility&=~j
                j = possibility & ~np.subtract(possibility, ONE)
            B &= ~i
            i = B&~np.subtract(B,ONE)
    
    def getMovesR(self, R):
        if self.isWhiteTurn:
            type = 'R'
        else:
            type = 'r'

        i = R&~np.subtract(R, ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = self.HAndVMoves(iLocation) & self.NOT_MY_PIECES
            j = possibility & ~np.subtract(possibility, ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "R"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLocation//8)*8)+(iLocation%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                self.moves.append(move)      

                possibility&=~j
                j = possibility & ~np.subtract(possibility, ONE)
            R &= ~i
            i = R&~np.subtract(R, ONE)
    
    def getMovesQ(self, Q):
        if self.isWhiteTurn:
            type = 'Q'
        else:
            type = 'q'

        i = Q&~np.subtract(Q, ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = (self.DAndAntiDMoves(iLocation) | self.HAndVMoves(iLocation) )& self.NOT_MY_PIECES
            j = possibility & ~np.subtract(possibility, ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "Q"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLocation//8)*8)+(iLocation%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                self.moves.append(move)

                possibility&=~j
                j = possibility & ~np.subtract(possibility, ONE)
            Q &= ~i
            i = Q&~np.subtract(Q, ONE)


    def getMovesN(self, N):  
        if self.isWhiteTurn:
            type = 'N'
        else:
            type = 'n'  
        i = N &~(N - ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            if iLoc >  18:
                possibility = KNIGHT_SPAN << np.uint64(iLoc-18)
            else:
                possibility = KNIGHT_SPAN >> np.uint64(18 - iLoc)
            if iLoc%8 < 4:
                possibility &= ~FILE_GH & self.NOT_MY_PIECES
            else:
                possibility &= ~FILE_AB & self.NOT_MY_PIECES
            j = possibility &~np.subtract(possibility,ONE)
            while j != 0:
                index = trailingZeros(j) 
                move = {}
                move['toString'] = "N"+makeField((iLoc//8),iLoc%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLoc//8)*8)+(iLoc%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                self.moves.append(move) 

                possibility&=~j
                j=possibility&~np.subtract(possibility,ONE)
            N &=~i
            i = N &~np.subtract(N, ONE)
    
    def getMovesK(self, K):
        if self.isWhiteTurn:
            type = 'K'
            castleRightK = 'K' in self.castleRight
            castleRightQ = 'Q' in self.castleRight
            castleK = CASTLE_K
            castleQ = CASTLE_Q
        else:
            type = 'k'
            castleRightK = 'k' in self.castleRight
            castleRightQ = 'q' in self.castleRight
            castleK = CASTLE_k
            castleQ = CASTLE_q

        isWhiteKing = K & self.WK > 0 
        iLoc = trailingZeros(K)
        if iLoc >  9:
            possibility = KING_SPAN << np.uint64(iLoc-9)
        else:
            possibility = KING_SPAN >> np.uint64(9 - iLoc)
        if iLoc%8 < 4:
            possibility &= ~FILE_GH & self.NOT_MY_PIECES
        else:
            possibility &= ~FILE_AB & self.NOT_MY_PIECES
        j = possibility &~np.subtract(possibility,ONE)
        safe = ~self.unsafeFor(isWhiteKing)

        if castleRightK and castleK & safe & self.EMPTY == castleK :
            move = {}
            move['toString'] = "0-0"
            move['type'] = type
            move['castle'] = "k"
            self.moves.append(move)
        if castleRightQ and castleQ & safe & self.EMPTY == castleQ :
            move = {}
            move['toString'] = "0-0-0"
            move['type'] = type
            move['castle'] = "q"
            self.moves.append(move)
            
        while j != 0:
            if j & safe != 0: #filters out unsafe fields
                index = trailingZeros(j) 
                move = {}
                move['toString'] = "K"+makeField((iLoc//8),iLoc%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLoc//8)*8)+(iLoc%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                self.moves.append(move)
            possibility&=~j
            j=possibility&~np.subtract(possibility, ONE)

    def unsafeFor(self, isForWhite: bool):
        """
        Generates a bitboard with all fields that would put the King of the color set through `isFormWhite` in check/danger.

        Args:
            `isForWhite` (bool): if `True` bitboard shows fields that are not safe for white pieces, if `False` then same for black 

        Returns:
            bitboard with unsafe fields for given color
        """
        if isForWhite:
            P = self.BP
            N = self.BN
            QB = self.BQ|self.BB
            QR = self.BQ|self.BR
            K = self.BK
            #black pawn
            unsafe = (P<<np.uint64(7)) & ~FILE_H 
            unsafe |= (P<<np.uint64(9)) & ~FILE_A
        else:
            P = self.WP
            N = self.WN
            QB = self.WQ|self.WB
            QR = self.WQ|self.WR
            K = self.WK
            #white pawn
            unsafe = (P>>np.uint64(7)) & ~FILE_A 
            unsafe |= (P>>np.uint64(9)) & ~FILE_H

        
        #knight
        i = N &~np.subtract(N,ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            if iLoc > 18:
                possibility = KNIGHT_SPAN << np.uint64(iLoc - 18)
            else:
                possibility = KNIGHT_SPAN >> np.uint64(18 - iLoc)
            if iLoc % 8 < 4:
                possibility &= ~FILE_GH
            else:
                possibility &= ~FILE_AB
            unsafe |= possibility
            N &=~i
            i = N & ~np.subtract(N,ONE)
            
        #(anti)diagonal sliding pieces (bishop & queen)
        i = QB &~np.subtract(QB,ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLoc)
            unsafe |= possibility
            QB&=~i
            i=QB&~np.subtract(QB,ONE)
            
        #staight sliding pieces (rook & queen)
        i = QR &~np.subtract(QR,ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.HAndVMoves(iLoc)
            unsafe |= possibility
            QR&=~i
            i=QR&~np.subtract(QR, ONE)
        
        #king
        iLoc = trailingZeros(K)
        if iLoc > 9:
            possibility = KING_SPAN<<np.uint64(iLoc-9)
        else:
            possibility = KING_SPAN>>np.uint64(9 -iLoc)
        if iLoc % 8 < 4:
            possibility &=~FILE_GH
        else:
            possibility &=~FILE_AB
        unsafe |= possibility
        
        return unsafe

    def filterMoves(self, moves):
        newMoves = []
        for move in moves:
            type = move['type']
            if type == 'K' or type == 'k':
                newMoves.append(move)
            else:
                if type == 'P':
                    newBoard = self.WB | self.WK | self.WN | self.WQ | self.WR | self.doMoveHelper(move, self.WP)
                elif type == 'N':
                    newBoard = self.WP | self.WB | self.WQ | self.WK | self.WR | self.doMoveHelper(move, self.WN)
                elif type == 'B':
                    newBoard = self.WP | self.WK | self.WN | self.WQ | self.WR | self.doMoveHelper(move, self.WB)
                elif type == 'R':
                    newBoard = self.WP | self.WB | self.WQ | self.WK | self.WN | self.doMoveHelper(move, self.WR)
                elif type == 'Q':
                    newBoard = self.WP | self.WB | self.WR | self.WK | self.WN | self.doMoveHelper(move, self.WQ)
                elif type == 'p':
                    newBoard = self.BB | self.BK | self.BN | self.BQ | self.BR | self.doMoveHelper(move, self.BP)
                elif type == 'n':
                    newBoard = self.BP | self.BB | self.BQ | self.BK | self.BR | self.doMoveHelper(move, self.BN)
                elif type == 'b':
                    newBoard = self.BP | self.BK | self.BN | self.BQ | self.BR | self.doMoveHelper(move, self.BB)
                elif type == 'r':
                    newBoard = self.BP | self.BB | self.BQ | self.BK | self.BN | self.doMoveHelper(move, self.BR)
                elif type == 'q':
                    newBoard = self.BP | self.BB | self.BR | self.BK | self.BN | self.doMoveHelper(move, self.BQ)
                safe = self.unsafeFor2(self.isWhiteTurn, newBoard, move['to'])
                if safe:
                    newMoves.append(move)
        return newMoves

    def unsafeFor2(self, isForWhite: bool, board:np.uint64 = None, destination: np.uint64 = None):
        if isForWhite:
            P = self.BP
            N = self.BN
            QB = self.BQ|self.BB
            QR = self.BQ|self.BR
            K = self.BK
            myK = self.WK
            P&=~(ONE<<destination)
            N&=~(ONE<<destination)
            QB&=~(ONE<<destination)
            QR&=~(ONE<<destination)
            K&=~(ONE<<destination)
            #black pawn
            if ((P<<np.uint64(7)) & ~FILE_H)&myK != 0:
                return False
            if ((P<<np.uint64(9)) & ~FILE_A)&myK != 0: 
                return False
        else:
            P = self.WP
            N = self.WN
            QB = self.WQ|self.WB
            QR = self.WQ|self.WR
            K = self.WK
            myK = self.BK

            P&=~(ONE<<destination)
            N&=~(ONE<<destination)
            QB&=~(ONE<<destination)
            QR&=~(ONE<<destination)
            K&=~(ONE<<destination)
            #white pawn
            if ((P>>7) & int(~FILE_A))&myK !=0:
                return False
            if ((P>>9) & int(~FILE_H))&myK != 0:
                return False
        
        OCCUPIED = board|np.uint64(P|N|QB|QR|K)
        
        #knight
        i = N &~np.subtract(N, ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            if iLoc > 18:
                possibility = KNIGHT_SPAN <<np.uint64(iLoc - 18)
            else:
                possibility = KNIGHT_SPAN >> np.uint64(18 - iLoc)
            if iLoc % 8 < 4:
                possibility &= ~FILE_GH
            else:
                possibility &= ~FILE_AB
            if np.uint64(possibility) & myK !=0:
                return False
            N &=~i
            i = N & ~np.subtract(N,ONE)
            
        #(anti)diagonal sliding pieces (bishop & queen)
        i = QB &~np.subtract(QB,ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLoc, OCCUPIED)
            if possibility & myK !=0:
                return False
            QB&=~i
            i=QB&~np.subtract(QB, ONE)
            
        #staight sliding pieces (rook & queen)
        i = QR &~np.subtract(QR, ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.HAndVMoves(iLoc, OCCUPIED)
            if possibility & myK != 0:
                return False
            QR&=~i
            i=QR&~np.subtract(QR,ONE)
        
        #king
        iLoc = trailingZeros(K)
        if iLoc > 9:
            possibility = (KING_SPAN)<<np.uint64(iLoc-9)
        else:
            possibility = (KING_SPAN)>>np.uint64(9 -iLoc)
        if iLoc % 8 < 4:
            possibility &=(~FILE_GH)
        else:
            possibility &=(~FILE_AB)
        if np.uint64(possibility) & myK != 0:
            return False
        
        return True

    def doMove(self, move):
        undoMove = []
        type = move['type']
        if type.isupper():
            if type == 'P':
                self.WP = self.doMoveHelperPawn(move, self.WP, undoMove)
                self.updateHash(move, 1, undoMove)
            elif type == 'B':
                self.WB = self.doMoveHelper(move, self.WB, undoMove)
                self.updateHash(move, 4, undoMove)
            elif type == 'N':
                self.WN = self.doMoveHelper(move, self.WN, undoMove)
                self.updateHash(move, 2, undoMove)
            elif type == 'R':
                self.WR = self.doMoveHelper(move, self.WR, undoMove)
                self.updateHash(move, 6, undoMove)
                if self.WR & FILE_A & RANK_1 == 0:
                    self.castleRight = self.castleRight.replace('K','')
                elif self.WR & FILE_H & RANK_1 == 0:
                    self.castleRight = self.castleRight.replace('Q','')
            elif type == 'K':
                self.WK = self.doMoveHelperKing(move, self.WK, undoMove)
                self.updateHash(move, 10, undoMove)
                undoMove.append(('castle', self.castleRight))
                self.castleRight = self.castleRight.replace('KQ','')
            elif type == 'Q':
                self.WQ = self.doMoveHelper(move, self.WQ, undoMove)
                self.updateHash(move, 8, undoMove)

            if move['type'] =='P' and move.get('enPassant'):
                destination = move['enemy']
                self.clearDestination(True, destination, undoMove)   
            elif not move.get('castle'):
                destination = move['to']
                self.clearDestination(True, destination, undoMove)   
        else:
            if type == 'p':
                self.BP = self.doMoveHelperPawn(move, self.BP, undoMove)
                self.updateHash(move, 2, undoMove)
            elif type == 'b':
                self.BB = self.doMoveHelper(move, self.BB, undoMove)
                self.updateHash(move, 5, undoMove)
            elif type == 'n':
                self.BN = self.doMoveHelper(move, self.BN, undoMove)
                self.updateHash(move, 3, undoMove)
            elif type == 'r':
                self.BR = self.doMoveHelper(move, self.BR, undoMove)
                self.updateHash(move, 7, undoMove)
                if self.BR & FILE_A & RANK_8 == 0:
                    self.castleRight = self.castleRight.replace('k','')
                elif self.WR & FILE_H & RANK_8 == 0:
                    self.castleRight = self.castleRight.replace('q','')
            elif type == 'k':
                self.BK = self.doMoveHelperKing(move, self.BK, undoMove)
                self.updateHash(move, 11, undoMove)
                undoMove.append(('castle', self.castleRight))
                self.castleRight = self.castleRight.replace('kq','')
            elif type == 'q':
                self.BQ = self.doMoveHelper(move, self.BQ, undoMove)
                self.updateHash(move, 9, undoMove)

            if move['type'] == 'p' and move.get('enPassant'):
                destination = move['enemy']
                self.clearDestination(False, destination, undoMove) 
            elif not move.get('castle') :   
                destination = move['to']
                self.clearDestination(False, destination, undoMove) 

        boardString = getBoardStr(self) #might be replaced with hash function later
        if boardString in self.STATE_HISTORY:
            self.STATE_HISTORY[boardString] += 1
        else:
            self.STATE_HISTORY[boardString] = 1

        self.isWhiteTurn = not self.isWhiteTurn
        undoMove.append(('enPassant', self.enPassant))
        if move.get('double'):
            self.enPassant = move['double']
        else:
            self.enPassant = '-'
        self.MOVE_HISTORY.append(undoMove)

    def doMoveHelper(self, move, BOARD:np.uint64, undoMove:array = None):
        if undoMove is not None:
            undoMove.append((move['type'], BOARD))

        start = move['from']
        end = move['to']
        BOARD &= ~(ONE << start)
        BOARD |= (ONE << end)
        return BOARD

    def doMoveHelperKing(self, move, BOARD, undoMove:array = None):
        if not move.get('castle'):
            start = move['from']
            end = move['to']
            undoMove.append((move['type'], BOARD))
            BOARD &= ~(ONE << start)
            BOARD |= (ONE << end)
        else:
            type = move['type']
            castle = move ['castle']
            if type.isupper():
                if castle == 'q':
                    undoMove.append((type, BOARD))
                    undoMove.append(('r', self.WR))
                    BOARD =(BOARD >> ONE)
                    self.WR ^=(np.uint64(72057594037927936))
                    self.WR |=(ONE << np.uint64(60))
                elif castle =='k':
                    undoMove.append((type, BOARD))
                    undoMove.append(('r', self.WR))
                    BOARD =(BOARD << ONE)
                    self.WR ^=(np.uint64(9223372036854775808))
                    self.WR |=(ONE << np.uint64(60))

            else:
                if castle == 'q':
                    undoMove.append((type, BOARD))
                    undoMove.append(('r', self.BR))
                    BOARD = BOARD >> ONE 
                    self.BR ^= np.uint64(1)
                    self.BR |=(ONE << np.uint64(4))
                elif castle == 'k':
                    undoMove.append((type, BOARD))
                    undoMove.append(('r', self.BR))
                    BOARD = BOARD << ONE 
                    self.BR ^= np.uint64(128)
                    self.BR |=(ONE << np.uint64(4))
        return BOARD


    def doMoveHelperPawn(self, move, BOARD, undoMove:array = None):
        oldBoard = BOARD
        start = move['from']
        end = move['to']
        if not move.get('isPromo'):
            if (((BOARD >> start) & ONE) == ONE):
                BOARD &= ~(ONE << start)
                BOARD |= (ONE << end)
                undoMove.append((move['type'], oldBoard))
        else:
            if (((BOARD >> start) & ONE) == ONE):
                BOARD &= ~(ONE << start)
                type = move['promoType']
                if type == 'Q':
                    oldBoard2 = self.WQ
                    self.WQ |= (ONE << end)
                elif type == 'R':
                    oldBoard2 = self.WR
                    self.WR |= (ONE << end)
                elif type == 'B':
                    oldBoard2 = self.WB
                    self.WB |= (ONE << end)
                elif type == 'N':
                    oldBoard2 = self.WN
                    self.WN |= (ONE << end)
                elif type == 'q':
                    oldBoard2 = self.BQ
                    self.BQ |= (ONE << end)
                elif type == 'r':
                    oldBoard2 = self.BR
                    self.BR |= (ONE << end)
                elif type == 'b':
                    oldBoard2 = self.BB
                    self.BB |= (ONE << end)
                elif type == 'n':
                    oldBoard2 = self.BN
                    self.BN |= (ONE << end)

                undoMove.extend([(move['type'], oldBoard),(type,oldBoard2)])

        return BOARD

    def updateHash(self, move, value, undoMove:array):
        start = move['from']
        end = move['to']
        undoMove.append(('hash', self.hash))
        self.hash ^=self.zobTable[start][value]
        self.hash ^=self.zobTable[end][value]

    def clearDestination(self, isWhite:bool, destination:np.uint64, undoMove:array):
        if isWhite:
            if (((self.BP >> destination) & ONE) == ONE):
                undoMove.append(('p', self.BP))
                self.BP &= ~(ONE << destination)
            elif (((self.BN >> destination) & ONE) == ONE):
                undoMove.append(('n', self.BN))
                self.BN&=~(ONE<<destination)
            elif (((self.BQ >> destination) & ONE) == ONE):
                undoMove.append(('q', self.BQ))
                self.BQ&=~(ONE<<destination)
            elif (((self.BB >> destination) & ONE) == ONE):
                undoMove.append(('b', self.BB))
                self.BB&=~(ONE<<destination)
            elif (((self.BR >> destination) & ONE) == ONE):
                undoMove.append(('r', self.BR))
                self.BR&=~(ONE<<destination)
            elif (((self.BK >> destination) & ONE) == ONE):
                undoMove.append(('k', self.BK))
                self.BK&=~(ONE<<destination) 
        else:
            if (((self.WP >> destination) & ONE) == ONE):
                undoMove.append(('P', self.WP))
                self.WP &= ~(ONE << destination)
            elif (((self.WN >> destination) & ONE) == ONE):
                undoMove.append(('N', self.WN))
                self.WN&=~(ONE<<destination)
            elif (((self.WQ >> destination) & ONE) == ONE):
                undoMove.append(('Q', self.WQ))
                self.WQ&=~(ONE<<destination)
            elif (((self.WB >> destination) & ONE) == ONE):
                undoMove.append(('B', self.WB))
                self.WB&=~(ONE<<destination)
            elif (((self.WR >> destination) & ONE) == ONE):
                undoMove.append(('R', self.WR))
                self.WR&=~(ONE<<destination)
            elif (((self.WK >> destination) & ONE) == ONE):
                undoMove.append(('K', self.WK))
                self.WK&=~(ONE<<destination) 

    def undoLastMove(self):
        if len(self.MOVE_HISTORY) == 0:
            return
        last = self.MOVE_HISTORY.pop()
        self.STATE_HISTORY[getBoardStr(self)]-=1 #might be replaced with hash function later
        
        for type, value in last:
            if type =='P':
                self.WP = value
            elif type == 'B':
                self.WB = value
            elif type == 'N':
                self.WN = value
            elif type == 'R':
                self.WR = value
            elif type == 'Q':
                self.WQ = value
            elif type == 'K':
                self.WK = value
            elif type =='p':
                self.BP = value
            elif type == 'b':
                self.BB = value
            elif type == 'n':
                self.BN = value
            elif type == 'r':
                self.BR = value
            elif type == 'q':
                self.BQ = value
            elif type == 'k':
                self.BK = value
            elif type == 'castle':
                self.castleRight = value
            elif type == 'enPassant':
                self.enPassant = value
            elif type == 'hash':
                self.hash = value
        self.isWhiteTurn = not self.isWhiteTurn        
    
    def printBoard(self):
        printBits(self.WP, 'White Pawns')
        printBits(self.WN, 'White Knights')
        printBits(self.WB, 'White Bishops')
        printBits(self.WQ, 'White Queen')
        printBits(self.WR, 'White Rooks')
        printBits(self.WK, 'White King')
        print('===========================')
        printBits(self.BP, 'Black Pawns')
        printBits(self.BN, 'Black Knights')
        printBits(self.BB, 'Black Bishops')
        printBits(self.BQ, 'Black Queen')
        printBits(self.BR, 'Black Rooks')
        printBits(self.BK, 'Black King')
        
    def evaluate(self):
        value = 0
        colorfactor = -1
        if self.isWhiteTurn:
            colorfactor = 1

        pawns = 1*(countSetBits(self.WP) - countSetBits(self.BP))
        knightsAndBishops = 3*(countSetBits(self.WN | self.WB) - countSetBits(self.BN | self.BB))
        rooks = 5* (countSetBits(self.WR) - countSetBits(self.BR))
        queens = 9 * (countSetBits(self.WQ) - countSetBits(self.BQ))
        squarePieceBalance = colorfactor*(queens + rooks + knightsAndBishops + pawns)
        
        simpleMobility = colorfactor*(len(self.possibleMovesW()) - len(self.possibleMovesB()))
        
        value = squarePieceBalance + simpleMobility
        
        if self.isCheck(): value = -10
        if self.isRemis(): value = -100
        if self.isCheckMate(): value = -10000
        if self.isKingOfTheHill(): value = 10000
        
        return value 
        
    
# //////////////////////////////////////////////////////
#
#                    State checks
#
# //////////////////////////////////////////////////////

    def isGameDone(self):
        return self.isCheckMate() or self.isKingOfTheHill() or self.isRemis()
        
    def isCheck(self):
        K = self.BK
        if (self.isWhiteTurn):
            K = self.WK
        return self.unsafeFor(self.isWhiteTurn) & K > 0
    
    def isCheckMate(self):
        return len(self.getMoves()) == 0 and self.isCheck()
    
    def isKingOfTheHill(self):
        K = self.BK
        if (self.isWhiteTurn):
            K = self.WK
        return HILLS & K > 0
    
    def isRemis(self):
        return self.is3Fold() or self.is50Rule() or self.isStaleMate()
        
    def isStaleMate(self):
        return len(self.getMoves()) == 0 and not self.isCheck()
        
    def is50Rule(self):
        return self.halfmoveClock == 50 # or 100??

    def is3Fold(self):
        for key in self.STATE_HISTORY:
            if self.STATE_HISTORY[key] >= 3:
                return True
        return False

