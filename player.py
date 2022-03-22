import numpy as np

class Player():
    def __init__(self,
            difficulty):
        self.difficulty = difficulty

    def getshipplacement(self,board,shiplen):
        #currently only supports random player
        orientation = np.random.randint(4)
        if orientation%2 == 0: #horizontal
            startx = np.random.randint(10-shiplen+1)
            starty = np.random.randint(10)
        else:
            startx = np.random.randint(10)
            starty = np.random.randint(10-shiplen+1)

        #to ensure field is completely on board
        if orientation == 2:
            startx = 10-startx
        if orientation == 3:
            startx = 10-starty

        field = board.makefield(shiplen,(startx,starty),orientation)
        return field, orientation

    def guess(self,guesses):
        xs,ys = np.where(guesses == 0)
        ind = np.random.randint(len(xs))
        return (xs[ind],ys[ind])
