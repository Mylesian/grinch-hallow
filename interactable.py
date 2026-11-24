import pygut
import pygame
import entity
import const

class Interactable(entity.Entity):
    def __init__(self, platform, image, trigger):
        super().__init__(platform, 0, image, 0, 0, image.get_size(), (0,0))
        self.trigger = trigger

class Potion(Interactable):
    def __init__(self, platform):
        def collect():
            player = pygut.app.player
            player.heal(const.POTION_HEAL_AMT)
            pygut.app.screen.remove(self)
            pygut.app.interactables.remove(self)
            
        img = pygame.transform.scale(pygame.image.load('assets/potion.png').convert_alpha(), const.POTION_DIMENSIONS)
        
        super().__init__(platform, img, collect)

class Chest(Interactable):
    def __init__(self, platform):
        def collect():
            player = pygut.app.player
            player.heal(const.CHEST_HEAL_AMT)
            pygut.app.screen.remove(self)
            pygut.app.interactables.remove(self)
            
        img = pygame.Surface(const.CHEST_DIMENSIONS)
        img.fill((255,127,0))
        
        super().__init__(platform, img, collect)
        
class Mimic(Interactable):
    def __init__(self, platform):
        def collect():
            player = pygut.app.player
            player.damage(const.MIMIC_DMG_AMT, self.pos)
            pygut.app.screen.remove(self)
            pygut.app.interactables.remove(self)
            
        img = pygame.Surface(const.CHEST_DIMENSIONS)
        img.fill((255,127,0))
        
        super().__init__(platform, img, collect)