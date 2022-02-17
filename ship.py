class Ship():
    def __init__(self,field):
        self.size = len(field)
        self.field = field
        self.sunk = False

    def setfield(self,field):
        self.field = field


