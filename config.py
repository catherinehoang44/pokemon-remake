"""
Game configuration settings
"""

# Screen settings
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
FPS = 60

# Colors (Pokemon-style palette)
BG_COLOR = (135, 206, 235)  # Sky blue background
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game settings
GAME_TITLE = "Pokemon Adventure"

# Tile size for pixel art (16x16 or 32x32)
TILE_SIZE = 32

# Player movement speed
PLAYER_SPEED = 3

# Paths
ASSETS_PATH = "assets"
SPRITES_PATH = f"{ASSETS_PATH}/sprites"
IMAGES_PATH = f"{ASSETS_PATH}/images"
SOUNDS_PATH = f"{ASSETS_PATH}/sounds"
FONTS_PATH = f"{ASSETS_PATH}/fonts"

class Config:
    SCREEN_WIDTH = SCREEN_WIDTH
    SCREEN_HEIGHT = SCREEN_HEIGHT
    FPS = FPS
    BG_COLOR = BG_COLOR
    WHITE = WHITE
    BLACK = BLACK
    GRAY = GRAY
    DARK_GRAY = DARK_GRAY
    RED = RED
    GREEN = GREEN
    BLUE = BLUE
    GAME_TITLE = GAME_TITLE
    TILE_SIZE = TILE_SIZE
    PLAYER_SPEED = PLAYER_SPEED
    ASSETS_PATH = ASSETS_PATH
    SPRITES_PATH = SPRITES_PATH
    IMAGES_PATH = IMAGES_PATH
    SOUNDS_PATH = SOUNDS_PATH
    FONTS_PATH = FONTS_PATH




