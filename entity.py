from pygut.base import GameElement
from pygut.collider import RectCollider
import pygut
import pygut.base
import pygame
import const
import fsm
import random as rand

player_dim = const.PLAYER_DIMENSIONS
player_img_dim = const.PLAYER_IMG_DIMENSIONS
enemy1_dim = const.ENEMY1_DIMENSIONS
enemy1_img_dim = const.ENEMY1_IMG_DIMENSIONS

class Entity(GameElement):
    def __init__(self, start_platform, hp, start_image, hitbox_dimensions, image_offset, speed_cap = None, falls = True):
        pos = (start_platform.centerx, start_platform.top + hitbox_dimensions[1]/2)
        super().__init__((pos[0] + image_offset[0], pos[1] + image_offset[1]), start_image,
                         RectCollider(pos[0], pos[1], hitbox_dimensions[0], hitbox_dimensions[1]))
        
        self.velocity = pygame.Vector2()
        self.acceleration = pygame.Vector2(0, const.GRAVITY if falls else 0)
        self.speed_cap = speed_cap
        self.moving = False
        
        self.on_ground = False
        self.falls = falls
        
        self.can_attack = True
        self.attacking = False
        self.invincible = False
        
        self.current_platform: Platform = start_platform
        self.hp = hp
        self.max_hp = hp
        self.is_alive = True
        
    def damage(self, dmg: int):
        self.hp -= dmg
        if self.hp <= 0: 
            self.is_alive = False
            self.hp = 0
    def heal(self, dmg: int):
        self.hp += dmg
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def update(self, **kwargs):
        super().update(**kwargs)
        
        self.cap_speed()
        self.move_logic()
        
    def cap_speed(self):
        if self.falls:
            if self.velocity.y > const.MAX_FALL_VELOCITY:
                self.velocity.y = const.MAX_FALL_VELOCITY
            if self.velocity.y < -const.MAX_FALL_VELOCITY:
                self.velocity.y = -const.MAX_FALL_VELOCITY
        elif self.speed_cap is not None:
            if self.velocity.magnitude() > self.speed_cap:
                self.velocity.scale_to_length(self.speed_cap)
            
        if not self.moving:
            self.velocity.x *= const.DRAG

        if self.speed_cap is None: return
        
        if self.invincible and abs(self.velocity.x) > self.speed_cap:
            self.acceleration.x = 0
        
        if not self.invincible:
            if self.velocity.x > self.speed_cap:
                self.velocity.x = self.speed_cap
            if self.velocity.x < -self.speed_cap:
                self.velocity.x = -self.speed_cap
        elif self.velocity.x > self.speed_cap or self.velocity.x < -self.speed_cap:
            self.velocity.x *= const.DRAG
    
    def move_logic(self):
        self.velocity += self.acceleration
        
        self.move((self.velocity.x, 0))
        # future x collision logic here
        
        self.move((0, self.velocity.y))
        # y collision logic
        for e in pygut.app.platforms:
            if self.collider.collides(e.collider):
                if self.velocity.y < 0:
                    self.move((0, self.rect.top - e.rect.bottom))
                    self.velocity.y = 0
                else:
                    self.move((0, e.rect.top - self.rect.bottom))
                    
                    self.on_ground = True
                    self.velocity.y = 0
                    self.acceleration.y = 0
                    
                    if e is not self.current_platform:
                        self.current_platform = e
        
        if not self.on_ground and self.acceleration.y == 0: self.acceleration.y = const.GRAVITY
    
