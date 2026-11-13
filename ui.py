import pygut
import pygut.base
import pygame
import const

class HUD(pygut.base.UIElement):
    def __init__(self):
        self.surf = pygame.Surface((pygut.app.win.size[0] - const.HUD_OFFSET[0] * 2, pygut.app.win.size[1] - const.HUD_OFFSET[1] * 2), pygame.SRCALPHA)
        self.hp_bar = pygame.Surface((const.HP_IMG_DIMENSIONS[0]*const.IMG_SCL + (const.PLAYER_HP-1)*const.HP_IMG_SPACING,
                                      const.HP_IMG_DIMENSIONS[1]))
        super().__init__(pygut.app.center, self.surf)
        
        self.hp_empty_img = pygame.transform.scale(pygame.image.load('assets/hp_empty.png').convert_alpha(), (const.HP_IMG_DIMENSIONS))
        self.hp_full_img = pygame.transform.scale(pygame.image.load('assets/hp_full.png').convert_alpha(), (const.HP_IMG_DIMENSIONS))
        
    def update(self, **kwargs):
        self.surf.fill((0,0,0,0))
        self.set_hp_bar()
    
    def set_hp_bar(self):
        for p in range(0, const.PLAYER_HP):
            if p <= pygut.app.player.hp - 1:
                self.surf.blit(self.hp_full_img, (p*const.HP_IMG_DIMENSIONS[0] + p*const.HP_IMG_SPACING, 0))
            else:
                self.surf.blit(self.hp_empty_img, (p*const.HP_IMG_DIMENSIONS[0] + p*const.HP_IMG_SPACING, 0))