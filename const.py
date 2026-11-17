import pygame

class screen_constants():
    FPS = 60
    # IMG_SCL = 4
    WIDTH = 1000
    HEIGHT = 650
    # X = 0
    # Y = 1
    DT = 1/60
    BACKGROUND_COLOR = (20, 24, 40)
    TILES = 50
    CELL_SIZE = WIDTH // TILES

# # Player non-graphical constants
# PLAYER_MAX_SPEED = 40 / screen_constants.FPS
# PLAYER_ACCELERATION = 600 / screen_constants.FPS
# PLAYER_ATK_DELAY_SEC = 0.3
# PLAYER_JUMP_SPEED = -1200 / screen_constants.FPS
# PLAYER_IFRAME_SEC = 0.7
# PLAYER_HP = 6
# PLAYER_DMG = 6
# PLAYER_DIMENSIONS = (13*screen_constants.IMG_SCL, 20*screen_constants.IMG_SCL)
# PLAYER_ATK_DIMENSIONS = (24*screen_constants.IMG_SCL, 12*screen_constants.IMG_SCL)
# PLAYER_KB_SPEED = 2000 / screen_constants.FPS
# PLAYER_LEFT_KEY = pygame.K_LEFT
# PLAYER_RIGHT_KEY = pygame.K_RIGHT
# PLAYER_JUMP_KEY = pygame.K_z
# PLAYER_ATK_KEY = pygame.K_x
# PLAYER_INTERACT_KEY = pygame.K_UP

# # Enemy1 non-graphical constants
# ENEMY1_PATROL_SPEED = 240 / screen_constants.FPS
# ENEMY1_HP = 20
# ENEMY1_DIMENSIONS = (20*screen_constants.IMG_SCL, 33*screen_constants.IMG_SCL)
# ENEMY1_KB_SPEED = 1400 / screen_constants.FPS
# ENEMY1_IFRAME_SEC = 0.4

# # Graphical constants
# PLAYER_IMG_DIMENSIONS = (54*screen_constants.IMG_SCL, 24*screen_constants.IMG_SCL)
# ENEMY1_IMG_DIMENSIONS = (87*screen_constants.IMG_SCL, 46*screen_constants.IMG_SCL)
# IFRAME_FLIP_SEC = 0.1

# # Universal gameplay constants
# GRAVITY = 60 / screen_constants.FPS
# MAX_FALL_VELOCITY = 3000 / screen_constants.FPS
# DRAG = 0.75

# # Interactable constants
# POTION_HEAL_AMT = 1
# POTION_DIMENSIONS = (9*screen_constants.IMG_SCL, 12*screen_constants.IMG_SCL)

# # Base HUD constants
# HP_IMG_DIMENSIONS = (16*screen_constants.IMG_SCL, 14*screen_constants.IMG_SCL)
# HP_IMG_SPACING = 1*screen_constants.IMG_SCL
# HUD_HP_OFFSET = (10,10)
# HUD_HP_BAR_DIMENSIONS = (HP_IMG_DIMENSIONS[screen_constants.WIDTH]*PLAYER_HP + HP_IMG_SPACING*(PLAYER_HP-1), HP_IMG_DIMENSIONS[screen_constants.HEIGHT])

# # Debug constants
# TOGGLE_DEBUG_KEY = pygame.K_F3
# METRICS_ADVANCE_INDEX = 4
# DEBUG_FONT = pygame.font.SysFont('Times New Roman', 20)
# DEBUG_CHAR_WIDTH_EST = DEBUG_FONT.metrics('_')[0][METRICS_ADVANCE_INDEX]
# DEBUG_CHAR_HEIGHT = DEBUG_FONT.get_height()

# DEBUG_TEXT_COL = 25
# DEBUG_TEXT_WIDTH = DEBUG_CHAR_WIDTH_EST * DEBUG_TEXT_COL

# DEBUG_INPUT_COL = 16
# DEBUG_INPUT_DIMENSIONS = (DEBUG_CHAR_WIDTH_EST * DEBUG_INPUT_COL, DEBUG_CHAR_HEIGHT)

# DEBUG_INPUT_UNPRESSED_CLR = (255, 255, 255)
# DEBUG_INPUT_PRESSED_CLR = (0, 255, 0)
# DEBUG_TEXT_CLR = (255, 255, 255)
# DEBUG_PLAYER_CLR = (0, 255, 0)
# DEBUG_PLAYER_ATK_CLR = (255, 0, 255)
# DEBUG_ENEMY_CLR = (255, 0, 0)
# DEBUG_ENEMY_ATK_CLR = (255, 255, 0)
# DEBUG_INTERACTABLE_CLR = (0, 255, 255)

# # FSM States
# PATROL = 0
# CHASE = 1
# ATTACK = 2

class img_consts:
    PLAYER = 0
    SOLID = 0
    COIN = 0
    CHEST = 0
    NONE = None
    MOB = 0

class maze_consts:
    MAZE = 0
    SOLID_RESERVATION = '▀'
    PLAYER_RESERVATION = '×'

class colors:
    COLOR_BG = (22, 22, 29)         # Dark slate blue
    COLOR_WALL = (145, 150, 163)     # Muted silver gray
    COLOR_START = (39, 174, 96)      # Soft green
    COLOR_GOAL = (192, 57, 43)       # Soft red
    COLOR_PLAYER = (52, 152, 219)    # Bright blue
    COLOR_VISITED = (44, 62, 80)     # Dark accent for carved rooms during generation
    COLOR_CURRENT = (241, 196, 15)
