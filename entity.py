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
    def __init__(self, start_platform, hp, start_image, iframe_time, hit_kb_speed, hitbox_dimensions, image_offset, speed_cap = None, falls = True):
        pos = (start_platform.centerx, start_platform.top + hitbox_dimensions[1]/2)
        super().__init__((pos[0] + image_offset[0], pos[1] + image_offset[1]), start_image,
                         RectCollider(pos[0], pos[1], hitbox_dimensions[0], hitbox_dimensions[1]))
        
        self.velocity = pygame.Vector2()
        self.acceleration = pygame.Vector2(0, const.GRAVITY if falls else 0)
        self.speed_cap = speed_cap
        self.moving = False
        self.facing_right = True
        
        self.on_ground = False
        self.falls = falls
        
        self.can_attack = True
        self.attacking = False
        self.invincible = False
        
        self.current_platform: Platform = start_platform
        self.hp = hp
        self.max_hp = hp
        self.is_alive = True
        self.hit_kb_speed = hit_kb_speed

        def flip_image():
            if not self.is_alive: return
            if self.invincible:
                if self.image == self.idle_right or self.image == self.attack_right: self.image = self.hit_right
                elif self.image == self.idle_left or self.image == self.attack_left: self.image = self.hit_left
                elif self.image == self.hit_right: self.image = self.idle_right
                else: self.image = self.idle_left
                
                self.iframe_flip_timer.reset()
                return
            
            if self.image == self.hit_right: self.image = self.idle_right
            elif self.image == self.hit_left: self.image = self.idle_left
        
        def flip_iframes(): 
            self.invincible = False
            self.can_attack = True
        self.iframe_timer = pygut.Timer(iframe_time, False, flip_iframes)
        self.iframe_flip_timer = pygut.Timer(const.IFRAME_FLIP_SEC, False, flip_image)
        
        pygut.add_timer(self.iframe_timer)
        pygut.add_timer(self.iframe_flip_timer)
        
        self.attack = None

    def damage(self, dmg, src_pos):
        self.hp -= dmg
        if self.hp <= 0: 
            self.kill()
            return
        
        self.invincible = True
        self.can_attack = False
        self.iframe_timer.reset()
        self.iframe_flip_timer.reset()
        
        if self.pos.x < src_pos.x: self.velocity.x = -self.hit_kb_speed
        else: self.velocity.x = self.hit_kb_speed
        
        if self.hp <= 0:
            self.hp = 0
            self.kill()
      
    def kill(self):
        self.image = self.dead
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
        self.idle_right = pygame.transform.scale(pygame.image.load('assets/player_idle.png').convert_alpha(), player_img_dim)
        self.idle_left = pygame.transform.flip(self.idle_right, True, False)
        
        self.attack_right = pygame.transform.scale(pygame.image.load('assets/player_attack.png').convert_alpha(), player_img_dim)
        self.attack_left = pygame.transform.flip(self.attack_right, True, False)
        
        self.hit_left = pygame.transform.scale(pygame.image.load('assets/player_hit.png').convert_alpha(), player_img_dim)
        self.hit_right = pygame.transform.flip(self.hit_left, True, False)
        
        self.dead = pygame.transform.scale(pygame.image.load('assets/player_dead.png').convert_alpha(), player_img_dim)
        
        super().__init__(start_platform, const.PLAYER_HP, self.idle_right, const.PLAYER_IFRAME_SEC, const.PLAYER_KB_SPEED, player_dim, (0, player_dim[1] - player_img_dim[1]), const.PLAYER_MAX_SPEED)
        self.current_platform = start_platform
        
        self.set_inputs()
        
    def update(self, **kwargs):
        super().update(**kwargs)
        
        if not self.is_alive: return

        for e in pygut.app.enemies:
            if not self.invincible and e.is_alive and self.collider.collides(e.collider):
                self.damage(1, e.pos)
                                
                break
        
    def set_inputs(self):
        # movement functions called when movement buttons are pressed
        def move_left():
            if not self.is_alive: return
            
            self.acceleration.x = -const.PLAYER_ACCELERATION
            if self.facing_right: 
                self.image = self.idle_left
                self.facing_right = False
                
                if self.attack is not None and self.attack.attach_right:
                    self.attack = None
            
            self.moving = True
        def move_right():
            if not self.is_alive: return
            
            self.acceleration.x = const.PLAYER_ACCELERATION
            if not self.facing_right:
                self.image = self.idle_right
                self.facing_right = True
                
                if self.attack is not None and not self.attack.attach_right:
                    self.attack = None
            
            self.moving = True
        def movement_key_up():
            self.moving = False
            self.acceleration.x = 0
        def jump():
            if self.on_ground == True and self.is_alive:
                self.velocity.y = const.PLAYER_JUMP_SPEED
                self.on_ground = False
        
        # attack functions to handle animation & kb
        def attack():
            if self.can_attack and self.is_alive:
                if self.facing_right:
                    self.image = self.attack_right
                else:
                    self.image = self.attack_left
                self.attack = Attack(self, const.PLAYER_ATK_DIMENSIONS)
                self.attack_timer.reset()
                self.can_attack = False
        def attack_complete():
            if not self.is_alive: return
            
            if self.facing_right:
                self.image = self.idle_right
            else:
                self.image = self.idle_left
            
            self.attack = None
            self.can_attack = True
        
        self.add_action(pygame.K_LEFT, pygut.K_HELD, move_left)
        self.add_action(pygame.K_RIGHT, pygut.K_HELD, move_right)
        self.add_action(pygame.K_LEFT, pygut.K_UP, movement_key_up)
        self.add_action(pygame.K_RIGHT, pygut.K_UP, movement_key_up)
        self.add_action(pygame.K_z, pygut.K_DOWN, jump)
        self.add_action(pygame.K_x, pygut.K_DOWN, attack)
        
        self.attack_timer = pygut.base.Timer(const.PLAYER_ATK_DELAY_SEC, False, attack_complete)
        pygut.add_timer(self.attack_timer)

