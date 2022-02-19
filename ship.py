class Ship():
    def __init__(self,shipid,field,topleft,im):
        self.shipid = shipid
        self.size = len(field)
        self.field = field
        self.sunk = False
        self.topleft = topleft 
        self.hitlocs = []
        self.im = im

    def hit(self,loc):
        self.hitlocs.append(loc)
        if len(self.hitlocs) == self.size:
            self.sunk = True

    def render(self,screen):
        if self.sunk:
            shiprect = self.im.get_rect(topleft = self.topleft)
            screen.blit(self.im,shiprect)
