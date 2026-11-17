import pygame
import math
import random

from const import(
    screen_constants as sc,
    colors as c,
    maze_consts as mz,
    img_consts as Tile
)

class MapSkinner:

    def __init__(self):
        self.platformExtendProbability = 1
        self.powerUpProbability = 0.2
        self.coinProbability = 0.2
        self.enemyProbability = 0.3

    def skinMap(self, map, path, controller):
        columns, rows = map.getDimensions()

        columnsSinceEnemy = [0] * rows
        solids = []
        clearBelow = []

        powerupHeight = round(controller.jumpHeight + controller.height)

        for x in range(columns):
            foundContent = False
            tilesFromFloor = float('-inf')

            for y in range(rows - 1, -1, -1):
                tilesFromFloor += 1
                columnsSinceEnemy[y] += 1
                tile = map.getTileAt(x, y)

                if tile == mz.SOLID_RESERVATION:
                    bottom = y if foundContent else rows - 1
                    map.fill(Tile.SOLID, x, y, x, bottom)
                    tilesFromFloor = 0
                    solids.append({'x': x, 'y': y})
                else:
                    if tilesFromFloor > -1 and 2 < x < columns - 2:
                        if tilesFromFloor == powerupHeight and tile != mz.PLAYER_RESERVATION and random.random() < self.powerUpProbability:
                            map.place(Tile.CHEST, x, y)
                        elif tilesFromFloor == 1:
                            if map.getTileAt(x, y - 1) == mz.PLAYER_RESERVATION and columnsSinceEnemy[y] > 2 and random.random() < self.enemyProbability:
                                map.place(Tile.MOB, x, y)
                                columnsSinceEnemy[y] = 0
                            elif random.random() < self.coinProbability:
                                map.place(Tile.COIN, x, y)

                if not foundContent:
                    clearBelow[x] = y
                    foundContent = tile != Tile.NONE

        for solid in solids:
            if solid['x'] > 0 and map.getTileAt(solid['x'] - 1, solid['y']) == Tile.NONE and not map.isSolid(solid['x'] - 2, solid['y']) and random.random() < self.platformExtendProbability:
                bottom = rows - 1 if clearBelow[solid['x'] - 1] <= solid['y'] else solid['y']
                map.fill(Tile.SOLID, solid['x'] - 1, solid['y'], solid['x'] - 1, bottom)

            if solid['x'] < columns - 1 and map.getTileAt(solid['x'] + 1, solid['y']) == Tile.NONE and not map.isSolid(solid['x'] + 2, solid['y']) and random.random() < self.platformExtendProbability:
                bottom = rows - 1 if clearBelow[solid['x'] + 1] <= solid['y'] else solid['y']
                map.fill(Tile.SOLID, solid['x'] + 1, solid['y'], solid['x'] + 1, bottom)

        jumpStart = -1
        for i in range(len(path)):
            state = path[i]

            if state.framesSinceGround == 1:
                jumpStart = i
            elif jumpStart >= 0 and state.framesSinceGround == 0:
                start = path[jumpStart]
                distance = abs(state.x - start.x)
                if distance > 3 or abs(start.y - state.y) > 0.5:
                    for j in range(jumpStart, i):
                        here = path[j]
                        x = round(here.x)
                        y = round(here.y)

                        deviation = (here.x - x) ** 2 + (here.y - y) ** 2
                        if deviation < 0.1 and random.random() < self.coinProbability:
                            map.place(Tile.COIN, x, y)
                jumpStart = -1