class Attack(RectCollider):
    def __init__(self, parent: Entity, size):
        self.parent = parent
        
        if parent.facing_right:
            x = parent.collider.bounds.right + size[0]/2
            self.attach_right = True
        else:
            x = parent.collider.bounds.left - size[0]/2
            self.attach_right = False
        
        y = (parent.collider.bounds.top + parent.collider.bounds.bottom) / 2
        super().__init__(x, y, size[0], size[1])

class Enemy(Entity, fsm.Machine):
    def __init__(self, start_platform):
        self.idle_right = pygame.transform.scale(pygame.image.load('assets/enemy1_idle.png').convert_alpha(), enemy1_img_dim)
        self.idle_left = pygame.transform.flip(self.idle_right, True, False)
        
        self.attack_right = pygame.transform.scale(pygame.image.load('assets/enemy1_attack.png').convert_alpha(), enemy1_img_dim)
        self.attack_left = pygame.transform.flip(self.attack_right, True, False)
        
        self.hit_right = pygame.transform.scale(pygame.image.load('assets/enemy1_hit.png').convert_alpha(), enemy1_img_dim)
        self.hit_left = pygame.transform.flip(self.hit_right, True, False)
        
        self.dead = pygame.transform.scale(pygame.image.load('assets/enemy1_dead.png').convert_alpha(), enemy1_img_dim)
        
        Entity.__init__(self, start_platform, const.ENEMY1_HP, self.idle_right, const.ENEMY1_IFRAME_SEC, const.ENEMY1_KB_SPEED, enemy1_dim, (0, enemy1_dim[1]-enemy1_img_dim[1]))
        
        patrol = fsm.State(self.check_player)
        self.states = [patrol]
        
        self.target: Platform = None
        
        fsm.Machine.__init__(self, [patrol], patrol)
        
    def check_player(self):
        # Temp check until generation/world is done and I can write actual a* pathfinding and more fsm states
        return True

    def update(self, **kwargs):
        player = pygut.app.player
        self.check_state()
        
        if not self.invincible and player.attack is not None and self.collider.collides(player.attack):
            self.damage(const.PLAYER_DMG, player.pos)
        
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