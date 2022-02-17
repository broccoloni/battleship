import numpy as np
from square import *
from ship import *

class Board():
    def __init__(self,
            boardwidth,
            boardheight,
            screenwidth,
            screenheight,
            separation = 3,
            squarewidth = 25,
            squareheight = 25,
            shipcolour = (0,255,0),
            hovercolour = (255,0,0),
            seacolour = (0,0,255)):

        #from inputs
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.board = np.zeros((boardheight,boardwidth))
        self.separation = separation
        self.squarewidth = squarewidth
        self.squareheight = squareheight
        self.screenwidth = screenwidth
        self.screenheight = screenheight
        self.shipcolour = shipcolour
        self.hovercolour = hovercolour
        self.seacolour = seacolour

        #internal variables
        self.ships = []
        self.allshipsplaced = False
        self.gamewidth = boardwidth * squarewidth + (boardwidth-1)*separation
        self.gameheight = boardheight * squareheight + (boardheight-1)*separation
        self.left = (screenwidth - self.gamewidth)//2
        self.top = (screenheight - self.gameheight)//2
        self.squares = [[Square(squarewidth,squareheight,seacolour) for i in range(boardwidth)] for j in range(boardheight)]
        for x in range(boardwidth):
            for y in range(boardheight):
                posx = self.left + x * (squarewidth+separation)
                posy = self.top + y * (squareheight+separation)
                self.squares[y][x].setpos(posx,posy)

    def isonboard(self,pos):
        posx,posy = pos
        if posx < self.left:
            return False
        elif posx > self.left + self.gamewidth:
            return False
        elif posy < self.top:
            return False
        elif posy > self.top + self.gameheight:
            return False
        return True
    
    def isfieldonboard(self,field):
        for (y,x) in field:
            if y < 0 or y > self.boardheight or x < 0 or x > self.boardwidth:
                return False
        return True

    def isfieldonship(self,field):
        for (y,x) in field:
            if y > 0 and y < self.boardheight and x > 0 and x < self.boardwidth:
                if self.board[y,x] == 1:
                    return True
        return False

    def cropfield(self,field):
        toremove = []
        for (y,x) in field:
            if y < 0 or y >= self.boardheight or x < 0 or x >= self.boardwidth:
                toremove.append((y,x))
        for i in toremove:
            field.remove(i)
        return
            
    def getsquare(self,pos):
        posx,posy = pos
        posx -= self.left
        posy -= self.top
        tilex = posx // (self.squarewidth + self.separation)
        tiley = posy // (self.squareheight + self.separation)
        return (tiley,tilex)

    def resetcolour(self,field):
        for (y,x) in field:
            self.squares[y][x].reset_colour()
        return

    def setcolour(self,field,colour):
        for (y,x) in field:
            self.squares[y][x].set_colour(colour)
        return

    def setcolourhard(self,field,colour):
        for (y,x) in field:
            self.squares[y][x].set_colour_hard(colour)
        return

    def makefield(self,size,hoverloc,orientation):
        field = [hoverloc]
        y,x = hoverloc
        for i in range(1,size):
            if orientation == 0:
                field.append((y,x+i))
            if orientation == 1:
                field.append((y+i,x))
            if orientation == 2:
                field.append((y,x-i))
            if orientation == 3:
                field.append((y-i,x))
        return field

    def placeship(self,field):
        if self.isfieldonboard(field) and not self.isfieldonship(field) and not self.allshipsplaced:
            self.ships.append(Ship(field))
            self.setcolourhard(field,self.shipcolour)
            for (y,x) in field:
                self.board[y,x] = 1
            if len(self.ships) == 5:
                self.allshipsplaced = True
            return True
        else:
            self.cropfield(field)
            self.setcolour(field,self.hovercolour)
            return False

    def hovership(self,field):
        self.cropfield(field)
        self.setcolour(field,self.hovercolour)
        return
            
    def update(self,screen):
        for x in range(self.boardwidth):
            for y in range(self.boardheight):
                screen.blit(self.squares[y][x].surf,self.squares[y][x].pos)