class Player(Entity):
    def __init__(self, start_platform):
        idle_right = pygame.transform.scale(pygame.image.load('assets/player_idle.png').convert_alpha(), player_img_dim)
        idle_left = pygame.transform.flip(idle_right, True, False)
        
        attack_right = pygame.transform.scale(pygame.image.load('assets/player_attack.png').convert_alpha(), player_img_dim)
        attack_left = pygame.transform.flip(attack_right, True, False)
        
        hit_left = pygame.transform.scale(pygame.image.load('assets/player_hit.png').convert_alpha(), player_img_dim)
        hit_right = pygame.transform.flip(hit_left, True, False)
        
        super().__init__(start_platform, const.PLAYER_HP, idle_right, player_dim, (0, player_dim[1] - player_img_dim[1]), const.PLAYER_MAX_SPEED)
        self.current_platform = start_platform
        
        self.facing_right = True
        self.set_inputs(idle_left, idle_right, attack_left, attack_right)
        
        def flip_image():
            if self.invincible:
                if self.image == idle_right or self.image == attack_right: self.image = hit_right
                elif self.image == idle_left or self.image == attack_left: self.image = hit_left
                elif self.image == hit_right: self.image = idle_right
                else: self.image = idle_left
                
                self.iframe_flip_timer.reset()
                return
            
            if self.image == hit_right: self.image = idle_right
            elif self.image == hit_left: self.image = idle_left
        
        def flip_iframes(): 
            self.invincible = not self.invincible
            if self.invincible: self.iframe_flip_timer.reset()
        self.iframe_timer = pygut.Timer(const.PLAYER_IFRAME_SEC, False, flip_iframes, flip_iframes)
        self.iframe_flip_timer = pygut.Timer(const.PLAYER_IFRAME_FLIP_SEC, False, flip_image)
        
        pygut.add_timer(self.iframe_timer)
        pygut.add_timer(self.iframe_flip_timer)
        
    def update(self, **kwargs):
        super().update(**kwargs)
        
        for e in pygut.app.enemies:
            if not self.invincible and self.collider.collides(e.collider):
                self.damage(1, e.pos)
                                
                break
        
    def damage(self, dmg, src_pos):
        super().damage(dmg)
        
        self.iframe_timer.reset()
        
        if self.pos.x < src_pos.x: self.velocity.x = -const.PLAYER_KB_SPEED
        else: self.velocity.x = const.PLAYER_KB_SPEED
        
    def set_inputs(self, idle_left, idle_right, attack_left, attack_right):
        # movement functions called when movement buttons are pressed
        def move_left():
            self.acceleration.x = -const.PLAYER_ACCELERATION
            if self.facing_right: 
                self.image = idle_left
                self.facing_right = False
            
            self.moving = True
        def move_right():
            self.acceleration.x = const.PLAYER_ACCELERATION
            if not self.facing_right:
                self.image = idle_right
                self.facing_right = True
            
            self.moving = True
        def movement_key_up():
            self.moving = False
            self.acceleration.x = 0
        def jump():
            if self.on_ground == True:
                self.velocity.y = const.PLAYER_JUMP_SPEED
                self.on_ground = False
        
        # attack functions to handle animation & kb
        def attack():
            if self.can_attack:
                if self.facing_right:
                    self.image = attack_right
                else:
                    self.image = attack_left
                self.attack_timer.reset()
                self.can_attack = False
        def attack_complete():
            if self.facing_right:
                self.image = idle_right
            else:
                self.image = idle_left
            
            self.can_attack = True
        
        self.add_action(pygame.K_LEFT, pygut.K_HELD, move_left)
        self.add_action(pygame.K_RIGHT, pygut.K_HELD, move_right)
        self.add_action(pygame.K_LEFT, pygut.K_UP, movement_key_up)
        self.add_action(pygame.K_RIGHT, pygut.K_UP, movement_key_up)
        self.add_action(pygame.K_z, pygut.K_DOWN, jump)
        self.add_action(pygame.K_x, pygut.K_DOWN, attack)
        
        self.attack_timer = pygut.base.Timer(const.PLAYER_ATK_DELAY_SEC, False, attack_complete)
        pygut.add_timer(self.attack_timer)

class Enemy(Entity, fsm.Machine):
    def __init__(self, start_platform):
        idle_right = pygame.transform.scale(pygame.image.load('assets/enemy1_idle.png').convert_alpha(), enemy1_img_dim)
        idle_left = pygame.transform.flip(idle_right, True, False)
        
        attack_right = pygame.transform.scale(pygame.image.load('assets/enemy1_attack.png').convert_alpha(), enemy1_img_dim)
        attack_left = pygame.transform.flip(attack_right, True, False)
        
        hit_right = pygame.transform.scale(pygame.image.load('assets/enemy1_hit.png').convert_alpha(), enemy1_img_dim)
        hit_left = pygame.transform.flip(hit_right, True, False)
        
        Entity.__init__(self, start_platform, const.ENEMY1_HP, idle_right, enemy1_dim, (0, enemy1_dim[1]-enemy1_img_dim[1]))
        
        patrol = fsm.State(self.check_player)
        self.states = [patrol]
        
        self.target: Platform = None
        
        fsm.Machine.__init__(self, [patrol], patrol)
        
    def check_player(self):
        # Temp check until generation/world is done and I can write actual a* pathfinding and more fsm states
        return True

    def update(self, **kwargs):
        self.check_state()
        
        if self.current_state == self.states[const.PATROL] and self.target is not None:
            self.target = self.pick_patrol_target()
        
        if self.target is not None:
            pass
            
        Entity.update(self, **kwargs)
        
    def pick_patrol_target(self) -> Platform:
        return rand.choice(self.current_platform.touching)
        
class Platform(GameElement):
    def __init__(self, pos, w, h):
        img = pygame.Surface((w,h))
        img.fill((0,0,255))
        
        super().__init__(pos, img, RectCollider(pos[0], pos[1], w, h))
        self.centerx = pos[0]
        self.top = pos[1] - h/2
        
        self.touching = [self]