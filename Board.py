from array import array
from random import *
import re
import numpy as np
from helpers import *
from constants import *
from copy import copy


class Board:
    WP = 0
    WN = 0
    WB = 0
    WR = 0
    WQ = 0
    WK = 0
    BP = 0
    BN = 0
    BB = 0
    BR = 0
    BQ = 0
    BK = 0
    
    MY_PIECES = 0
    NOT_MY_PIECES =  0

    EMPTY = 0
    OCCUPIED = 0

    hash = -1
    moves = []
    MOVE_HISTORY = []
    STATE_HISTORY = {} #später transpostion table?
    zobTable = [[(randint(1,2**64 - 1)) for i in range(12)]for j in range(64)]
    zobEnPass = [(randint(1,2**64 - 1)) for i in range(8)]
    zobCastle = [(randint(1,2**64 - 1)) for i in range(4)]
    zobTurn = (randint(1,2**64 - 1))
    ttable = {} 
    """
    Table entries with form:
    ```
    12345678738627 : {
            "score": 123,
            "depth": 3,
            "move" : moveObject,
    }
    ```
    """

    isWhiteTurn = True
    castleRight = 15 #1111 default
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
            self.convertCastleRightsToBitboard(splittedFEN[2])
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
        
    def convertCastleRightsToBitboard(self, castleRight:str):
        self.castleRight = 0
        if castleRight == '-':
            return
        for cR in castleRight:
            if cR == 'K':
                self.castleRight |= K_Flag
            elif cR == 'Q':
                self.castleRight |= Q_Flag
            elif cR == 'k':
                self.castleRight |= k_Flag
            elif cR == 'q':
                self.castleRight |= q_Flag

    def stringifyCastleRights(self):
        if self.castleRight == 0:
            return '-'
        result = ""
        if self.castleRight & K_Flag:
            result+="K"
        if self.castleRight & Q_Flag:
            result+="Q"
        if self.castleRight & k_Flag:
            result+="k"
        if self.castleRight & q_Flag:
            result+="q"
        return result

    def convertArraysToBitboards(self):
        for i in range(64):
            binary = ZERO_STRING[i+1:] + "1" + ZERO_STRING[0:i]
            num = (int(binary, 2))
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
            if (self.WP >> i) & 1 == 1:
                newChessBoard[row][col] = "P"
            elif (self.WN >> i) & 1 == 1:
                newChessBoard[row][col] = "N"
            elif (self.WB >> i) & 1 == 1:
                newChessBoard[row][col] = "B"
            elif (self.WR >> i) & 1 == 1:
                newChessBoard[row][col] = "R"
            elif (self.WQ >> i) & 1 == 1:
                newChessBoard[row][col] = "Q"
            elif (self.WK >> i) & 1 == 1:
                newChessBoard[row][col] = "K"
            elif (self.BP >> i) & 1 == 1:
                newChessBoard[row][col] = "p"
            elif (self.BN >> i) & 1 == 1:
                newChessBoard[row][col] = "n"
            elif (self.BB >> i) & 1 == 1:
                newChessBoard[row][col] = "b"
            elif (self.BR >> i) & 1 == 1:
                newChessBoard[row][col] = "r"
            elif (self.BQ >> i) & 1 == 1:
                newChessBoard[row][col] = "q"
            elif (self.BK >> i) & 1 == 1:
                newChessBoard[row][col] = "k"

        return newChessBoard
    
    def genZobHash(self):
        hash = 0
        for i in range(64):
            if (self.WP >> i) & 1 == 1:
                hash ^= self.zobTable[i][0]
            elif (self.BP >> i) & 1 == 1:
                hash ^= self.zobTable[i][1]
            elif (self.WN >> i) & 1 == 1:
                hash ^= self.zobTable[i][2]
            elif (self.BN >> i) & 1 == 1:
                hash ^= self.zobTable[i][3]
            elif (self.WB >> i) & 1 == 1:
                hash ^= self.zobTable[i][4]
            elif (self.BB >> i) & 1 == 1:
                hash ^= self.zobTable[i][5]
            elif (self.WR >> i) & 1 == 1:
                hash ^= self.zobTable[i][6]
            elif (self.BR >> i) & 1 == 1:
                hash ^= self.zobTable[i][7]
            elif (self.WQ >> i) & 1 == 1:
                hash ^= self.zobTable[i][8]
            elif (self.BQ >> i) & 1 == 1:
                hash ^= self.zobTable[i][9]
            elif (self.WK >> i) & 1 == 1:
                hash ^= self.zobTable[i][10]
            elif (self.BK >> i) & 1 == 1:
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
        return hash
    
    def getFEN(self):
        rows = []
        chessArray = self.convertBitboardsToArray()
        for row in chessArray:
            newRow = ''
            for field in row:
                if field =='':
                    newRow+='1'
                else:
                    newRow+=field
            newRow = re.sub('11+', lambda m: str(len(m.group())), newRow)
            rows.append(newRow)
        board = '/'.join(rows)
        player = 'w' if self.isWhiteTurn else 'b'
        return f'{board} {player} {self.stringifyCastleRights()} {self.enPassant} {self.halfmoveClock} {self.fullmoveCount}'

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
        self.getMovesB()
        self.getMovesN()
        self.getMovesQ()
        self.getMovesR()
        self.getMovesK()
        self.getMovesP()
        return self.moves

        
    
    def possibleMovesB(self):
        #added WK to avoid illegal capture
        self.NOT_MY_PIECES=~(self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK|self.WK)
        #omitted BK to avoid illegal capture
        self.MY_PIECES=self.BP|self.BN|self.BB|self.BR|self.BQ
        self.OCCUPIED=self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        self.EMPTY=~self.OCCUPIED
        self.getMovesB()
        self.getMovesN()
        self.getMovesQ()
        self.getMovesR()
        self.getMovesK()
        self.getMovesP()
        return self.moves 

    
    def getMovesP(self):
        # exluding black king, because he can't be eaten
        BLACK_PIECES = (self.BP | self.BN | self.BB | self.BR | self.BQ)
        
        # same here
        WHITE_PIECES = self.WP | self.WN | self.WB | self.WR | self.WQ

        # beat right
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> 7) & BLACK_PIECES & int(~RANK_8 & ~FILE_A)
            PAWN_MOVES_PROMO = (self.WP >> 7) & BLACK_PIECES & self.OCCUPIED & int(RANK_8 & ~FILE_A)
            color = 1
            type = 'P' 
        else: 
            PAWN_MOVES = (self.BP << 7) & WHITE_PIECES  & int(~RANK_1 & ~FILE_H)
            PAWN_MOVES_PROMO = (self.BP << 7) & WHITE_PIECES & self.OCCUPIED & int(RANK_1 & ~FILE_H)
            color = -1
            type = 'p'
        
        # beat right normal
        possibility = PAWN_MOVES&~(PAWN_MOVES-1)
        while possibility != 0:
            move = {}
            i = trailingZeros(possibility)
            destination = ((i//8)*8 + (i % 8))
            move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x" + makeField((i//8), i % 8)
            move['from'] = (((i//8)+(color*1))*8+((i % 8)-(color*1)))
            move['to'] = destination
            move['type'] = type
            move['score'] = self.evaluateMove(self.isWhiteTurn, 1, destination)
            self.moves.append(move)

            PAWN_MOVES&=~possibility
            possibility=PAWN_MOVES&~(PAWN_MOVES-1)

        # beat right with promo
        possibility = PAWN_MOVES_PROMO&~(PAWN_MOVES_PROMO-1)
        while possibility != 0:
            move = {}
            i = trailingZeros(possibility)
            destination = ((i//8)*8 + (i % 8))
            move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x" + makeField((i//8), i % 8)
            move['from'] = (((i//8)+(color*1))*8+((i % 8)-(color*1)))
            move['to'] = destination
            move['type'] = type
            move['isPromo'] = True
            move['score'] = self.evaluateMove(self.isWhiteTurn, 1, destination) + 10
            self.promoHelper(self.isWhiteTurn, move)

            PAWN_MOVES_PROMO&=~possibility
            possibility=PAWN_MOVES_PROMO&~(PAWN_MOVES_PROMO-1)

        # beat left
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> 9) & BLACK_PIECES  & int(~RANK_8 & ~FILE_H)
            PAWN_MOVES_PROMO = (self.WP >> 9) & BLACK_PIECES & self.OCCUPIED & int(RANK_8 & ~FILE_H)
        else:
            PAWN_MOVES = (self.BP << 9) & WHITE_PIECES  & int(~RANK_1 & ~FILE_A)
            PAWN_MOVES_PROMO = (self.BP << 9) & WHITE_PIECES & self.OCCUPIED & int(RANK_1 & ~FILE_A)
        
        # beat left normal
        possibility = PAWN_MOVES&~(PAWN_MOVES-1)
        while possibility != 0:
            move = {}
            i = trailingZeros(possibility)
            destination = ((i//8)*8+(i % 8))
            move['toString'] = makeField((i//8)+(color*1), (i % 8)+(color*1)) + "x"+makeField((i//8), i % 8)
            move['from'] = (((i//8)+(color*1))*8+((i % 8)+(color*1))) 
            move['to'] = destination
            move['type'] = type
            move['score'] = self.evaluateMove(self.isWhiteTurn, 1, destination)
            self.moves.append(move)

            PAWN_MOVES&=~possibility
            possibility=PAWN_MOVES&~(PAWN_MOVES-1)
        
        # beat left promo
        possibility = PAWN_MOVES_PROMO&~(PAWN_MOVES_PROMO-1)
        while possibility != 0:
            move = {}
            i = trailingZeros(possibility)
            destination = ((i//8)*8+(i % 8))
            move['toString'] = makeField((i//8)+(color*1), (i % 8)+(color*1)) + "x"+makeField((i//8), i % 8)
            move['from'] = (((i//8)+(color*1))*8+((i % 8)+(color*1))) 
            move['to'] = destination
            move['type'] = type
            move['isPromo'] = True
            move['score'] = self.evaluateMove(self.isWhiteTurn, 1, destination) + 10
            self.promoHelper(self.isWhiteTurn, move)

            PAWN_MOVES_PROMO&=~possibility
            possibility=PAWN_MOVES_PROMO&~(PAWN_MOVES_PROMO-1)

        # move 1 forward
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> 8) & self.EMPTY & int(~RANK_8)
            PAWN_MOVES_PROMO = (self.WP >> 8) & self.EMPTY & int(RANK_8)
        else:
            PAWN_MOVES = (self.BP << 8) & self.EMPTY & int(~RANK_1)
            PAWN_MOVES_PROMO = (self.BP << 8) & self.EMPTY & int(RANK_1)
        
        # move 1 forward normal
        possibility = PAWN_MOVES&~(PAWN_MOVES-1)
        while possibility != 0:
            i = trailingZeros(possibility)
            move = {}
            move['toString'] = makeField((i//8)+(color*1), (i % 8))+makeField((i//8), i % 8)
            move['from'] = (((i//8)+(color*1))*8+(i % 8))
            move['to'] = ((i//8)*8+(i%8))
            move['type'] = type
            move['score'] = 0
            self.moves.append(move)

            PAWN_MOVES&=~possibility
            possibility=PAWN_MOVES&~(PAWN_MOVES-1)

        # move 1 forward promo
        possibility = PAWN_MOVES_PROMO&~(PAWN_MOVES_PROMO-1)
        while possibility != 0:
            i = trailingZeros(possibility)
            move = {}
            move['toString'] = makeField((i//8)+(color*1), (i % 8))+makeField((i//8), i % 8)
            move['from'] = (((i//8)+(color*1))*8+(i % 8))
            move['to'] = ((i//8)*8+(i%8))
            move['type'] = type
            move['isPromo'] = True
            move['score'] = 10
            self.promoHelper(self.isWhiteTurn, move)

            PAWN_MOVES_PROMO&=~possibility
            possibility=PAWN_MOVES_PROMO&~(PAWN_MOVES_PROMO-1)

        # move 2 forward
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> 16) & self.EMPTY & (self.EMPTY >> 8) & int(RANK_4)
        else:
            PAWN_MOVES = (self.BP << 16) & self.EMPTY & (self.EMPTY << 8) & int(RANK_5)
        
        possibility = PAWN_MOVES&~(PAWN_MOVES-1)
        while possibility != 0:
            i = trailingZeros(possibility)
            move = {}
            move['toString'] = makeField((i//8)+(color*2), (i % 8))+makeField((i//8), i % 8)
            move['from'] = (((i//8)+(color*2))*8+(i%8))
            move['to'] = ((i//8)*8+(i % 8))
            move['type'] = type
            move['double'] = makeField((i//8)+(color*1), i % 8)
            move['score'] = 0
            self.moves.append(move)

            PAWN_MOVES&=~possibility
            possibility=PAWN_MOVES&~(PAWN_MOVES-1)

        if self.enPassant != '-':
            RANK = FileMasks8[self.enPassant[0]]

            # en passant right
            if self.isWhiteTurn:
                PAWN_MOVES = (self.WP << 1) & self.BP & int(RANK_5 & ~FILE_A & RANK)
            else:
                PAWN_MOVES = (self.BP >> 1) & self.WP & int(RANK_4 & ~FILE_H & RANK)
            
            possibility = PAWN_MOVES&~(PAWN_MOVES-1)
            while possibility != 0:
                move = {}
                i = trailingZeros(possibility)
                if self.isWhiteTurn:
                    destination = (((((i//8)-(color*1))+1)*8)+(i % 8))
                else:
                    destination = (((((i//8)-(color*1))-1)*8)+(i % 8))
                move['toString'] = makeField((i//8), i % 8-(color*1))+'x'+makeField((i//8)-(color*1), i % 8)
                move['from'] = (((i//8)*8)+(i%8-(color*1)))
                move['to'] = (((i//8)-(color*1))*8+(i % 8))
                move['type'] = type
                move['enPassant'] = True
                move['enemy'] = destination
                move['score'] = self.evaluateMove(self.isWhiteTurn, 1, destination)
                self.moves.append(move)

                PAWN_MOVES_PROMO&=~possibility
                possibility=PAWN_MOVES_PROMO&~(PAWN_MOVES_PROMO-1)

            # en passant left
            if self.isWhiteTurn:
                PAWN_MOVES = (self.WP >> 1) & self.BP & int(RANK_5 & ~FILE_H & RANK)
            else:
                PAWN_MOVES = (self.BP << 1) & self.WP & int(RANK_4 & ~FILE_A & RANK)

            possibility = PAWN_MOVES&~(PAWN_MOVES-1)
            while possibility != 0:
                move = {}
                i = trailingZeros(possibility)
                if self.isWhiteTurn:
                    destination = (((((i//8)-(color*1))+1)*8)+(i % 8))
                else:
                    destination = (((((i//8)-(color*1))-1)*8)+(i % 8))
                move['toString'] = makeField((i//8), i % 8+(color*1))+'x'+ makeField((i//8) -(color*1), i % 8)
                move['from'] = (((i//8)*8)+(i % 8+(color*1)))
                move['to'] = (((i//8)-(color*1))*8+(i % 8))
                move['type'] = type
                move['enPassant'] = True
                move['enemy'] = destination
                move['score'] = self.evaluateMove(self.isWhiteTurn, 1, destination)
                self.moves.append(move)

                PAWN_MOVES_PROMO&=~possibility
                possibility=PAWN_MOVES_PROMO&~(PAWN_MOVES_PROMO-1)

    
    def promoHelper(self, isWhiteTurn:bool ,move):
        type = 'R' if isWhiteTurn else 'r'
        moveR = copy(move)
        moveR['promoType'] = type
        moveR['toString'] += type
        moveR['score'] += 5
        self.moves.append(moveR)
        type = 'Q' if isWhiteTurn else 'q' 
        moveQ = copy(move)
        moveQ['promoType'] = type
        moveQ['toString'] += type
        moveQ['score'] += 9
        self.moves.append(moveQ)
        type = 'B' if isWhiteTurn else 'b'
        moveB = copy(move)
        moveB['promoType'] = type
        moveB['toString'] += type
        moveB['score'] += 3
        self.moves.append(moveB)
        type = 'N' if isWhiteTurn else 'n'
        moveN = copy(move)
        moveN['promoType'] = type
        moveN['toString'] += type
        moveN['score'] += 3
        self.moves.append(moveN)

    def HAndVMoves(self, s, OCCUPIED_CUSTOM = None):
        OCCUPIED = OCCUPIED_CUSTOM if OCCUPIED_CUSTOM else (self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK)
        return self.get_rank_moves_bb(s, OCCUPIED) | self.get_file_moves_bb(s, OCCUPIED)
    
    def DAndAntiDMoves(self, s:int, OCCUPIED_CUSTOM = None):
        OCCUPIED = OCCUPIED_CUSTOM if OCCUPIED_CUSTOM else (self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK)
        return self.get_diag_moves_bb(s, OCCUPIED) | self.get_antidiag_moves_bb(s, OCCUPIED)

    def get_rank_moves_bb(self, i, occ):
        """
        i is index of square
        occ is the combined occupancy of the board
        """
        f = i & 7
        occ = RankMasks8[i//8] & np.uint64(occ) # isolate rank occupancy
        occ = np.multiply(FILE_A, occ) >> np.uint8(56) # map to first rank
        occ = FILE_A * FIRST_RANK_MOVES[f][occ] # lookup and map back to rank
        return int(RankMasks8[i//8] & occ)

    def get_file_moves_bb(self, i, occ):
        """
        i is index of square
        occ is the combined occupancy of the board
        """
        f = i & 7
        # Shift to A file
        occ = FILE_A & np.uint64(occ) >> np.uint8(f)
        # Map occupancy and index to first rank
        occ = np.multiply(A1H8_DIAG, occ) >> np.uint8(56)
        first_rank_index = (i ^ 56) >> 3
        # Lookup moveset and map back to H file
        occ = np.multiply(A1H8_DIAG, FIRST_RANK_MOVES[first_rank_index][occ])
        # Isolate H file and shift back to original file
        return int(FILE_H & occ) >> (f ^ 7)

    def get_diag_moves_bb(self, i, occ):
        """
        i is index of square
        occ is the combined occupancy of the board
        """
        f = i & 7
        occ = DiagonalMasks8[(i // 8) + (i % 8)] & np.uint64(occ) # isolate diagonal occupancy
        occ = np.multiply(FILE_A , occ) >> np.uint8(56) # map to first rank
        occ = FILE_A * FIRST_RANK_MOVES[f][occ] # lookup and map back to diagonal
        return int(DiagonalMasks8[(i // 8) + (i % 8)] & occ)

    def get_antidiag_moves_bb(self, i, occ):
        """
        i is index of square
        occ is the combined occupancy of the board
        """
        f = i & 7
        occ = AntiDiagonalMasks8[(i // 8) + 7 - (i % 8)] & np.uint64(occ) # isolate antidiagonal occupancy
        occ = np.multiply(FILE_A, occ) >> np.uint8(56) # map to first rank
        occ = FILE_A * FIRST_RANK_MOVES[f][occ] # lookup and map back to antidiagonal
        return int(AntiDiagonalMasks8[(i // 8) + 7 - (i % 8)] & occ)
    
    def getMovesB(self):
        if self.isWhiteTurn:
            type = 'B'
            B = self.WB
        else:
            type = 'b'
            B = self.BB
        i = B&~(B-1)
        while(i != 0):
            bLocation = trailingZeros(i)
            possibility = self.DAndAntiDMoves(bLocation) & self.NOT_MY_PIECES
            j = possibility & ~(possibility-1)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                destination = (((index//8)*8)+(index%8))
                score = self.evaluateMove(self.isWhiteTurn, 3, destination)
                move['toString'] = "B"+makeField((bLocation//8),bLocation%8)+('x'if score !=0 else '')+makeField((index//8),index%8)
                move['from'] = (((bLocation//8)*8)+(bLocation%8))
                move['to'] = destination
                move['type'] = type
                move['score'] = score
                self.moves.append(move)

                possibility&=~j
                j = possibility & ~(possibility-1)
            B &= ~i
            i = B&~(B-1)
    
    def getMovesR(self):
        if self.isWhiteTurn:
            type = 'R'
            R = self.WR
        else:
            type = 'r'
            R = self.BR
        i = R&~(R-1)
        while(i != 0):
            rLocation = trailingZeros(i)
            possibility = self.HAndVMoves(rLocation) & self.NOT_MY_PIECES
            j = possibility & ~(possibility-1)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                destination = (((index//8)*8)+(index%8))
                score = self.evaluateMove(self.isWhiteTurn, 5, destination)
                move['toString'] = "R"+makeField((rLocation//8),rLocation%8)+('x'if score !=0 else '')+makeField((index//8),index%8)
                move['from'] = (((rLocation//8)*8)+(rLocation%8))
                move['to'] = destination
                move['type'] = type
                move['score'] = score
                self.moves.append(move)      

                possibility&=~j
                j = possibility & ~(possibility-1)
            R &= ~i
            i = R&~(R-1)
    
    def getMovesQ(self):
        if self.isWhiteTurn:
            type = 'Q'
            Q = self.WQ
        else:
            type = 'q'
            Q = self.BQ
        i = Q&~(Q-1)
        while(i != 0):
            qLocation = trailingZeros(i)
            possibility = (self.DAndAntiDMoves(qLocation) | self.HAndVMoves(qLocation) )& self.NOT_MY_PIECES
            j = possibility & ~(possibility-1)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                destination = (((index//8)*8)+(index%8))
                score = self.evaluateMove(self.isWhiteTurn, 9, destination)
                move['toString'] = "Q"+makeField((qLocation//8),qLocation%8)+('x'if score !=0 else '')+makeField((index//8),index%8)
                move['from'] = (((qLocation//8)*8)+(qLocation%8))
                move['to'] = destination
                move['type'] = type
                move['score'] = score
                self.moves.append(move)

                possibility&=~j
                j = possibility & ~(possibility-1)
            Q &= ~i
            i = Q&~(Q-1)


    def getMovesN(self):  
        if self.isWhiteTurn:
            type = 'N'
            N = self.WN
        else:
            type = 'n'
            N = self.BN  
        i = N &~(N - 1)
        while i != 0:
            nLoc = trailingZeros(i)
            if nLoc >  18:
                possibility = KNIGHT_SPAN << (nLoc-18)
            else:
                possibility = KNIGHT_SPAN >> (18 - nLoc)
            if nLoc%8 < 4:
                possibility &= int(~FILE_GH) & self.NOT_MY_PIECES
            else:
                possibility &= int(~FILE_AB) & self.NOT_MY_PIECES
            j = possibility &~(possibility-1)
            while j != 0:
                move = {}
                index = trailingZeros(j) 
                destination = (((index//8)*8)+(index%8))
                score = self.evaluateMove(self.isWhiteTurn, 3, destination)
                move['toString'] = "N"+makeField((nLoc//8),nLoc%8)+('x' if score!=0 else '')+makeField((index//8),index%8)
                move['from'] = (((nLoc//8)*8)+(nLoc%8))
                move['to'] = destination
                move['type'] = type
                move['score'] = score
                self.moves.append(move) 

                possibility&=~j
                j=possibility&~(possibility-1)
            N &=~i
            i = N &~(N-1)
    
    def getMovesK(self):
        if self.isWhiteTurn:
            type = 'K'
            K = self.WK
            castleRightK = self.castleRight & K_Flag
            castleRightQ = self.castleRight & Q_Flag
            castleK = CASTLE_MASKS['K']
            castleQ = CASTLE_MASKS['Q']
        else:
            type = 'k'
            K = self.BK
            castleRightK = self.castleRight & k_Flag
            castleRightQ = self.castleRight & q_Flag
            castleK = CASTLE_MASKS['k']
            castleQ = CASTLE_MASKS['q']

        isWhiteKing = K & self.WK > 0 
        kLoc = trailingZeros(K)
        if kLoc >  9:
            possibility = KING_SPAN << (kLoc-9)
        else:
            possibility = KING_SPAN >> (9 - kLoc)
        if kLoc%8 < 4:
            possibility &= int(~FILE_GH) & self.NOT_MY_PIECES
        else:
            possibility &= int(~FILE_AB) & self.NOT_MY_PIECES
        j = possibility &~(possibility-1)
        safe = ~self.unsafeFor(isWhiteKing)

        if castleRightK and castleK & safe & self.EMPTY == castleK :
            move = {}
            move['toString'] = "0-0"
            move['type'] = type
            move['castle'] = "k"
            move['score'] = 9
            self.moves.append(move)
        if castleRightQ and castleQ & safe & self.EMPTY == castleQ :
            move = {}
            move['toString'] = "0-0-0"
            move['type'] = type
            move['castle'] = "q"
            move['score'] = 9
            self.moves.append(move)
            
        while j != 0:
            if j & safe != 0: #filters out unsafe fields
                index = trailingZeros(j) 
                move = {}
                destination = (((index//8)*8)+(index%8))
                score = self.evaluateMove(self.isWhiteTurn, 9, destination)
                move['toString'] = "K"+makeField((kLoc//8),kLoc%8)+('x'if score !=0 else '')+makeField((index//8),index%8)
                move['from'] = (((kLoc//8)*8)+(kLoc%8))
                move['to'] = destination
                move['type'] = type
                move['score'] = score
                self.moves.append(move)
            possibility&=~j
            j=possibility&~(possibility-1)

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
            unsafe = (P<<7) & int(~FILE_H )
            unsafe |= (P<<9) & int(~FILE_A)
        else:
            P = self.WP
            N = self.WN
            QB = self.WQ|self.WB
            QR = self.WQ|self.WR
            K = self.WK
            #white pawn
            unsafe = (P>>7) & int(~FILE_A )
            unsafe |= (P>>9) & int(~FILE_H)

        
        #knight
        i = N &~(N-1)
        while i != 0:
            iLoc = trailingZeros(i)
            if iLoc > 18:
                possibility = KNIGHT_SPAN << (iLoc - 18)
            else:
                possibility = KNIGHT_SPAN >> (18 - iLoc)
            if iLoc % 8 < 4:
                possibility &= int(~FILE_GH)
            else:
                possibility &= int(~FILE_AB)
            unsafe |= possibility
            N &=~i
            i = N & ~(N-1)
            
        #(anti)diagonal sliding pieces (bishop & queen)
        i = QB &~(QB-1)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLoc, self.WP|self.WN|self.WB|self.WR|self.WQ|self.BP|self.BN|self.BB|self.BR|self.BQ)
            unsafe |= possibility
            QB&=~i
            i=QB&~(QB-1)
            
        #staight sliding pieces (rook & queen)
        i = QR &~(QR-1)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.HAndVMoves(iLoc, self.WP|self.WN|self.WB|self.WR|self.WQ|self.BP|self.BN|self.BB|self.BR|self.BQ)
            unsafe |= possibility
            QR&=~i
            i=QR&~(QR-1)
        
        #king
        iLoc = trailingZeros(K)
        if iLoc > 9:
            possibility = KING_SPAN<<(iLoc-9)
        else:
            possibility = KING_SPAN>>(9 -iLoc)
        if iLoc % 8 < 4:
            possibility &=int(~FILE_GH)
        else:
            possibility &=int(~FILE_AB)
        unsafe |= possibility
        
        return unsafe

    def filterMoves(self, moves):
        newMoves = []
        for move in moves:
            type = move['type']
            if type == 'K' or type == 'k':
                newMoves.append(move)
            else:
                ownValue = 0
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
                safe = self.leavesNotInCheck(self.isWhiteTurn, newBoard, move['to'])
                if safe:
                    newMoves.append(move)
        return sorted(newMoves, key=lambda x: x.get('score', 0), reverse=True)

    def leavesNotInCheck(self, isForWhite: bool, board = None, destination = None):
        if isForWhite:
            P = (self.BP)
            N = (self.BN)
            QB = (self.BQ|self.BB)
            QR = (self.BQ|self.BR)
            K = (self.BK)
            myK = (self.WK)
            dest = (1<<destination)
            P&=~dest
            N&=~dest
            QB&=~dest
            QR&=~dest
            K&=~dest
            #black pawn
            if ((P<<7) & int(~FILE_H))&myK != 0:
                return False
            if ((P<<9) & int(~FILE_A))&myK != 0: 
                return False
        else:
            P = (self.WP)
            N = (self.WN)
            QB = (self.WQ|self.WB)
            QR = (self.WQ|self.WR)
            K = (self.WK)
            myK = self.BK
            P&=~(1<<destination)
            N&=~(1<<destination)
            QB&=~(1<<destination)
            QR&=~(1<<destination)
            K&=~(1<<destination)
            #white pawn
            if ((P>>7) & int(~FILE_A))&myK !=0:
                return False
            if ((P>>9) & int(~FILE_H))&myK != 0:
                return False
        
        OCCUPIED = np.uint(board|P|N|QB|QR|K)
        
        #knight
        i = N &~(N-1)
        while i != 0:
            iLoc = trailingZeros(i)
            if iLoc > 18:
                possibility = KNIGHT_SPAN <<(iLoc - 18)
            else:
                possibility = KNIGHT_SPAN >> (18 - iLoc)
            if iLoc % 8 < 4:
                possibility &= int(~FILE_GH)
            else:
                possibility &= int(~FILE_AB)
            if (possibility) & myK !=0:
                return False
            N &=~i
            i = N & ~(N-1)
            
        #(anti)diagonal sliding pieces (bishop & queen)
        i = QB &~(QB-1)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLoc, OCCUPIED)
            if possibility & myK !=0:
                return False
            QB&=~i
            i=QB&~(QB-1)
            
        #staight sliding pieces (rook & queen)
        i = QR &~(QR-1)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.HAndVMoves(iLoc, OCCUPIED)
            if possibility & myK != 0:
                return False
            QR&=~i
            i=QR&~(QR-1)
        
        #king
        iLoc = trailingZeros(K)
        if iLoc > 9:
            possibility = KING_SPAN<<(iLoc-9)
        else:
            possibility = KING_SPAN>>(9 -iLoc)
        if iLoc % 8 < 4:
            possibility &=int(~FILE_GH)
        else:
            possibility &=int(~FILE_AB)
        if (possibility) & myK != 0:
            return False
        
        return True

    def doMove(self, move):
        undoMove = []
        type = move['type']
        if type == 'P' or type =='p':
            return self.doMovePawn(move)
        if type == 'K' or type =='k':
            return self.doMoveKing(move)

        if type.isupper():
            if type == 'B':
                self.WB = self.doMoveHelper(move, self.WB, undoMove)
                self.updateHash(move, 4, undoMove)
            elif type == 'N':
                self.WN = self.doMoveHelper(move, self.WN, undoMove)
                self.updateHash(move, 2, undoMove)
            elif type == 'R':
                self.WR = self.doMoveHelper(move, self.WR, undoMove)
                self.updateHash(move, 6, undoMove)
                if self.WR & int(FILE_A) & int(RANK_1) == 0 and self.castleRight & Q_Flag:
                    undoMove.append(('castle', self.castleRight))
                    self.castleRight ^= Q_Flag
                if self.WR & int(FILE_H) & int(RANK_1) == 0 and self.castleRight & K_Flag:
                    undoMove.append(('castle', self.castleRight))
                    self.castleRight ^= K_Flag
            elif type == 'Q':
                self.WQ = self.doMoveHelper(move, self.WQ, undoMove)
                self.updateHash(move, 8, undoMove)
        else:
            if type == 'b':
                self.BB = self.doMoveHelper(move, self.BB, undoMove)
                self.updateHash(move, 5, undoMove)
            elif type == 'n':
                self.BN = self.doMoveHelper(move, self.BN, undoMove)
                self.updateHash(move, 3, undoMove)
            elif type == 'r':
                self.BR = self.doMoveHelper(move, self.BR, undoMove)
                self.updateHash(move, 7, undoMove)
                if self.BR & int(FILE_A) & int(RANK_8) == 0 and self.castleRight & q_Flag:
                    undoMove.append(('castle', self.castleRight)) 
                    self.castleRight ^= q_Flag
                if self.BR & int(FILE_H) & int(RANK_8) == 0 and self.castleRight & k_Flag:
                    undoMove.append(('castle', self.castleRight))
                    self.castleRight ^= k_Flag
            elif type == 'q':
                self.BQ = self.doMoveHelper(move, self.BQ, undoMove)
                self.updateHash(move, 9, undoMove)
  
        self.clearDestination(type.isupper(), move['to'], undoMove)
        if not self.isWhiteTurn:
            undoMove.append(('fullmove', self.fullmoveCount))
            self.fullmoveCount+=1
        self.isWhiteTurn = not self.isWhiteTurn
        undoMove.append(('enPassant', self.enPassant))
        self.enPassant = '-'
        self.MOVE_HISTORY.append(undoMove)
        # boardString = getBoardStr(self) #might be replaced with hash function later
        # if boardString in self.STATE_HISTORY:
        #     self.STATE_HISTORY[boardString] += 1
        # else:
        #     self.STATE_HISTORY[boardString] = 1

    def doMoveHelper(self, move, BOARD, undoMove:array = None):
        if undoMove is not None:
            undoMove.append((move['type'], BOARD))

        start = move['from']
        end = move['to']
        BOARD &= ~(1 << start)
        BOARD |= (1 << end)
        return BOARD

    def doMoveKing(self, move):
        undoMove = []
        type = move['type']
        castle = move.get('castle')
        undoMove.append(('castle', self.castleRight))
        undoMove.append(('enPassant', self.enPassant))

        if not castle:
            start = move['from']
            end = move['to']
            if type.isupper():
                undoMove.append((type, self.WK))
                self.WK &= ~(1 << start)
                self.WK |= (1 << end)
                if self.castleRight & K_Flag: self.castleRight ^= K_Flag
                if self.castleRight & Q_Flag: self.castleRight ^= Q_Flag
                self.updateHash(move, 10, undoMove)
                self.clearDestination(True, end, undoMove)
            else:
                undoMove.append((type, self.BK))
                self.BK &= ~(1 << start)
                self.BK |= (1 << end)
                if self.castleRight & k_Flag: self.castleRight ^= k_Flag
                if self.castleRight & q_Flag: self.castleRight ^= q_Flag
                self.updateHash(move, 11, undoMove)
                self.clearDestination(False, end, undoMove) 
        else:
            if type.isupper():
                if castle == 'q':
                    undoMove.append((type, self.WK))
                    self.WK >>= 2
                    self.updateHash({'from':60, 'to':58}, 10, undoMove)
                    undoMove.append(('R', self.WR))
                    self.WR ^= 72057594037927936
                    self.WR |=(1 << 59)
                    self.hash ^= self.zobTable[56][6]
                    self.hash ^= self.zobTable[59][6]
                elif castle =='k':
                    undoMove.append((type, self.WK))
                    self.WK <<= 2
                    self.updateHash({'from':60, 'to':62}, 10, undoMove)
                    undoMove.append(('R', self.WR))
                    self.WR ^= 9223372036854775808
                    self.WR |=(1 << 61)
                    self.hash ^= self.zobTable[63][6]
                    self.hash ^= self.zobTable[61][6]
                if self.castleRight & K_Flag: self.castleRight ^= K_Flag
                if self.castleRight & Q_Flag: self.castleRight ^= Q_Flag
            else:
                if castle == 'q':
                    undoMove.append((type, self.BK))
                    self.BK >>= 2
                    self.updateHash({'from':4, 'to':2}, 11, undoMove)
                    undoMove.append(('r', self.BR))
                    self.BR ^= 1
                    self.BR |=(1 << 3)
                    self.hash ^= self.zobTable[0][7]
                    self.hash ^= self.zobTable[3][7]
                elif castle == 'k':
                    undoMove.append((type, self.BK))
                    self.BK <<= 2
                    self.updateHash({'from':4, 'to':6}, 11, undoMove)
                    undoMove.append(('r', self.BR))
                    self.BR ^= 128
                    self.BR |=(1 << 5)
                    self.hash ^= self.zobTable[7][7]
                    self.hash ^= self.zobTable[5][7]
                if self.castleRight & k_Flag: self.castleRight ^= k_Flag
                if self.castleRight & q_Flag: self.castleRight ^= q_Flag
            undoMove.append(('halfmove', self.halfmoveClock))
            self.halfmoveClock += 1

        if not self.isWhiteTurn:
            undoMove.append(('fullmove', self.fullmoveCount))
            self.fullmoveCount+=1
        self.isWhiteTurn = not self.isWhiteTurn
        self.enPassant = '-'
        self.MOVE_HISTORY.append(undoMove)

    def doMovePawn(self, move):
        undoMove = []
        start = move['from']
        end = move['to']
        type = move['type']
        undoMove.append(('enPassant', self.enPassant))

        if not move.get('isPromo'):
            if move.get('enPassant'):
                destination = move['enemy']
            else:
                destination = end
            
            if type.isupper():
                undoMove.append((type, self.WP))
                self.WP &= ~(1 << start)
                self.WP |= (1 << end)

                self.updateHash(move, 0, undoMove)
                self.clearDestination(True, destination, undoMove)

            else:
                undoMove.append((type, self.BP))
                self.BP &= ~(1 << start)
                self.BP |= (1 << end)
                self.updateHash(move, 1, undoMove)
                self.clearDestination(False, destination, undoMove) 

            if move.get('double'):
                self.enPassant = move['double']
            else:
                self.enPassant = '-'

        else:
            undoMove.append(('hash', self.hash))
            if type.isupper():
                undoMove.append((type, self.WP))
                self.WP &= ~(1 << start)
                self.hash ^= self.zobTable[start][0]
            else:
                undoMove.append((type, self.BP))
                self.BP &= ~(1 << start)
                self.hash ^= self.zobTable[start][1]

            promoType = move['promoType']
            if promoType == 'Q':
                oldBoard = self.WQ
                self.WQ |= (1 << end)
                self.hash ^= self.zobTable[end][8]
            elif promoType == 'R':
                oldBoard = self.WR
                self.WR |= (1 << end)
                self.hash ^= self.zobTable[end][6]
            elif promoType == 'B':
                oldBoard = self.WB
                self.WB |= (1 << end)
                self.hash ^= self.zobTable[end][4]
            elif promoType == 'N':
                oldBoard = self.WN
                self.WN |= (1 << end)
                self.hash ^= self.zobTable[end][2]
            elif promoType == 'q':
                oldBoard = self.BQ
                self.BQ |= (1 << end)
                self.hash ^= self.zobTable[end][9]
            elif promoType == 'r':
                oldBoard = self.BR
                self.BR |= (1 << end)
                self.hash ^= self.zobTable[end][7]
            elif promoType == 'b':
                oldBoard = self.BB
                self.BB |= (1 << end)
                self.hash ^= self.zobTable[end][5]
            elif promoType == 'n':
                oldBoard = self.BN
                self.BN |= (1 << end)
                self.hash ^= self.zobTable[end][3]

            undoMove.append((promoType, oldBoard))
            undoMove.append(('halfmove', self.halfmoveClock))
            self.enPassant = '-'

        if not self.isWhiteTurn:
            undoMove.append(('fullmove', self.fullmoveCount))
            self.fullmoveCount+=1
        self.halfmoveClock = 0
        self.isWhiteTurn = not self.isWhiteTurn
        self.MOVE_HISTORY.append(undoMove)

    def updateHash(self, move, value, undoMove:array):
        start = move['from']
        end = move['to']
        undoMove.append(('hash', self.hash))
        self.hash ^=self.zobTable[start][value]
        self.hash ^=self.zobTable[end][value]

    def clearDestination(self, isWhite:bool, destination:int, undoMove:array):
        undoMove.append(('halfmove', self.halfmoveClock))
        if isWhite:
            if (((self.BP >> destination) & 1) == 1):
                undoMove.append(('p', self.BP))
                self.BP &= ~(1 << destination)
                self.hash ^=self.zobTable[destination][1]
                self.halfmoveClock = 0
            elif (((self.BN >> destination) & 1) == 1):
                undoMove.append(('n', self.BN))
                self.BN&=~(1<<destination)
                self.hash ^=self.zobTable[destination][3]
                self.halfmoveClock = 0
            elif (((self.BQ >> destination) & 1) == 1):
                undoMove.append(('q', self.BQ))
                self.BQ&=~(1<<destination)
                self.hash ^=self.zobTable[destination][9]
                self.halfmoveClock = 0
            elif (((self.BB >> destination) & 1) == 1):
                undoMove.append(('b', self.BB))
                self.BB&=~(1<<destination)
                self.hash ^=self.zobTable[destination][5]
                self.halfmoveClock = 0
            elif (((self.BR >> destination) & 1) == 1):
                undoMove.append(('r', self.BR))
                self.BR&=~(1<<destination)
                self.hash ^=self.zobTable[destination][7]
                self.halfmoveClock = 0
            elif (((self.BK >> destination) & 1) == 1):
                undoMove.append(('k', self.BK))
                self.BK&=~(1<<destination) 
                self.hash ^=self.zobTable[destination][11]
                self.halfmoveClock = 0
            else:
                self.halfmoveClock += 1
        else:
            if (((self.WP >> destination) & 1) == 1):
                undoMove.append(('P', self.WP))
                self.WP &= ~(1 << destination)
                self.hash ^=self.zobTable[destination][0]
                self.halfmoveClock = 0
            elif (((self.WN >> destination) & 1) == 1):
                undoMove.append(('N', self.WN))
                self.WN&=~(1<<destination)
                self.hash ^=self.zobTable[destination][2]
                self.halfmoveClock = 0
            elif (((self.WQ >> destination) & 1) == 1):
                undoMove.append(('Q', self.WQ))
                self.WQ&=~(1<<destination)
                self.hash ^=self.zobTable[destination][8]
                self.halfmoveClock = 0
            elif (((self.WB >> destination) & 1) == 1):
                undoMove.append(('B', self.WB))
                self.WB&=~(1<<destination)
                self.hash ^=self.zobTable[destination][4]
            elif (((self.WR >> destination) & 1) == 1):
                undoMove.append(('R', self.WR))
                self.WR&=~(1<<destination)
                self.hash ^=self.zobTable[destination][6]
                self.halfmoveClock = 0
            elif (((self.WK >> destination) & 1) == 1):
                undoMove.append(('K', self.WK))
                self.WK&=~(1<<destination) 
                self.hash ^=self.zobTable[destination][10]
                self.halfmoveClock = 0
            else:
                self.halfmoveClock += 1

    def undoLastMove(self):
        if len(self.MOVE_HISTORY) == 0:
            return
        last = self.MOVE_HISTORY.pop()
        # self.STATE_HISTORY[getBoardStr(self)]-=1 #might be replaced with hash function later
        
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
            elif type == 'fullmove':
                self.fullmoveCount = value
            elif type == 'halfmove':
                self.halfmoveClock = value
        self.isWhiteTurn = not self.isWhiteTurn        
    
    def undoAllMoves(self):
        while len(self.MOVE_HISTORY) > 0:
            self.undoLastMove()
    
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
        
        movesW = self.possibleMovesW()
        movesB = self.possibleMovesB()
        simpleMobility = colorfactor*(len(movesW) - len(movesB))
        
        value = squarePieceBalance + simpleMobility
        
        if self.isCheck(): value = -10
        if self.isRemis(): value = -100
        if self.isCheckMate(): value = -10000
        if self.isKingOfTheHill(): value = 10000
        
        return value 
        
    def evaluateMove(self, isWhite, ownValue, destination):
        if isWhite:
            if (((self.BP >> destination) & 1) == 1):
                return 1  
            elif (((self.BN >> destination) & 1) == 1):
                if ownValue < 3:
                    return 3
                else:
                    return 1 
            elif (((self.BQ >> destination) & 1) == 1):
                if ownValue < 9:
                    return 9
                else:
                    return 1             
            elif (((self.BB >> destination) & 1) == 1):
                if ownValue < 3:
                    return 3
                else:
                    return 1            
            elif (((self.BR >> destination) & 1) == 1):
                if ownValue < 5:
                    return 5
                else:
                    return 1 
            elif (((self.BK >> destination) & 1) == 1):
                    return 9           
            else:
                return 0
        else:
            if (((self.WP >> destination) & 1) == 1):
                return 1 
            elif (((self.WN >> destination) & 1) == 1):
                if ownValue < 3:
                    return 3
                else:
                    return 1 
            elif (((self.WQ >> destination) & 1) == 1):
                if ownValue < 9:
                    return 9
                else:
                    return 1  
            elif (((self.WB >> destination) & 1) == 1):
                if ownValue < 3:
                    return 3
                else:
                    return 1  
            elif (((self.WR >> destination) & 1) == 1):
                if ownValue < 5:
                    return 5
                else:
                    return 1 
            elif (((self.WK >> destination) & 1) == 1):
              return 9
            else:
                return 0    
    
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
        # for key in self.STATE_HISTORY:
        #     if self.STATE_HISTORY[key] >= 3:
        #         return True
        return False

    def didOpponentWin(self, opponentIsWhite):
        return self.isGameDone() and not self.isWhiteTurn == opponentIsWhite
