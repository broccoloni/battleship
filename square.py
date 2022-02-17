
import pygame
from pygame.locals import *

class Square(pygame.sprite.Sprite):
    def __init__(self,width,height,colour = (0,200,255),pos = (0,0)):
        super(Square, self).__init__()
        self.width = width
        self.height = height
        self.colour = colour
        self.pos = pos
        self.surf = pygame.Surface((width,height))
        self.surf.fill(self.colour)
        self.rect = self.surf.get_rect()

    def set_colour(self,newcolour):
        self.surf.fill(newcolour)

    def set_colour_hard(self,newcolour):
        self.surf.fill(newcolour)
        self.colour = newcolour

    def reset_colour(self):
        self.surf.fill(self.colour)

    def setpos(self,x,y):
        self.pos = (x,y)





