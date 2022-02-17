import numpy as np
from square import *
from ship import *
from pygame import *

class Board():
    def __init__(self,
            boardwidth,
            boardheight,
            screenwidth,
            screenheight,
            separation = 3,
            squarewidth = 25,
            squareheight = 25,
            numships = 5,
            shipcolour = (100,100,100),
            hovercolour = (175,175,0),
            seacolour = (0,0,255),
            hitcolour = (0,255,0),
            misscolour = (255,0,0),
            sunkcolour = (240,240,240),
            textcolour = (255,255,255)):

        #from inputs
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.separation = separation
        self.squarewidth = squarewidth
        self.squareheight = squareheight
        self.screenwidth = screenwidth
        self.screenheight = screenheight
        self.numships = numships
        self.shipcolour = shipcolour
        self.hovercolour = hovercolour
        self.seacolour = seacolour
        self.hitcolour = hitcolour
        self.misscolour = misscolour
        self.sunkcolour = sunkcolour
        self.textcolour = textcolour

        #internal variables
        self.board = np.zeros((boardheight,boardwidth),dtype = np.int8)
        self.ships = []
        self.setupdone = False
        self.shipsleft = self.numships
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
        for loc in field:
            if not self.isloconboard(loc):
                return False
        return True

    def isfieldonship(self,field):
        for loc in field:
            if self.isloconboard(loc):
                if self.boardval(loc) > 0:
                    return True
        return False

    def isloconboard(self,loc):
        y,x = loc
        if y>=0 and y<self.boardheight and x>=0 and x < self.boardwidth:
            return True
        return False

    def boardval(self,loc):
        y,x = loc
        return self.board[y,x]

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
            elif orientation == 1:
                field.append((y+i,x))
            elif orientation == 2:
                field.append((y,x-i))
            elif orientation == 3:
                field.append((y-i,x))
        return field

    def placeship(self,field):
        if self.isfieldonboard(field) and not self.isfieldonship(field) and not self.setupdone:
            self.ships.append(Ship(field))
            self.setcolourhard(field,self.shipcolour)
            for (y,x) in field:
                self.board[y,x] = len(self.ships)
            
            if len(self.ships) == self.numships:
                self.setupdone = True
                for row in self.squares:
                    for square in row:
                        square.set_colour_hard(self.seacolour)
            return True
        else:
            self.cropfield(field)
            self.setcolour(field,self.hovercolour)
            return False

    def hovership(self,field):
        self.cropfield(field)
        self.setcolour(field,self.hovercolour)
        return

    def attack(self,loc):
        y,x = loc
        hit = int(self.boardval(loc))
        self.board[y,x] = -1
        if hit > 0:
            #print("Attacking location:",loc,"... HIT!")
            self.ships[hit-1].hit(loc)
            self.setcolourhard([loc],self.hitcolour)
            if self.ships[hit-1].sunk:
                #print("Ship ",hit-1, " sunk")
                self.shipsleft -= 1
                self.setcolourhard(self.ships[hit-1].field,self.sunkcolour)
            return self.shipsleft
        elif hit == 0:
            #print("Attacking location:",loc,"... miss :(")
            self.setcolourhard([loc],self.misscolour)
            return self.shipsleft
        else:
            return -1

    def render(self,screen,text,font):
        screen.fill((0,0,0))
        for x in range(self.boardwidth):
            for y in range(self.boardheight):
                screen.blit(self.squares[y][x].surf,self.squares[y][x].pos)
        text = font.render(text,True,self.textcolour,(0,0,0))
        textrect = text.get_rect()
        textrect.center = (self.screenwidth // 2, self.top // 2) 
        screen.blit(text,textrect)

    def reset(self):
        self.board = np.zeros((self.boardheight,self.boardwidth),dtype = np.int8)
        self.ships = []
        self.setupdone = False
        self.shipsleft = self.numships
        for row in self.squares:
            for square in row:
                square.set_colour_hard(self.seacolour)
