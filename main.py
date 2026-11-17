import pygame
pygame.init()

import pygut
import pygut.base
import entity
import interactable
import ui

class Game(pygut.Application):
    def __init__(self):
        super().__init__((400, 400), maximize=True, handle_init=False)
        w = self.win.get_surface().width
        h = self.win.get_surface().height
        
        self.hud = ui.HUD()
        
        # temp creation for testing while worldgen is being finished
        self.platforms = [entity.Platform((w/4, h-25), w/2, 50), entity.Platform((5*w/8, h-75), w/4, 50, False), entity.Platform((7*w/8, h-75), w/4, 50, True)]
        self.platforms[0].touching.append(self.platforms[1])
        self.platforms[1].touching += [self.platforms[0], self.platforms[2]]
        self.platforms[2].touching.append(self.platforms[1])
        
        self.player = entity.Player(self.platforms[0])
        self.enemies = [entity.Enemy(self.platforms[2])]
        self.interactables: list[interactable.Interactable] = [interactable.Mimic(self.platforms[0])]
        
        game_screen = pygut.base.Screen((50,50,50), [self.player, self.hud] + self.platforms + self.enemies + self.interactables)
        
        self.set_screen(game_screen)
        
game = Game()
game.run()
