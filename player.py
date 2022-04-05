import numpy as np
import matplotlib.pyplot as plt

class Player():
    def __init__(self,
            playerid,
            difficulty,
            boardwidth,
            boardheight,
            samplesize = 10000):
        
        #from inputs
        self.playerid = playerid
        self.difficulty = difficulty
        self.difficulty = 1
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.samplesize = samplesize
        self.posterior = None

        #internal variable
        shipsizes = np.array([5,4,3,3,2])
        self.shipconfigs = [self.get_all_ship_configs(shipsize) for shipsize in shipsizes]
        self.ships = self.sample_ships(self.shipconfigs)[0]
        self.allshipconfigs = [oneshipsampling(ship_configs) for ship_configs in self.shipconfigs]
        self.revealedships = np.ma.masked_all((len(self.shipconfigs),)+self.shipconfigs[0][0].shape)
        self.turn_revealed = []
        self.updateposterior()
        self.generateheatmap()
        self.attacking_scores = []

    def getshipplacement(self,board,shiplen):
        #Random player
        if self.difficulty >= 0:
            orientation = np.random.randint(4)
            if orientation%2 == 0: #horizontal
                startx = np.random.randint(self.boardwidth-shiplen+1)
                starty = np.random.randint(self.boardheight)
            else:
                startx = np.random.randint(self.boardwidth)
                starty = np.random.randint(self.boardheight-shiplen+1)

            #to ensure field is completely on board if in left or up orientation
            if orientation == 2:
                startx = self.boardwidth-startx
            if orientation == 3:
                startx = self.boardheight-starty

            field = board.makefield(shiplen,(startx,starty),orientation)
            return field, orientation

        #Medium AI player
        if self.difficulty == 1:
            pass

    def guess(self):
        print("in guess")
        print("revealed\n",self._revealed())
        #Random player
        if self.difficulty == 0:
            xs,ys = np.where(self._revealed())
            ind = np.random.randint(len(xs))
            return (xs[ind],ys[ind])

        #Medium AI player
        if self.difficulty > 0:
            print("posterior\n", self.posterior)
            return self.argmax_2d(self.posterior)

    def updateposterior(self):
        self.posterior = np.ma.masked_array(
                         self.sample_posterior(), 
                         mask = ~self._revealed().mask)

    def generateheatmap(self):
        params = {'ytick.color':'w',
                  'xtick.color':'w',
                  'axes.labelcolor':'w',
                  'axes.edgecolor':'w'}

        plt.rcParams.update(params)

        fig,ax = plt.subplots(figsize = (4,4))
        fig.patch.set_facecolor('black')
        im = ax.imshow(self.posterior,cmap = 'hot',interpolation = 'nearest')
        ax.set_xticks(range(10))
        ax.set_yticks(range(10))
        ax.set_xticklabels(range(1,11))
        ax.set_yticklabels(['A','B','C','D','E','F','G','H','I','J'])
        cbar = fig.colorbar(im,orientation = "horizontal",ticks = [self.posterior.min(),self.posterior.max()])
        cbar.ax.set_xticklabels(['low','high'])
        plt.savefig(f'./images/player{self.playerid}heatmap.png',bbox_inches = 'tight',dpi = 100)

    def argmax_2d(self,dist):
        maxx = dist.max(axis = 1).argmax()
        maxy = dist[maxx].argmax()
        return (maxx,maxy)

    def sample_posterior(self):
        print("in sample posterior")
        all_compatible_configs = [
                shipconfig.compatible_ships(seen_ships)
                for (shipconfig, seen_ships) in zip(self.allshipconfigs, self.revealedships)]
        
        samples = self.sample_n_ships(all_compatible_configs,self._revealed())
        return samples.sum(axis = 1).mean(axis = 0)

    def sample_n_ships(self,possible_ships,revealed):
        print("sampling n configs")
        samples = []
        while len(samples) == 0:
            samples = self.get_samples(possible_ships,revealed)
        return samples

    def get_samples(self, possible_ships,revealed):
        print("getting samples")
        randnumgen = np.random.default_rng()
        samples = np.stack([randnumgen.choice(ships,
                                             size = self.samplesize,
                                             shuffle = False)
                            for ships in possible_ships],axis = 1)
        valid_samples = samples[self.validate_samples(samples)]
        
        if revealed.mask.all():
            return valid_samples
        else:
            compatible = (valid_samples.sum(axis = 1) == revealed).all(axis = (-2,-1))
            return valid_samples[compatible]

    def generate_compatible_ships(self,possible_ships,revealed):
        while True:
            yield from self.sample_n_ships(possible_ships,revealed)

    def sample_ships(self,possible_ships):
        empty = np.ma.masked_all_like(self.shipconfigs[0][0])
        generated_compatible_ships = self.generate_compatible_ships(possible_ships,empty)
        return np.array([x for _,x in zip(range(self.samplesize),generated_compatible_ships)])

    def validate_samples(self,samples, ship_axis = 1, board_axis = (-2,-1)):
        print("validating samples")
        return (samples.sum(axis = ship_axis).max(axis = board_axis) == 1)

    def get_all_ship_configs(self, shipsize):
        print("getting ship configs")
        configs1d = self.get_all_ship_configs_1d(shipsize)
        rows, _ = configs1d.shape
        y = np.arange(self.boardheight)
        boards = np.zeros((rows,self.boardwidth,self.boardwidth,self.boardheight))
        boards[:,y,y,:] = configs1d[:,np.newaxis]
        board_configs = boards.reshape((-1, self.boardwidth,self.boardheight))
        return np.concatenate((board_configs,board_configs.transpose(0,2,1)))

    def get_all_ship_configs_1d(self, shipsize):
        print("getting 1d ship configs")
        x,y = np.indices((self.boardwidth,self.boardwidth))[:,:-shipsize+1]
        return 1 * (x <= y) & (y < x + shipsize)

    def updaterevealed(self,retval,field):
        print("updating revealed")
        x,y = field
        prev_sunk = self._sunk()
        next_ships = self._revealed_ships().copy()
        next_ships[:,x,y] = self.ships[:,x,y]
        self.turn_revealed.append(next_ships)

        curr_sunk = self._sunk()

        if (curr_sunk == prev_sunk).all():
            sunk = None
        else:
            sunk = (curr_sunk & ~prev_sunk).argmax() 
        if self.ships.sum(axis = 0)[x,y] == 0 or sunk is not None:
            self.revealedships[:,x,y] = 0
            if sunk is not None:
                self.revealedships[sunk,x,y] = 1

        #calculate guess score

        guess_prob = self.posterior[x,y]
        attacking_score = np.searchsorted(np.sort(self.posterior.flatten()),
                                          guess_prob)/(self.posterior.count()-1)
        self.attacking_scores.append(attacking_score)

        self.updateposterior()
        self.generateheatmap()

    #Some dynamic properties
    def _is_solved(self):
        return self._revealed.sum() == (self.ships.sum(axis = 0)).sum()

    def _revealed(self):
        return self._revealed_ships().sum(axis = 0)

    def _sunk(self):
        ship_sizes = self.ships.sum(axis = (1,2))
        revealed_ship_sizes = (self._revealed_ships().sum(axis = (1,2)).filled(0))
        return ship_sizes == revealed_ship_sizes
    
    def _revealed_ships(self):
        if self._turns() > 0:
            return self.turn_revealed[-1]
        else:
            return np.ma.masked_all_like(self.ships)

    def _turns(self):
        return len(self.turn_revealed)

    def _turn_revealed(self): #his is turn_revealed, and other one is _turn_revealed
        return [np.ma.masked_all_like(self._board())]+[revealed.sum(axis = 0) for revealed in self.turn_revealed]

class oneshipsampling():
    def __init__(self, ship_configs):
        self.ship_configs = ship_configs

    def compatible_ships(self, revealed):
        print("finding compatible ships in one ship sampling")
        if revealed.mask.all():
            return self.ship_configs
        else:
            compatible_configs = self.get_compatible_configs(self.ship_configs,revealed)
            return self.ship_configs[compatible_configs]

    def get_compatible_configs(self,ship_configs,revealed):
        return (ship_configs == revealed).all(axis = (-2,-1))
