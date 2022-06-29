import re
from tkinter import ON
import numpy as np
from helpers import *
from constants import *


def makeField(row, col):
    colNames = ["a", "b", "c", "d", "e", "f", "g", "h"]
    rowNames = ["8", "7", "6", "5", "4", "3", "2", "1"]
    return colNames[col] + rowNames[row]


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
    

    NOT_WHITE_PIECES = np.uint64(0)
    BLACK_PIECES = np.uint64(0)
    EMPTY = np.uint64(0)
    OCCUPIED = np.uint64(0)


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
            if (self.WN >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "N"
            if (self.WB >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "B"
            if (self.WR >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "R"
            if (self.WQ >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "Q"
            if (self.WK >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "K"
            if (self.BP >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "p"
            if (self.BN >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "n"
            if (self.BB >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "b"
            if (self.BR >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "r"
            if (self.BQ >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "q"
            if (self.BK >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "k"

        return newChessBoard

    def getMoves(self):
        # exluding black king, because he can't be eaten
        self.BLACK_PIECES = self.BP | self.BN | self.BB | self.BR | self.BQ
        
        # same here
        self.WHITE_PIECES = self.WP | self.WN | self.WB | self.WR | self.WQ

        #added BK to avoid illegal capture
        self.NOT_WHITE_PIECES = ~(self.WP | self.WN | self.WB | self.WR | self.WQ | self.WK | self.BK)

        self.OCCUPIED = self.WP | self.WN | self.WB | self.WR | self.WQ | self.WK | self.BP | self.BN | self.BB | self.BR | self.BQ | self.BK

        # board with empty fields
        self.EMPTY= ~self.OCCUPIED

        return self.getMovesWK()

    def getMovesP(self):
        moves = []
        color = 1
        if not self.isWhiteTurn:
            color = -1

        # beat right
        PAWN_MOVES = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & ~RANK_8 & ~ FILE_A
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & RANK_8 & ~FILE_A

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(7)) & self.WHITE_PIECES & ~RANK_1 & ~ FILE_H
            PAWN_MOVES_PROMO = (self.BP << np.uint64(7)) & self.WHITE_PIECES & RANK_1 & ~FILE_H

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE  == ONE :
                move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x" + makeField((i//8), i % 8)
                move['isHit'] = True
                moves.append(move)

        # beat left
        PAWN_MOVES = (self.WP >> np.uint64(9)) & self.BLACK_PIECES & ~RANK_8 & ~ FILE_H
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(9)) & self.BLACK_PIECES & RANK_8 & ~FILE_H

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(9)) & self.WHITE_PIECES & ~RANK_1 & ~ FILE_A
            PAWN_MOVES_PROMO = (self.BP << np.uint64(9)) & self.WHITE_PIECES & RANK_1 & ~FILE_A

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x"+makeField((i//8), i % 8)
                move['isHit'] = True
                moves.append(move)

        # move 1 forward
        PAWN_MOVES = (self.WP >> np.uint64(8)) & self.EMPTY & ~RANK_8
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(8)) & self.EMPTY & RANK_8

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(8)) & self.EMPTY & ~RANK_1
            PAWN_MOVES_PROMO = (self.BP << np.uint64(8)) & self.EMPTY & RANK_1

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['isHit'] = False
                moves.append(move)

        # move 2 forward
        PAWN_MOVES = (self.WP >> np.uint64(16)) & self.EMPTY & (self.EMPTY >> np.uint64(8)) & RANK_4
    
        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(16)) & self.EMPTY & (self.EMPTY << np.uint64(8)) & RANK_5

        for i in range(64):
            move = {}
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*2), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['isHit'] = False
                moves.append(move)

        if self.enPassant != '-':
            RANK = FileMasks8[self.enPassant[0]]

            # en passant right
            PAWN_MOVES = (self.WP << ONE) & self.BP & RANK_5 & ~FILE_A & RANK
            
            if not self.isWhiteTurn:
                PAWN_MOVES = (self.BP >> ONE) & self.WP & RANK_4 & ~FILE_H & RANK
            
            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8-(color*1))+'x'+self.enPassant
                    move['isHit'] = True
                    move['enPassant'] = True
                    moves.append(move)

            # en passant left
            PAWN_MOVES = (self.WP >> ONE) & self.BP & RANK_5 & ~FILE_H & RANK

            if not self.isWhiteTurn:
                PAWN_MOVES = (self.BP << ONE) & self.WP & RANK_4 & ~FILE_A & RANK

            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8+(color*1))+'x'+self.enPassant
                    move['isHit'] = True
                    move['enPassant'] = True
                    moves.append(move)

        return moves

    def HAndVMoves(self, s):
        binaryS = ONE << np.uint64(s)
        possibilitiesHorizontal = (self.OCCUPIED - TWO * binaryS) ^ reverse(reverse(self.OCCUPIED) - TWO * reverse(binaryS))
        possibilitiesVertical = ((self.OCCUPIED & FileMasks82[s % 8]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & FileMasks82[s % 8]) - (TWO * reverse(binaryS)))
        return (possibilitiesHorizontal & RankMasks8[(s // 8)]) | (possibilitiesVertical & FileMasks82[s % 8])
    
    def DAndAntiDMoves(self, s:int):
        binaryS =ONE << np.uint64(s)
        possibilitiesDiagonal = ((self.OCCUPIED & DiagonalMasks8[(s // 8) + (s % 8)]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & DiagonalMasks8[(s // 8) + (s % 8)]) - (TWO * reverse(binaryS)))
        possibilitiesAntiDiagonal = ((self.OCCUPIED & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (TWO * reverse(binaryS)))
        return (possibilitiesDiagonal & DiagonalMasks8[(s // 8) + (s % 8)]) | (possibilitiesAntiDiagonal & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)])
    
    def getMovesWB(self):
        moves = []
        WB = self.WB
        i = WB&~(WB - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLocation) & self.NOT_WHITE_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "B"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                moves.append(move)
                possibility&=~j
                j = possibility & ~(possibility - ONE)
            WB &= ~i
            i = WB&~(WB - ONE)
        return moves
    
    def getMovesWR(self):
        moves = []
        WR = self.WR
        i = WR&~(WR - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = self.HAndVMoves(iLocation) & self.NOT_WHITE_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "R"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                moves.append(move)
                possibility&=~j
                j = possibility & ~(possibility - ONE)
            WR &= ~i
            i = WR&~(WR - ONE)
        return moves
    
    def getMovesWQ(self):
        moves = []
        WQ = self.WQ
        i = WQ&~(WQ - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = (self.DAndAntiDMoves(iLocation) | self.HAndVMoves(iLocation) )& self.NOT_WHITE_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "Q"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                moves.append(move)
                possibility&=~j
                j = possibility & ~(possibility - ONE)
            WQ &= ~i
            i = WQ&~(WQ - ONE)
        return moves
    
    def getMovesWN(self):    
        moves = []
        WN = self.WN
        i = WN &~(WN - ONE)
        while i != 0:
            iLoc = trailingZeros(i) #loc of N
            if iLoc >  18:
                possibility = KNIGHT_SPAN << np.uint64(iLoc-18)
            else:
                possibility = KNIGHT_SPAN >> np.uint64(18 - iLoc)
            if iLoc%8 < 4:
                possibility &= ~FILE_GH & self.NOT_WHITE_PIECES
            else:
                possibility &= ~FILE_AB & self.NOT_WHITE_PIECES
            j = possibility &~(possibility-ONE)
            while j != 0:
                index = trailingZeros(j) 
                move = {}
                move['toString'] = "N"+makeField((iLoc//8),iLoc%8)+'-'+makeField((index//8),index%8)
                moves.append(move)
                possibility&=~j
                j=possibility&~(possibility- ONE)
            WN &=~i
            i = WN &~(WN - ONE)
        return moves
    
    def getMovesWK(self):
        moves = []
        WK = self.WK
        iLoc = trailingZeros(WK)
        if iLoc >  9:
            possibility = KING_SPAN << np.uint64(iLoc-9)
        else:
            possibility = KING_SPAN >> np.uint64(9 - iLoc)
        if iLoc%8 < 4:
            possibility &= ~FILE_GH & self.NOT_WHITE_PIECES
        else:
            possibility &= ~FILE_AB & self.NOT_WHITE_PIECES
        j = possibility &~(possibility-ONE)
        while j != 0:
            index = trailingZeros(j) 
            move = {}
            move['toString'] = "K"+makeField((iLoc//8),iLoc%8)+'-'+makeField((index//8),index%8)
            moves.append(move)
            possibility&=~j
            j=possibility&~(possibility- ONE)
        return moves
    
    def unsafeForBlack(self):
        WP = self.WP
        WN = self.WN
        QB = self.WQ|self.WR
        QR = self.WQ|self.WR
        WK = self.WK

        #pawn
        unsafe = (WP>>np.uint64(7)) & ~FILE_A   #actually >>>
        unsafe |= (WP>>np.uint64(9)) & ~FILE_H
        
        #knight
        i = WP &~(WP - ONE)
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
            WN &=~i
            i = WN & ~(WN-ONE)
            
        #(anti)diagonal sliding pieces (bishop & queen)
        i = QB &~(QB-ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLoc)
            unsafe |= possibility
            QB&=~i
            i=QB&~(QB-ONE)
            
        #staight sliding pieces (rook & queen)
        i = QR &~(QR-ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.HAndVMoves(iLoc)
            unsafe |= possibility
            QR&=~i
            i=QR&~(QR-ONE)
        
        #king
        iLoc = trailingZeros(WK)
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
  
# //////////////////
#
#       Tests
#
# ///////////////////
    
b = Board('rnbqkbnr/p1p1p1pp/1p1p1p2/8/8/1PPQ2B1/1PP1PPPP/RNB1K1NR w KQkq - 0 1')
print(b.getMoves())
