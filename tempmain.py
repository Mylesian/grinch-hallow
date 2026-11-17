import pygame
# import pygut
import math
import random
import time
import sys
import pather as mg

from const import(
    screen_constants as sc,
    colors as c
)

pygame.init()
screen = pygame.display.set_mode((sc.WIDTH, sc.HEIGHT))
pygame.display.set_caption("Grinch's Hallows")
clock = pygame.time.Clock()

running = True    

while running:
    screen.fill(c.COLOR_BG)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    for i in range(sc.TILES):
        for j in range(sc.TILES):
            tile = pygame.Rect(j * sc.CELL_SIZE, i * sc.CELL_SIZE, sc.CELL_SIZE, sc.CELL_SIZE)
            pygame.draw.rect(screen, c.COLOR_WALL, tile, width=1)

    
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
