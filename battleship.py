import pygame
from pygame.locals import *
from square import *
from ship import *
from board import *
pygame.init()

boardwidth = 10
boardheight = 10
screenwidth = 800
screenheight = 600
board = Board(boardwidth,boardheight,screenwidth,screenheight)
hoverloc = (-1,-1)
hovercolour = (255,0,0)
clickcolour = (0,255,0)
boardcolour = (0,0,255)
clicked = False

ships = [5,4,3,3,2] #ships to place
curship = 0 #index of ship
orientation = 0 #0 - right, 1 - down, 2 - left, 3 - up
field = [] #highlighted ship area
prevfield = [] #previous highlighted ship area

screen = pygame.display.set_mode((screenwidth,screenheight))
gameOn = True

def isfieldonboard(field):
    for ind in field:
        if ind < 0 or ind > boardwidth*boardheight:
            field.remove(ind)
    return field

while gameOn:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                gameOn = False
            if event.key == K_UP:
                curship = (curship+1)%len(ships)
            if event.key == K_DOWN:
                curship = (curship-1)%len(ships)
            if event.key == K_RIGHT:
                orientation = (orientation+1)%4
            if event.key == K_LEFT:
                orientation = (orientation-1)%4

        elif event.type == MOUSEMOTION:
            if board.isonboard(event.pos):
                hoverloc = board.getsquare(event.pos)
    
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1: #left click
                clicked = True
            elif event.button == 3: #right click
                orientation = (orientation+1)%4

        elif event.type == QUIT:
            gameOn = False

    board.resetcolour(prevfield)
    prevfield = field
    field = board.makefield(ships[curship],hoverloc,orientation)
    if clicked:
        if board.placeship(field):
            ships.remove(len(field))
            if not ships: #if all ships placed
                ships.append(1)
            curship = 0
    else:
        board.hovership(field)
    clicked = False

    board.update(screen)
    pygame.display.flip()







