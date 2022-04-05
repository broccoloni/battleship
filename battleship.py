import pygame
from pygame.locals import *
from square import *
from ship import *
from board import *
from button import *
from player import *
from copy import deepcopy
import time

pygame.init()

#params that stay constant
gameOn = True
numships = 5
ships = [5,4,3,3,2]
boardwidth = 10
boardheight = 10
screenwidth = 900
screenheight = 600
squarewidth = screenwidth//80*3
squareheight = squarewidth
separation = 3
screen = pygame.display.set_mode((screenwidth,screenheight))
bigfont = pygame.font.SysFont("Ubuntu",squarewidth)
smallfont = pygame.font.SysFont("Ubuntu",squarewidth//2)
pygame.display.set_caption("Battleship")

#images
waterim = pygame.image.load("images/water.jpg")
waterim = pygame.transform.scale(waterim,(squarewidth,squareheight))
hitim = pygame.image.load("images/hit.png")
hitim = pygame.transform.scale(hitim,(12*squarewidth,squareheight)) #12 because there's twelve side by side ims
missim = pygame.image.load("images/miss.png")
missim = pygame.transform.scale(missim,(4*squarewidth,squareheight))
squareims = [waterim,hitim,missim]
ship5im = pygame.image.load("images/ship5.png").convert_alpha()
ship4im = pygame.image.load("images/ship4.png").convert_alpha()
ship3im1 = pygame.image.load("images/ship3_1.png").convert_alpha()
ship3im2 = pygame.image.load("images/ship3_2.png").convert_alpha()
ship2 = pygame.image.load("images/ship2.png").convert_alpha()
shipims = [ship5im,ship4im,ship3im1,ship3im2,ship2]

#rescale ship images
for i,im in enumerate(shipims):
    size = ships[i]
    im = pygame.transform.scale(im,(squarewidth,size*squareheight+size-1*separation))
    shipims[i] = pygame.transform.rotate(im,90)

#need to be reset with new game
playerturn = 0 #0 - p1, 1 - p2
opponenttype = 0 #0 - AI, 1 - Human
opponentdifficulty = 2 #0 - random, 1 - matches user level, 2 - best play -> only applies for AI opponent
players = [Player(i,opponentdifficulty,
                    boardwidth,
                    boardheight) for i in range(2)]
hoverloc = (-1,-1)
mousepos = (0,0)
countdown = 5
timeleft = deepcopy(countdown)
clicked = False
shipids = [0,1,2,3,4]
curship = 0 #index of ship
orientation = 0 #0 - right, 1 - down, 2 - left, 3 - up
field = [] #highlighted ship area
prevfield = [] #previous highlighted ship area
gamestate = 0
winner = 0
p1board = Board(boardwidth,
        boardheight,
        screenwidth,
        screenheight,
        shipims,
        squareims = squareims,
        squarewidth=squarewidth,
        squareheight=squareheight,
        separation=separation,
        numships=numships)
p2board = Board(boardwidth,
        boardheight,
        screenwidth,
        screenheight,
        shipims,
        squareims = squareims,
        squarewidth=squarewidth,
        squareheight=squareheight,
        separation=separation,
        numships=numships)
boards = [p1board,p2board]
buttons = [] #each gamestate will store different buttons in here, which will get cleared when changing gamestates
imstoblit = []
curshiptoblit = None
transitiontime = None
clock = pygame.time.Clock()
displaytext = ""

def loadheatmap(playerturn):
    separation = 15
    heatmap = pygame.image.load(f"images/player{playerturn}heatmap.png")
    heatmap = pygame.transform.scale(heatmap,(boards[0].left - separation,boards[0].left-separation))
    return heatmap

#Game loop
while gameOn:
    #Start menu
    if gamestate == 0:
        #inputs
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    gameOn = False

            elif event.type == MOUSEMOTION:
                mousepos = event.pos

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left click
                    clicked = True

            elif event.type == QUIT:
                gameOn = False
    
        #start menu with buttons
        if len(buttons) == 0:
            menuwidth = screenwidth//2
            menuheight = screenheight//2
            spacing = 10 #actually half of the spacing based on implementation
            bwidth = menuwidth//2.5
            bheight = menuheight//5
            
            #menu backgound - id 0
            buttons.append(Button(len(buttons),
                           (screenwidth - menuwidth)//2,
                           (screenheight - menuheight)//2,
                           menuwidth,
                           menuheight,
                           rounded = False))
            buttons[-1].hovercolour = buttons[-1].buttoncolour

            #play button - id 1
            buttons.append(Button(len(buttons),
                           screenwidth//2-spacing-bwidth,
                           int(screenheight//2-(spacing+bheight)*1.5),
                           bwidth,
                           bheight,
                           text = "Play Battleship!",
                           font = smallfont))

            #quit button - id 2
            buttons.append(Button(len(buttons),
                           screenwidth//2+spacing,
                           int(screenheight//2-(spacing+bheight)*1.5),
                           bwidth,
                           bheight,
                           text = "Quit",
                           font = smallfont))

            #Opponent AI button - id 3
            buttons.append(Button(len(buttons),
                           screenwidth//2-spacing-bwidth,
                           int(screenheight//2-(spacing+bheight)*0.5),
                           bwidth,
                           bheight,
                           text = "AI Opponent",
                           font = smallfont))
            buttons[-1].clicked = True #default is to play an AI

            #Opponent Human button - id 4 
            buttons.append(Button(len(buttons),
                           screenwidth//2+spacing,
                           int(screenheight//2-(spacing+bheight)*0.5),
                           bwidth,
                           bheight,
                           text = "Human Opponent",
                           font = smallfont))
            
        #If AI player is selected and only 5 buttons, make AI difficulty buttons
        if buttons[3].clicked and len(buttons) < 6: 
            menuwidth = screenwidth//2
            menuheight = screenheight//3
            spacing = 10 #actually half of the spacing based on implementation
            bwidth = menuwidth//10
            bheight = menuheight//5

            #text that says "AI difficulty:" - id 5
            buttons.append(Button(len(buttons),
                           screenwidth//2-spacing-menuwidth//2.5,
                           int(screenheight//2-(spacing+bheight)*-1.5),
                           menuwidth//2.5,
                           bheight,
                           text = "AI difficulty:",
                           font = smallfont))
            buttons[-1].hovercolour = buttons[-1].buttoncolour
            buttons[-1].bordercolour = buttons[-1].buttoncolour
            buttons[-1].hoverbordercolour = buttons[-1].buttoncolour

            #difficulty 1 - id 6
            buttons.append(Button(len(buttons),
                           screenwidth//2+spacing,
                           int(screenheight//2-(spacing+bheight)*-1.5),
                           bwidth,
                           bheight,
                           text = "1",
                           font = smallfont))
            
            #difficulty 2 - id 7
            buttons.append(Button(len(buttons),
                           screenwidth//2+bwidth+3*spacing,
                           int(screenheight//2-(spacing+bheight)*-1.5),
                           bwidth,
                           bheight,
                           text = "2",
                           font = smallfont))
            buttons[-1].clicked = True #medium AI as default

            #difficulty 3 - id 8
            buttons.append(Button(len(buttons),
                           screenwidth//2+2*bwidth+5*spacing,
                           int(screenheight//2-(spacing+bheight)*-1.5),
                           bwidth,
                           bheight,
                           text = "3",
                           font = smallfont))
        if clicked:
            buttonid = -1
            for num,button in enumerate(buttons):
                if button.ison(mousepos):
                    buttonid = button.buttonid        
            
            #Start/Reset Game
            if buttonid == 1: 
                boards[0].reset()
                boards[1].reset()
                buttons = []
                playerturn = 0 
                hoverloc = (-1,-1)
                mousepos = (0,0)
                ships = [5,4,3,3,2]
                curship = 0 
                orientation = 0
                field = []
                prevfield = [] 
                buttons = []
                gamestate = 1
                board = boards[0]
                
            #Quit
            elif buttonid == 2:
                gameOn = False

            #AI Opponent
            elif buttonid == 3:
                opponenttype = 0
                buttons[3].clicked = True
                buttons[4].clicked = False
                #NEED TO GENERATE DIFFICULTY OPTIONS

            #Human Opponent
            elif buttonid == 4:
                opponenttype = 1
                buttons[3].clicked = False
                buttons[4].clicked = True
                
                #remove AI difficulty options
                del buttons[5:]

            #AI difficulty (buttonid 5 is just text)
            elif buttonid > 5:
                opponentdifficulty = buttonid-6
                for button in buttons[6:]:
                    button.clicked = False
                buttons[buttonid].clicked = True

        clicked = False

    #Game setup
    elif gamestate == 1: 
        #p1 sets up p2's board, p2 sets up p1's board
        board = boards[(playerturn+1)%2]
        displaytext = "Player "+str(playerturn+1)+" setup"

        #inputs
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    gameOn = False
                if event.key == K_UP:
                    board.buttons[shipids[curship]].clicked = False
                    curship = (curship-1)%len(shipids)
                    board.buttons[shipids[curship]].clicked = True
                if event.key == K_DOWN:
                    board.buttons[shipids[curship]].clicked = False
                    curship = (curship+1)%len(shipids)
                    board.buttons[shipids[curship]].clicked = True
                if event.key == K_RIGHT:
                    orientation = (orientation+1)%4
                    for i,im in enumerate(shipims):
                        shipims[i] = pygame.transform.rotate(im,90)
                if event.key == K_LEFT:
                    orientation = (orientation-1)%4
                    for i,im in enumerate(shipims):
                        shipims[i] = pygame.transform.rotate(im,-90)

            elif event.type == MOUSEMOTION:
                mousepos = event.pos
                if board.isonboard(event.pos):
                    hoverloc = board.getsquare(event.pos)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left click
                    clicked = True
                elif event.button == 3: #right click
                    orientation = (orientation+1)%4
                    for i,im in enumerate(shipims):
                        shipims[i] = pygame.transform.rotate(im,90)

            elif event.type == QUIT:
                gameOn = False

        #set hovering ship field
        board.resetcolour(prevfield)
        prevfield = field
        curships = [ships[shipid] for shipid in shipids]
        field = board.makefield(curships[curship],hoverloc,orientation)
        if board.isfieldonboard(field):
            shipim = shipims[shipids[curship]]
            shippos = board.topleftposoffield(field,orientation)
            curshiptoblit = (shipim,shippos)

        #when user clicks
        if clicked:
            if board.isonboard(mousepos):
                #place ship
                if board.placeship(shipids[curship],field,orientation):
                    shipid = shipids.pop(curship)
                    shipim = shipims[shipid]
                    shippos = board.topleftposoffield(field,orientation)
                    imstoblit.append((shipid,shipim,shippos))
                    curshiptoblit = None
                    
                    #if all ships placed go to setup transition
                    if not shipids:
                        gamestate = 2

                    #if there are some ships left
                    else:
                        curship = 0
                        board.buttons[shipids[curship]].clicked = True

            #if mouse is not on board
            else:
                board.hovership(field)
                for button in board.buttons:
                    #if mouse is on a ship button instead
                    if button.ison(mousepos):
                        shipid = button.buttonid
                        #switch current ship to that ship if it hasn't been placed yet
                        if shipid in shipids:
                            board.buttons[shipids[curship]].clicked = False
                            curship = shipids.index(shipid) 
                            button.clicked = True

        #if not clicked, hover
        else:
            board.hovership(field)

        clicked = False
 
    elif gamestate == 2: #player transition for setup state (ie. should only be used in gamestate 1)
        #inputs
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    gameOn = False

            elif event.type == MOUSEMOTION:
                mousepos = event.pos

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left click
                    clicked = True

            elif event.type == QUIT:
                gameOn = False
    
        if len(buttons) == 0:
            bottomofboard = board.top+board.gameheight
            spacing = 15 #half of actual separation
            bwidth = (board.left-3*spacing)//2
            bheight = int(1.5*squareheight)
            
            #confirm setup button
            buttons.append(Button(len(buttons),
                           spacing,
                           bottomofboard-bheight,
                           bwidth,
                           bheight,
                           text = "Confirm",
                           font = smallfont))

            #reset setup button
            buttons.append(Button(len(buttons),
                           2*spacing+bwidth,
                           bottomofboard-bheight,
                           bwidth,
                           bheight,
                           text = "Reset",
                           font = smallfont))
            
            #rate my setup button
            buttons.append(Button(len(buttons),
                           (board.left-bwidth*1.5)//2,
                           board.top,
                           int(bwidth*1.5),
                           bheight,
                           text = "Rate my setup!",
                           font = smallfont))

        if clicked:
            buttonid = -1
            for num,button in enumerate(buttons):
                if button.ison(mousepos):
                    buttonid = button.buttonid

            #confirm ship placement
            if buttonid == 0: 
                #AI opponent
                if opponenttype == 0 and playerturn == 0:
                    players[1].difficulty = opponentdifficulty 
                    
                    #set up board
                    board = boards[0]
                    shipids = [0,1,2,3,4]
                    while len(shipids)>0:
                        shiplen = ships[shipids[0]]
                        field,orientation = players[1].getshipplacement(board,shiplen)
                        if board.placeship(shipids[0],field,orientation):
                            shipids.pop(0)

                    #remove hovercolour change
                    for board in boards:
                        for button in board.buttons:
                            button.hovercolour = button.buttoncolour
                            button.hoverbordercolour = button.bordercolour
                    
                    #begin game
                    gamestate = 3

                elif playertype == 1:
                    playerturn = (playerturn+1)%2
                    #both have placed their ships, go to game mode
                    if playerturn == 0:
                        #remove hovercolour change
                        for board in boards:
                            for button in board.buttons:
                                button.hovercolour = button.buttoncolour
                                button.hoverbordercolour = button.bordercolour
                        
                        #begin game
                        gamestate = 3
                    
                    #go to setup state for other player
                    else:
                        gamestate = 1


            #reset ships (keep playerturn constant)
            elif buttonid == 1:
                gamestate = 1
                board.reset()

            #user defending score
            elif buttonid == 2:
                print("Not implemented yet!")
            
            #if confirm or reset clicked, reset for setup
            if buttonid == 0 or buttonid == 1:
                shipids = [0,1,2,3,4]
                ships = [5,4,3,3,2]
                imstoblit = []
                rotation = 0
                curship = 0
                hoverloc = (-1,-1)
                field = []
                if orientation == 1:
                    rotation = -90
                elif orientation == 2:
                    rotation = 180
                elif orientation == 3:
                    rotation = 90
                for i,im in enumerate(shipims):
                    shipims[i] = pygame.transform.rotate(im,rotation)
                orientation = 0

                #clear buttons
                buttons = []

        clicked = False

    elif gamestate == 3: #playing battleship
        board = boards[playerturn]
        displaytext = "Player "+str(playerturn+1)+" turn:"
    
        #inputs
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    gameOn = False

            elif event.type == MOUSEMOTION:
                mousepos = event.pos
                if board.isonboard(mousepos):
                    hoverloc = board.getsquare(mousepos)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left click
                    clicked = True

            elif event.type == QUIT:
                gameOn = False
        
        #buttons
        spacing = 15
        if len(buttons) == 0:
            bwidth = board.left//1.5
            bheight = int(1.5*squareheight)
            
            #options button - id 0
            buttons.append(Button(len(buttons),
                           spacing,
                           spacing,
                           bwidth,
                           bheight,
                           text = "Options",
                           font = smallfont))

            #hint button - id 1
            buttons.append(Button(len(buttons),
                           spacing,
                           screenheight-bheight-spacing,
                           bwidth,
                           bheight,
                           text = "Hint",
                           font = smallfont))
            
            bwidth = board.left-2*spacing
            #ship probability distribution - id 2
            buttons.append(Button(2,
                                  spacing,
                                  spacing+bheight,
                                  bwidth,
                                  bheight,
                                  text = "Ship Probability Distribution",
                                  font = smallfont,
                                  rounded = False,
                                  displayed = False))

            #user attacking score - id 3
            buttons.append(Button(3,
                                  spacing,
                                  spacing+2*bheight,
                                  bwidth,
                                  bheight,
                                  text = "Score Of Previous Guess",
                                  font = smallfont,
                                  rounded = False,
                                  displayed = False))
            
            #hint text - id 4
            buttons.append(Button(4,
                                  2*spacing + bwidth,
                                  screenheight-bheight-spacing,
                                  bwidth//3,
                                  bheight,
                                  font = smallfont,
                                  fontcolour = (255,255,255),
                                  hovercolour = (0,0,0),
                                  buttoncolour = (0,0,0),
                                  clickedcolour = (0,0,0),
                                  bordercolour = (0,0,0),
                                  hoverbordercolour = (0,0,0),
                                  clickedbordercolour = (0,0,0),
                                  displayed = False))

            #Requesting user feedback button - id 5
            buttons.append(Button(5,
                           spacing,
                           board.top+board.gameheight - 3*bheight,
                           bwidth,
                           bheight,
                           text = "Did you like this hint?",
                           font = smallfont,
                           displayed = False))
            buttons[-1].hovercolour = buttons[-1].buttoncolour

            #positive feedback - id 6
            buttons.append(Button(6,
                           spacing,
                           board.top+board.gameheight-2*bheight,
                           bwidth,
                           bheight,
                           buttoncolour = (150,220,170),
                           hovercolour = (180,220,200),
                           text = "Yes, show more!",
                           font = smallfont,
                           displayed = False))

            #negative feedback - id 7
            buttons.append(Button(7,
                           spacing,
                           board.top+board.gameheight-bheight,
                           bwidth,
                           bheight,
                           buttoncolour = (220,150,170),
                           hovercolour = (220,180,200),
                           text = "No, show less",
                           font = smallfont,
                           displayed = False))

            #Attacking score bar background - id 8
            buttons.append(Button(8,
                           spacing,
                           spacing + 3 * bheight,
                           bwidth,
                           bheight,
                           font = smallfont,
                           fontcolour = (255,255,255),
                           buttoncolour = (0,0,0),
                           hovercolour = (0,0,0),
                           clickedcolour = (0,0,0),
                           bordercolour = (255,255,255),
                           hoverbordercolour = (255,255,255),
                           clickedbordercolour = (255,255,255),
                           displayed = False))
            
            #Attacking score - id 9
            buttons.append(Button(9,
                           spacing,
                           spacing + 3 * bheight,
                           bwidth,
                           bheight,
                           font = smallfont,
                           fontcolour = (255,255,255),
                           bordercolour = (0,0,0),
                           hoverbordercolour = (0,0,0),
                           clickedbordercolour = (0,0,0),
                           displayed = False))
            

        board.resetcolour(prevfield)
        prevfield = [hoverloc]

        if clicked:
            buttonid = -1
            for num,button in enumerate(buttons):
                if button.ison(mousepos):
                    buttonid = button.buttonid
            
            print("Number of buttons:",len(buttons),buttonid)
            #Options button
            if buttonid == 0:
                #show options dropdown
                if not buttons[2].displayed:
                    buttons[2].displayed = True
                    buttons[3].displayed = True

                #remove options dropdown
                else:
                    buttons[2].displayed = False
                    buttons[3].displayed = False

            #Hint button
            elif buttonid == 1:     
                #if not displayed, display it
                if not buttons[4].displayed:
                    x,y = players[playerturn].guess()
                    letters = ['A','B','C','D','E','F','G','H','I','J']
                    hinttext = f"Try {letters[y]}{x+1}!"
                    buttons[4].text = hinttext
                    buttons[4].displayed = True
                    
                    #get user feedback
                    buttons[5].displayed = True
                    buttons[6].displayed = True
                    buttons[7].displayed = True

                #if displayed, stop showing it
                else:
                    buttons[4].displayed = False 
                    buttons[5].displayed = False
                    buttons[6].displayed = False
                    buttons[7].displayed = False
                #Get user feedback on hint 
                                
            #Probability distribution button
            elif buttonid == 2:
                #imstoblit in this gamestate is only used for displaying the heatmap
                #if it's not shown, show it
                if imstoblit == []:
                    #stop showing the attacking score
                    buttons[8].displayed = False
                    buttons[9].displayed = False

                    heatmap = loadheatmap(playerturn)
                    pos = (separation,(screenheight - board.left)//2)
                    imstoblit.append((2,heatmap,pos))
                
                #if it is shown, stop showing it
                else:
                    imstoblit = []

            #Attacking score button
            elif buttonid == 3:
                #if shown already, stop showing it
                if buttons[8].displayed:
                    buttons[8].displayed = False
                    buttons[9].displayed = False

                #if not shown, show the attacking score bar
                else:
                    #stop showing the heatmap
                    imstoblit = []

                    buttons[8].displayed = True
                    buttons[9].displayed = True
                    if len(players[playerturn].attacking_scores) > 0:
                        score = players[playerturn].attacking_scores[-1]
                        
                        #linearly interpolate button colour from red to green
                        r = int(255 * (1-score))
                        g = int(255 * score)
                        scorecolour = (r,g,0)
                        buttons[9].buttoncolour = scorecolour
                        buttons[9].hovercolour = scorecolour
                        buttons[9].clickedcolour = scorecolour
                        buttons[9].bordercolour = scorecolour
                        buttons[9].hoverbordercolour = scorecolour
                        buttons[9].clickedbordercolour = scorecolour
                    
                        #update text with current score
                        buttons[9].text = f"{int(score*100)}%"
                    
                        #update progress bar length
                        w = int(buttons[8].width * score)
                        buttons[9].width = w

                    else:
                        colour = (0,0,0)
                        buttons[9].buttoncolour = colour
                        buttons[9].hovercolour = colour
                        buttons[9].clickedcolour = colour
                        buttons[9].bordercolour = colour
                        buttons[9].hoverbordercolour = colour
                        buttons[9].clickedbordercolour = colour
                        buttons[9].text = "No Previous Attacks"

            #id 4 is hint text

            #id 5 is request for feedback

            #positive hint feedback
            elif buttonid == 6:
                buttons[5].displayed = False
                buttons[6].displayed = False
                buttons[7].displayed = False
                print("Positive hint feedback!")

            #negative hint feedback
            elif buttonid == 7:
                buttons[5].displayed = False
                buttons[6].displayed = False
                buttons[7].displayed = False
                print("Negative hint feedback")

            if board.isonboard(mousepos):
                retval, shipfield, shipsleft = board.attack(hoverloc)
                #it's a hit
                if retval > 0:
                    players[playerturn].updaterevealed(retval,shipfield)
                    displaytext+= " HIT!"
                    if shipsleft > 0:
                        gamestate = 4
                    
                    #game over
                    elif shipsleft == 0: 
                        displaytext = "Player "+str(playerturn+1)+" wins!" 
                        gamestate = 5
                
                #it's a miss
                elif retval == 0: 
                    players[playerturn].updaterevealed(retval,shipfield)
                    displaytext += " Miss :("
                    gamestate = 4
                
                #already attacked location
                elif retval == -1:
                    board.hovership([hoverloc])

        else:
            board.hovership([hoverloc])
    
        clicked = False
    
    elif gamestate == 4: #player transition during gameplay (ie, only from gamestate 3 and 5, since it switches back to that)
        #Inputs
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    gameOn = False
                elif event.type == QUIT:
                    gameOn = False
                elif event.type == MOUSEMOTION:
                    mousepos = event.pos

        #stop showing the heatmap
        imstoblit = []
        #stop showing any buttons that aren't options and hint
        for button in buttons:
            if button.buttonid > 1:
                button.displayed = False

        if transitiontime is None:
            transitiontime = pygame.time.get_ticks()

        else:
            delay = 1000
            timedif = pygame.time.get_ticks() - transitiontime
            if timedif >= delay:
                transitiontime = None

                #AI opponent
                if opponenttype == 0 and playerturn == 0:
                    gamestate = 5

                #Human opponent or after AI opponent has played
                else:
                    gamestate = 3

                #update player turn
                playerturn = (playerturn+1)%2

    elif gamestate == 5: #AI players turn
        displaytext = "AIs turn"
        board = boards[playerturn]
        guess = players[playerturn].guess()
        retval, shipfield, shipsleft = board.attack(guess)
        players[playerturn].updaterevealed(retval,shipfield)
        
        if shipsleft == 0:
            gamestate = 6
        else:
            gamestate = 4

    elif gamestate == 6: #player transition after game is won/lost
        #Inputs
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                        gameOn = False
                elif event.type == QUIT:
                    gameOn = False
                elif event.type == MOUSEMOTION:
                    mousepos = event.pos
        
        displaytext = "Player",playerturn,"won!"
        if transitiontime is None:
            transitiontime = pygame.time.get_ticks()

        else:
            delay = 1000
            timedif = pygame.time.get_ticks() - transitiontime
            if timedif >= delay:
                gamestate = 0
        
    if gamestate != 0:
        board.render(screen,displaytext,bigfont,mousepos)
    for button in buttons:
        button.render(screen,mousepos)
    for imid,im,pos in imstoblit:
        screen.blit(im,pos)
    if curshiptoblit is not None:
        im,pos = curshiptoblit
        screen.blit(im,pos)
    pygame.display.flip()
    clock.tick(60)

















