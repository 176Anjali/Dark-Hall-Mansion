# ==========================================
# DARK HALL MANSION - SETTINGS
# ==========================================
import math
WIDTH = 1280
HEIGHT = 720
FPS = 60

TITLE = "Dark Hall Mansion"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

MENU_BG = (8, 8, 12)
MENU_TEXT = (220, 220, 220)
MENU_SELECTED = (180, 30, 30)
MENU_DIM = (120, 120, 120)

# ==========================================
# PLAYER
# ==========================================

PLAYER_X = 5.5
PLAYER_Y = 13.5
PLAYER_ANGLE = -math.pi / 2

MOVE_SPEED = 3.0
RUN_SPEED = 5.0

PLAYER_RADIUS = 0.20

# ==========================================
# MOUSE
# ==========================================

MOUSE_SENSITIVITY = 0.0025

# ==========================================
# CAMERA
# ==========================================

FOV = 60
MAX_DEPTH = 20

# ==========================================
# AUDIO
# ==========================================

MASTER_VOLUME = 0.8
SFX_VOLUME = 0.8

# ==========================================
# GAME STATES
# ==========================================

MENU = "menu"
DOOR = "door"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
WIN = "win"
HOW_TO_PLAY = "how_to_play"
OPTIONS = "options"
