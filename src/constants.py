"""
Constants and configuration settings for Asteroid Navigator.
"""
import os

# --- Screen/Display Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (0, 0, 0)  # Black

# --- Player Constants ---
PLAYER_SIZE = 60  # Increased from 40 to make player bigger
PLAYER_SPEED = 300  # Pixels per second

# --- Health Bar Constants ---
PLAYER_MAX_HEALTH = 100
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_BORDER = 2
HEALTH_BAR_COLOR = (0, 255, 0)  # Green
HEALTH_BAR_BACKGROUND_COLOR = (100, 100, 100)  # Gray
HEALTH_BAR_BORDER_COLOR = (255, 255, 255)  # White

# --- Background Stars Constants ---
NUM_STARS = 100
STAR_SIZES = [1, 2, 3]  # Different star sizes
STAR_COLORS = [
    (255, 255, 255),  # White
    (200, 200, 255),  # Light Blue
    (255, 255, 200),  # Light Yellow
]
STAR_SPEEDS = [20, 40, 60]  # Different star speeds

# --- Countdown Timer Constants ---
COUNTDOWN_DURATION = 3  # seconds
COUNTDOWN_FONT_SIZE = 120
COUNTDOWN_COLOR = (255, 255, 255)  # White

# --- Scene Transition Constants ---
FADE_DURATION = 1.0  # seconds
MUSIC_FADE_DURATION = 1000  # milliseconds

# --- Asteroid Constants ---
ASTEROID_SIZES = {
    "small": {"min": 15, "max": 25},
    "medium": {"min": 26, "max": 40},
    "large": {"min": 41, "max": 60}
}
ASTEROID_MIN_SPEED = 50  # Pixels per second
ASTEROID_MAX_SPEED = 200  # Pixels per second
# Speed multipliers for different sizes (smaller = faster)
ASTEROID_SPEED_MULTIPLIERS = {
    "small": 1.4,
    "medium": 1.0,
    "large": 0.7
}
# Asteroid type spawn weights (higher number = more frequent)
ASTEROID_TYPE_WEIGHTS = {
    0: 25,  # a0 - Very common
    1: 20,  # a1
    2: 15,  # a2
    3: 10,  # a3
    4: 7,   # a4
    5: 4,   # a5
    6: 2    # a6 - Very rare
}
# Allowed size categories by asteroid type
# Higher asteroid numbers (more dangerous) are limited to smaller sizes
ASTEROID_SIZE_RESTRICTIONS = {
    0: ["small", "medium", "large"],  # a0 - All sizes allowed
    1: ["small", "medium", "large"],  # a1 - All sizes allowed
    2: ["small", "medium", "large"],  # a2 - All sizes allowed
    3: ["small", "medium"],          # a3 - Medium and small only
    4: ["small", "medium"],          # a4 - Medium and small only
    5: ["small"],                     # a5 - Small only
    6: ["small"]                      # a6 - Small only (most dangerous)
}
# Base damage values by asteroid type (higher = more damage)
ASTEROID_BASE_DAMAGE = {
    0: 5,    # a0 - Minimal damage
    1: 10,   # a1
    2: 15,   # a2
    3: 25,   # a3
    4: 35,   # a4
    5: 50,   # a5
    6: 80    # a6 - Very dangerous
}
# Damage multipliers by size (larger = more damage)
ASTEROID_SIZE_DAMAGE_MULTIPLIERS = {
    "small": 1.0,     # Base damage
    "medium": 1.5,    # 50% more damage
    "large": 2.0      # Double damage
}
ASTEROID_SPAWN_RATE = 0.5  # Seconds between spawns (average)

# --- Font Constants ---
SCORE_FONT_SIZE = 30
SCORE_COLOR = (255, 255, 255)  # White
GAME_OVER_FONT_SIZE = 75
TITLE_FONT_SIZE = 90
INSTRUCTION_FONT_SIZE = 25

# --- Game States ---
START = 0
COUNTDOWN = 1  # New state for countdown
PLAYING = 2    # Changed from 1 to 2
GAME_OVER = 3  # Changed from 2 to 3

# --- Asset Paths ---
# Using os.path.join for cross-platform compatibility
ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUND_DIR = os.path.join(ASSETS_DIR, "sound")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Image paths
PLAYER_IMG_PATH = os.path.join(IMAGES_DIR, "player.png")
ASTEROID_IMG_DIR = os.path.join(IMAGES_DIR, "asteroids")
LOGO_IMG_PATH = os.path.join(IMAGES_DIR, "logo.png")

# Sound paths
MENU_MUSIC_PATH = os.path.join(SOUND_DIR, "Lone Knight in the Stars(Menu Scene).ogg")
GAME_MUSIC_PATH = os.path.join(SOUND_DIR, "Pixel Knight Asteroid Chase(Game Scene).ogg")
GAME_OVER_MUSIC_PATH = os.path.join(SOUND_DIR, "Asteroid Knight(Game Over).ogg") 