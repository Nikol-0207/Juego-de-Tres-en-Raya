import pygame, sys
from pygame.locals import *


PANTALLA = pygame.display.set_mode((800,700))
pygame.display.set_caption('Juego de tres en raya')

while True: 
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()


