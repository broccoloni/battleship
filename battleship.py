import pygame
from pygame.locals import *
from square import *
from ship import *
from board import *
from button import *
from copy import deepcopy
pygame.init()

#params that stay constant
boardwidth = 10
boardheight = 10
screenwidth = 800
screenheight = 600
screen = pygame.display.set_mode((screenwidth,screenheight))
pygame.display.set_caption("Battleship")
font = pygame.font.SysFont("Ubuntu",30)
gameOn = True

#need to be reset with new game
playerturn = 0 #0 - p1, 1 - p2
hoverloc = (-1,-1)
pos = (0,0)
clicked = False
numships = 5
defaultships = [5,4,3,3,2]
ships = deepcopy(defaultships) #ships to place
curship = 0 #index of ship
orientation = 0 #0 - right, 1 - down, 2 - left, 3 - up
field = [] #highlighted ship area
prevfield = [] #previous highlighted ship area
setupdone = False
gameover = -1
p1board = Board(boardwidth,boardheight,screenwidth,screenheight,numships = numships)
p2board = Board(boardwidth,boardheight,screenwidth,screenheight,numships = numships)
boards = [p1board,p2board]
buttons = []

#Game loop
while gameOn:
    for event in pygame.event.get():
        #Game setup
        if not setupdone: 
            #p1 sets up p2's board, p2 sets up p1's board
            board = boards[(playerturn+1)%2]
            displaytext = "Player "+str(playerturn+1)+" setup"
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
                    curship = 0
                    if not ships: #if all ships placed
                        if playerturn == 0:
                            ships = deepcopy(defaultships) #player2 places ships now
                        else:
                            setupdone = True
                        playerturn = (playerturn+1)%2
            else:
                board.hovership(field)
            clicked = False

        elif gameover != -1:
            displaytext = "Player "+str(gameover)+" wins!" 
            
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    gameOn = False

            elif event.type == MOUSEMOTION:
                pos = event.pos
                if board.isonboard(pos):
                    hoverloc = board.getsquare(pos)
    
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left click
                    clicked = True

            elif event.type == QUIT:
                gameOn = False
            
            if len(buttons) == 0:
                buttons.append(Button(0,"Play Again",font,screenwidth//2-90,screenheight//2-30,180,60))
            
            if clicked:
                clickedbutton = -1
                for button in buttons:
                    if button.ison(pos):
                        clickedbutton = button.buttonid

                if clickedbutton == 0:
                    #quit
                    #gameOn = False
                
                    #reset game
                    boards[0].reset()
                    boards[1].reset()
                    buttons = []
                    playerturn = 0 
                    hoverloc = (-1,-1)
                    pos = (0,0)
                    ships = deepcopy(defaultships)
                    curship = 0 
                    orientation = 0
                    field = []
                    prevfield = [] 
                    setupdone = False
                    gameover = -1
                    
                    buttons = []

            clicked = False

        else: #if setup is done and game isn't over, we can begin the game
            board = boards[playerturn]
            displaytext = "Player "+str(playerturn+1)+" turn"
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    gameOn = False

            elif event.type == MOUSEMOTION:
                pos = event.pos
                if board.isonboard(pos):
                    hoverloc = board.getsquare(pos)
    
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left click
                    clicked = True

            elif event.type == QUIT:
                gameOn = False
           
            board.resetcolour(prevfield)
            prevfield = [hoverloc]

            if clicked:
                if board.isfieldonboard([hoverloc]):
                    shipsleft = board.attack(hoverloc)
                    #game over
                    if shipsleft == 0:
                        gameover = playerturn+1

                    elif shipsleft == -1:#if they attack where a sunk ship is - do nothing
                        board.hovership([hoverloc])
                    else:
                        playerturn = (playerturn+1)%2

            else:
                board.hovership([hoverloc])
            
            clicked = False
            
    board.render(screen,displaytext,font)
    for button in buttons:
        button.render(screen,pos)
    pygame.display.flip()

















