"""
Constants for the Asteroid Navigator game.
"""

# Game window settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (0, 0, 0)  # Black

# Player settings
PLAYER_SIZE = 60
PLAYER_SPEED = 300  # Pixels per second
PLAYER_MAX_HEALTH = 100
PLAYER_ACCELERATION = 1200  # Acceleration rate (pixels/second²)
PLAYER_DECELERATION = 900   # Deceleration rate (pixels/second²)

# Health bar settings
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_BORDER = 2
HEALTH_BAR_COLOR = (0, 255, 0)  # Green
HEALTH_BAR_BACKGROUND_COLOR = (100, 100, 100)  # Gray
HEALTH_BAR_BORDER_COLOR = (255, 255, 255)  # White

# Asteroid settings
ASTEROID_SIZES = {
    "small": {"min": 15, "max": 25},
    "medium": {"min": 26, "max": 40},
    "large": {"min": 41, "max": 60}
}
ASTEROID_MIN_SPEED = 50
ASTEROID_MAX_SPEED = 200
ASTEROID_SPAWN_RATE = 0.5  # Seconds between spawns (average)

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

# Particle system settings
ASTEROID_PARTICLE_COLORS = [
    (255, 165, 0),    # Orange
    (255, 140, 0),    # Dark Orange
    (255, 69, 0),     # Red-Orange
    (255, 215, 0),    # Gold
    (255, 99, 71)     # Tomato
]
PLAYER_THRUSTER_COLORS = [
    (0, 191, 255),    # Deep Sky Blue
    (30, 144, 255),   # Dodger Blue
    (65, 105, 225),   # Royal Blue
    (100, 149, 237),  # Cornflower Blue
    (135, 206, 250)   # Light Sky Blue
]
MAX_PARTICLES = 500
PARTICLE_LIFETIME = 1.0  # Seconds before a particle disappears

# Background stars settings
NUM_STARS = 100
STAR_SIZES = [1, 2, 3]  # Different star sizes
STAR_COLORS = [
    (255, 255, 255),  # White
    (200, 200, 255),  # Light Blue
    (255, 255, 200),  # Light Yellow
]
STAR_SPEEDS = [20, 40, 60]  # Different star speeds

# Countdown timer settings
COUNTDOWN_DURATION = 3  # seconds
COUNTDOWN_FONT_SIZE = 120
COUNTDOWN_COLOR = (255, 255, 255)  # White

# Scene transition settings
FADE_DURATION = 1.0  # seconds
MUSIC_FADE_DURATION = 1000  # milliseconds

# Font sizes
SCORE_FONT_SIZE = 30
GAME_OVER_FONT_SIZE = 75
TITLE_FONT_SIZE = 90
INSTRUCTION_FONT_SIZE = 25

# Score color
SCORE_COLOR = (255, 255, 255)  # White

# Game state identifiers
STATE_MENU = 0
STATE_COUNTDOWN = 1
STATE_PLAYING = 2
STATE_GAME_OVER = 3

# File paths
PLAYER_IMAGE_PATH = "assets/images/player.png"
LOGO_IMAGE_PATH = "assets/images/logo.png"
ASTEROID_IMAGE_PATTERN = "assets/images/asteroids/a{}.png"  # Format with 0-6
MENU_MUSIC_PATH = "assets/sound/Lone Knight in the Stars(Menu Scene).ogg"
GAME_MUSIC_PATH = "assets/sound/Pixel Knight Asteroid Chase(Game Scene).ogg"
GAME_OVER_MUSIC_PATH = "assets/sound/Asteroid Knight(Game Over).ogg" 