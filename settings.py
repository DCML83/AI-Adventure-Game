import random

# define some colors (R, G, B)
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
DARK_GREY   = ( 40,  40,  40)
LIGHT_GREY  = (100, 100, 100)
GREEN       = (  0, 255,   0)
B_GREEN     = (  50, 255,   50)
BLUE        = (  0,   0, 255)
RED         = (255,   0,   0)
YELLOW      = (255, 255,   0)
PURPLE      = (255,   0, 255)
TILE_COLOR  = [DARK_GREY,BLUE, GREEN, LIGHT_GREY, RED, BLACK]
COLOR_UPDATE = 800

# display settings
FPS         = 60
TITLE       = "Kris' Adventure"
FONT_NAME   = "monospace"
FONT_SIZE   = 16
FONT_BOLD   = True
FONT_COLOR  = WHITE
BG_COLOR    = LIGHT_GREY
GRID_COLOR  = DARK_GREY
TILE_SIZE   = 13
MAP_FILE    = 'resource/map/convert.txt'
MAX_SIZE    = 3
DRAW_EXPANDED = True
SHOW_VALUE_GRID_SIZE = range(-5, 5)

#RL setting 
STATE_WALKABLE = 0
STATE_BLOCKED  = 1
STATE_TERMINAL = 2
RL_GAMMA = 1.0

#Game setting
ENEMIES  = 10   # number of enemies show on the map
POTIONS  = 5       #number of healing potion show on the map
#Game image
enemy1 = "resource/image/character/enemy1.png"
enemy2 = "resource/image/character/enemy2.png"
enemy3 = "resource/image/character/enemy3.png"
CHARACTER = "resource/image/character/kris_tran.png"
CLAW = "resource/image/character/Claw_Marks.png"
SWORD_IMAGE = "resource/image/character/slashes.png"
ENEMIES_IMAGES =[enemy1, enemy2, enemy3]

HEALTH_WARNING = 4

bg1 = "resource/image/background/forest_bg.png"
bg2 = "resource/image/background/desert_bg.png"
bg3 = "resource/image/background/space_bg.png"
bg4 = "resource/image/background/fortress_bg.png"
FULL_MOON = "resource/image/background/full_moon_bg.png"
INTRO_KRIS= "resource/image/background/intro_kris_sword.png"
INTRO_BACK="resource/image/background/intro_bg.png"
LIGHTNING = "resource/image/background/lightning.png"
BACKGROUNDS=[bg1, bg2, bg3, bg4]
BG_CHOICE = random.choice(BACKGROUNDS)

#sound effect file
HEAL = 'resource/soundeffect/takepotion.wav'
BACKGROUND_MUSIC = 'resource/soundeffect/backgroundmusic.wav'
BATTLE_MUSIC ='resource/soundeffect/5984.mp3'
SWORD = 'resource/soundeffect/sword-gesture.wav'
CLAWS= 'resource/soundeffect/claws.wav'
FIGHT = 'resource/soundeffect/fight.wav'
GAME_OVER =  'resource/soundeffect/gameover.wav'
LIGHTING_SOUND =  'resource/soundeffect/lightingsound.wav'
BACKGROUNDS_VOLUMN = 0.3
# pathfinding settings
DIAGONAL_COST = 141
CARDINAL_COST = 100
LEGAL_ACTIONS = [(-1, -1), (0, -1), (1, -1),
                 (-1,  0),          (1,  0),
                 (-1,  1), (0,  1), (1,  1)]

UP = 1
DOWN = 6
LEFT = 3
RIGHT = 4