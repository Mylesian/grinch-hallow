import pygut
import pygut.base
import pygame
import const
from const import HEIGHT

class HUD(pygut.base.UIElement):
    def __init__(self):
        self.surf = pygame.Surface(pygut.app.win.size, pygame.SRCALPHA)
        self.hp_bar = pygame.Surface(const.HUD_HP_BAR_DIMENSIONS, pygame.SRCALPHA)
        super().__init__(pygut.app.center, self.surf)
        
        self.hp_empty_img = pygame.transform.scale(pygame.image.load('assets/hp_empty.png').convert_alpha(), (const.HP_IMG_DIMENSIONS))
        self.hp_full_img = pygame.transform.scale(pygame.image.load('assets/hp_full.png').convert_alpha(), (const.HP_IMG_DIMENSIONS))
        
        self.debug = pygame.Surface(self.surf.get_size(), pygame.SRCALPHA)
        self.debug_text = pygame.Surface((const.DEBUG_TEXT_WIDTH, self.debug.size[HEIGHT]), pygame.SRCALPHA)
        self.debug_input = pygame.Surface(const.DEBUG_INPUT_DIMENSIONS)
        self.show_debug = False
        
        def toggle_debug():
            self.show_debug = not self.show_debug

        self.add_action(const.TOGGLE_DEBUG_KEY, pygut.K_RELEASED, toggle_debug)
        
    def update(self, **kwargs):
        self.surf.fill((0,0,0,0))
        
        self.set_hp_bar()
        
        if self.show_debug: 
            self.set_debug()
    
    def set_hp_bar(self):
        self.hp_bar.fill((0,0,0,0))
        for p in range(0, const.PLAYER_HP):
            if p <= pygut.app.player.hp - 1:
                self.hp_bar.blit(self.hp_full_img, (p*const.HP_IMG_DIMENSIONS[0] + p*const.HP_IMG_SPACING, 0))
            else:
                self.hp_bar.blit(self.hp_empty_img, (p*const.HP_IMG_DIMENSIONS[0] + p*const.HP_IMG_SPACING, 0))
        self.surf.blit(self.hp_bar, const.HUD_HP_OFFSET)
    
    def set_debug(self):
        self.debug.fill((0,0,0,0))
        
        self.set_player_debug()
        self.set_enemy_debug()
        self.set_interactable_debug()
        self.set_input_debug()
        
        self.surf.blit(self.debug, (0,0))
    
    def set_player_debug(self):
        player = pygut.app.player
        pygame.draw.rect(self.debug, const.DEBUG_PLAYER_CLR, player.collider.bounds, 1)
        
        if player.attack is not None:
            pygame.draw.rect(self.debug, const.DEBUG_PLAYER_ATK_CLR, player.attack.bounds, 1)
    def set_enemy_debug(self):
        enemies = pygut.app.enemies
        self.debug_text.fill((0,0,0,0))
        for i in range(len(enemies)):
            e = enemies[i]
            pygame.draw.rect(self.debug, const.DEBUG_ENEMY_CLR, e.collider.bounds, 1)
            
            e_text = const.DEBUG_FONT.render(f'Enemy {i+1}\nType: {e.type}\nState: {e.current_state.name}\nHP: {e.hp}/{e.max_hp}\n\n',
                                             False, const.DEBUG_TEXT_CLR, wraplength=const.DEBUG_TEXT_WIDTH)
            self.debug_text.blit(e_text, (0, i*const.DEBUG_CHAR_HEIGHT))
            
            if e.attack is not None:
                pygame.draw.rect(self.debug, const.DEBUG_ENEMY_ATK_CLR, e.attack.bounds, 1)
                
            if e.target is not None and e.current_target is not None:
                pygame.draw.rect(self.debug, const.DEBUG_ENEMY_CLR, e.current_target.collider.bounds, 1)
        
        self.debug.blit(self.debug_text, (self.debug.width - const.DEBUG_TEXT_WIDTH, 0))
    def set_interactable_debug(self):
        ibles = pygut.app.interactables
        
        for i in ibles:
            pygame.draw.rect(self.debug, const.DEBUG_INTERACTABLE_CLR, i.collider.bounds, 1)
    def set_input_debug(self):
        pressed = pygame.key.get_pressed()
        
        jump = const.DEBUG_FONT.render('JUMP ', False, const.DEBUG_INPUT_PRESSED_CLR if pressed[const.PLAYER_JUMP_KEY] else const.DEBUG_INPUT_UNPRESSED_CLR)
        atk = const.DEBUG_FONT.render('ATK ', False, const.DEBUG_INPUT_PRESSED_CLR if pressed[const.PLAYER_ATK_KEY] else const.DEBUG_INPUT_UNPRESSED_CLR)
        left = const.DEBUG_FONT.render('<- ', False, const.DEBUG_INPUT_PRESSED_CLR if pressed[const.PLAYER_LEFT_KEY] else const.DEBUG_INPUT_UNPRESSED_CLR)
        up = const.DEBUG_FONT.render('^ ', False, const.DEBUG_INPUT_PRESSED_CLR if pressed[const.PLAYER_INTERACT_KEY] else const.DEBUG_INPUT_UNPRESSED_CLR)
        right = const.DEBUG_FONT.render('->', False, const.DEBUG_INPUT_PRESSED_CLR if pressed[const.PLAYER_RIGHT_KEY] else const.DEBUG_INPUT_UNPRESSED_CLR)
        
        self.debug_input.blit(jump)
        self.debug_input.blit(atk, (jump.width, 0))
        self.debug_input.blit(left, (jump.width+atk.width, 0))
        self.debug_input.blit(up, (jump.width+atk.width+left.width, 0))
        self.debug_input.blit(right, (jump.width+atk.width+left.width+right.width, 0))
        
        self.debug.blit(self.debug_input, (0, self.debug.height - self.debug_input.height))