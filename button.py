import pygame
from pygame.locals import *

class Button():
    def __init__(self,
            buttonid,
            text,
            font,
            left,
            top,
            width,
            height,
            fontcolour = (0,0,0),
            hovercolour = (180,180,200),
            buttoncolour = (150,150,170)):
        self.buttonid = buttonid
        self.text = text
        self.font = font
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.fontcolour = fontcolour
        self.hovercolour = hovercolour
        self.buttoncolour = buttoncolour
        self.button = pygame.Rect(left,top,width,height)

    def ison(self,pos):
        return self.button.collidepoint(pos)

    def render(self,screen,pos):
        if self.ison(pos):
            text = self.font.render(self.text,True,self.fontcolour,self.hovercolour)
        else:
            text = self.font.render(self.text,True,self.fontcolour,self.buttoncolour)
            
        screen.blit(text,self.button)

