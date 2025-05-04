import pygame
import sys
import random
import os # Import os for path joining
import math # For calculating star movement
from pygame.locals import * # Import constants like K_LEFT, QUIT etc.
from pygame.math import Vector2 # Import Vector2

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (0, 0, 0) # Black
PLAYER_SIZE = 60 # Increased from 40 to make player bigger
PLAYER_SPEED = 300 # Pixels per second

# Player health constants
PLAYER_MAX_HEALTH = 100
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_BORDER = 2
HEALTH_BAR_COLOR = (0, 255, 0)  # Green
HEALTH_BAR_BACKGROUND_COLOR = (100, 100, 100)  # Gray
HEALTH_BAR_BORDER_COLOR = (255, 255, 255)  # White

# Particle system constants
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
MAX_PARTICLES = 100   # Maximum number of particles in the system
PARTICLE_LIFETIME = 1.0  # Seconds before a particle disappears

# Background stars constants
NUM_STARS = 100
STAR_SIZES = [1, 2, 3]  # Different star sizes
STAR_COLORS = [
    (255, 255, 255),  # White
    (200, 200, 255),  # Light Blue
    (255, 255, 200),  # Light Yellow
]
STAR_SPEEDS = [20, 40, 60]  # Different star speeds

# Countdown timer constants
COUNTDOWN_DURATION = 3  # seconds
COUNTDOWN_FONT_SIZE = 120
COUNTDOWN_COLOR = (255, 255, 255)  # White

# Scene transition constants
FADE_DURATION = 1.0  # seconds
MUSIC_FADE_DURATION = 1000  # milliseconds

# Asteroid size categories and ranges
ASTEROID_SIZES = {
    "small": {"min": 15, "max": 25},
    "medium": {"min": 26, "max": 40},
    "large": {"min": 41, "max": 60}
}
ASTEROID_MIN_SPEED = 50  # Pixels per second # Reverted
ASTEROID_MAX_SPEED = 200 # Pixels per second # Reverted
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
ASTEROID_SPAWN_RATE = 0.5 # Seconds between spawns (average) # Reverted
SCORE_FONT_SIZE = 30
SCORE_COLOR = (255, 255, 255) # White
GAME_OVER_FONT_SIZE = 75
TITLE_FONT_SIZE = 90
INSTRUCTION_FONT_SIZE = 25

# --- Game States ---
START = 0
COUNTDOWN = 1  # New state for countdown
PLAYING = 2    # Changed from 1 to 2
GAME_OVER = 3  # Changed from 2 to 3

# --- Game Initialization ---
pygame.init()
# Initialize the mixer module *AFTER* pygame.init()
pygame.mixer.init()

# Setup display FIRST
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroid Navigator") # Reverted window title

# --- Asset Loading (Moved here) ---
# Load images - use os.path.join for cross-platform compatibility
try:
    # Load and convert images *after* display is set
    PLAYER_IMG = pygame.image.load(os.path.join("assets", "images", "player.png")).convert_alpha()
    # Load all asteroid images (a0-a6)
    ASTEROID_IMGS = {}
    for i in range(7):  # 0 to 6
        img_path = os.path.join("assets", "images", "asteroids", f"a{i}.png")
        ASTEROID_IMGS[i] = pygame.image.load(img_path).convert_alpha()
    LOGO_IMG = pygame.image.load(os.path.join("assets", "images", "logo.png")).convert_alpha() # Load logo
except pygame.error as e:
    print(f"Error loading image: {e}")
    # Optionally, create fallback surfaces if images fail to load
    PLAYER_IMG = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
    PLAYER_IMG.fill((0, 255, 0)) # Green fallback
    
    # Create fallback surfaces for asteroids
    ASTEROID_IMGS = {}
    for i in range(7):  # 0 to 6
        ASTEROID_IMGS[i] = pygame.Surface((ASTEROID_SIZES["large"]["max"], ASTEROID_SIZES["large"]["max"]))
        ASTEROID_IMGS[i].set_colorkey((0,0,0))
        # Use different colors for different asteroid types in fallback
        color = (128 + i * 18, 128 - i * 18, 128)  # Vary colors for different asteroid types
        pygame.draw.ellipse(ASTEROID_IMGS[i], color, (0, 0, ASTEROID_SIZES["large"]["max"], ASTEROID_SIZES["large"]["max"]))

# Load music for each game state
try:
    MENU_MUSIC = os.path.join("assets", "sound", "Lone Knight in the Stars(Menu Scene).ogg")
    GAME_MUSIC = os.path.join("assets", "sound", "Pixel Knight Asteroid Chase(Game Scene).ogg")
    GAME_OVER_MUSIC = os.path.join("assets", "sound", "Asteroid Knight(Game Over).ogg")
except pygame.error as e:
    print(f"Error loading music files: {e}")

# Fade surfaces for transitions
fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0, 0, 0))  # Black surface for fading

clock = pygame.time.Clock()

# --- Font Loading ---
# Use default fonts directly
default_font_path = None # Use pygame default
score_font = pygame.font.Font(default_font_path, SCORE_FONT_SIZE)
game_over_font = pygame.font.Font(default_font_path, GAME_OVER_FONT_SIZE)
title_font = pygame.font.Font(default_font_path, TITLE_FONT_SIZE)
instruction_font = pygame.font.Font(default_font_path, INSTRUCTION_FONT_SIZE)
countdown_font = pygame.font.Font(default_font_path, COUNTDOWN_FONT_SIZE)

# --- Particle Class ---
class Particle:
    def __init__(self, x, y, color, velocity=(0, 0), size=2, lifetime=PARTICLE_LIFETIME, gravity=False, fade=True):
        """Initialize a particle with position, color, and optional parameters."""
        self.x = x
        self.y = y
        self.color = color
        self.original_color = color  # Store original color for alpha calculations
        self.velocity = Vector2(velocity)
        self.size = size
        self.lifetime = lifetime
        self.age = 0.0
        self.gravity = gravity
        self.fade = fade
        
    def update(self, dt):
        """Update the particle position and age."""
        # Update position
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt
        
        # Apply simple gravity if enabled
        if self.gravity:
            self.velocity.y += 30 * dt  # Gravity acceleration
            
        # Update age
        self.age += dt
        
        # Return True if the particle is still alive
        return self.age < self.lifetime
        
    def draw(self, surface):
        """Draw the particle with optional size and alpha based on age."""
        # Calculate alpha (transparency) based on age if fade is enabled
        if self.fade:
            # Fade out as the particle gets older
            alpha = 255 * (1 - self.age / self.lifetime)
            
            # Create a copy of the color with new alpha
            color_with_alpha = self.original_color
            # Only apply alpha if using a surface with per-pixel alpha
            if isinstance(surface, pygame.Surface) and surface.get_flags() & pygame.SRCALPHA:
                r, g, b = self.original_color
                color_with_alpha = (r, g, b, int(alpha))
        else:
            color_with_alpha = self.color
            
        # Draw the particle as a circle
        if self.size <= 1:
            surface.set_at((int(self.x), int(self.y)), color_with_alpha)
        else:
            pygame.draw.circle(surface, color_with_alpha, (int(self.x), int(self.y)), self.size)
            
# --- Particle System ---
class ParticleSystem:
    def __init__(self, max_particles=MAX_PARTICLES):
        """Initialize an empty particle system."""
        self.particles = []
        self.max_particles = max_particles
        
    def add_particle(self, particle):
        """Add a particle to the system, removing oldest if at capacity."""
        if len(self.particles) >= self.max_particles:
            # Remove the oldest particle if we're at capacity
            self.particles.pop(0)
        self.particles.append(particle)
        
    def emit_particles(self, x, y, color_range, count, velocity_range=None, 
                      size_range=None, lifetime_range=None, gravity=False, fade=True):
        """Emit multiple particles at once with randomized properties."""
        for _ in range(count):
            # Choose random color from the provided range
            color = random.choice(color_range) if isinstance(color_range, list) else color_range
            
            # Set up velocity
            vel_x, vel_y = 0, 0
            if velocity_range:
                vel_x = random.uniform(velocity_range[0][0], velocity_range[0][1])
                vel_y = random.uniform(velocity_range[1][0], velocity_range[1][1])
                
            # Set up size
            size = 2  # Default size
            if size_range:
                size = random.uniform(size_range[0], size_range[1])
                
            # Set up lifetime
            lifetime = PARTICLE_LIFETIME  # Default lifetime
            if lifetime_range:
                lifetime = random.uniform(lifetime_range[0], lifetime_range[1])
                
            # Create and add the particle
            particle = Particle(x, y, color, (vel_x, vel_y), size, lifetime, gravity, fade)
            self.add_particle(particle)
            
    def update(self, dt):
        """Update all particles, removing dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]
        
    def draw(self, surface):
        """Draw all particles to the surface."""
        for particle in self.particles:
            particle.draw(surface)

# --- Star Class ---
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.choice(STAR_SIZES)
        self.color = random.choice(STAR_COLORS)
        self.speed = random.choice(STAR_SPEEDS)
        
    def update(self, dt):
        # Move stars downward
        self.y += self.speed * dt
        
        # If star goes off-screen, reset it to the top
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# --- Background Menu Asteroid Class ---
class MenuAsteroid:
    def __init__(self):
        self.size = random.randint(20, 60)
        self.x = random.randint(-100, SCREEN_WIDTH + 100)
        self.y = random.randint(-100, SCREEN_HEIGHT + 100)
        self.vel_x = random.uniform(-30, 30)
        self.vel_y = random.uniform(-30, 30)
        self.rotation = 0
        self.rotation_speed = random.uniform(-50, 50)
        self.image = pygame.transform.scale(
            ASTEROID_IMGS[random.randint(0, 6)], 
            (self.size, self.size)
        )
        self.image.set_colorkey((0, 0, 0))  # Make background transparent
        
        # For particle effects
        self.asteroid_type = random.randint(0, 6)  # Random asteroid type
        self.radius = self.size // 2  # Radius for particle emission
        
    def update(self, dt):
        # Move asteroid
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Rotate asteroid
        self.rotation += self.rotation_speed * dt
        self.rotation %= 360
        
        # If asteroid goes off-screen, reset it from the opposite side
        if self.x < -self.size:
            self.x = SCREEN_WIDTH + self.size
        elif self.x > SCREEN_WIDTH + self.size:
            self.x = -self.size
            
        if self.y < -self.size:
            self.y = SCREEN_HEIGHT + self.size
        elif self.y > SCREEN_HEIGHT + self.size:
            self.y = -self.size
            
    def draw(self, surface):
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        # Get new rect after rotation
        rect = rotated_image.get_rect(center=(self.x, self.y))
        # Draw the rotated image
        surface.blit(rotated_image, rect.topleft)
        
    def emit_fire_particles(self):
        """Emit fire particles trailing behind the asteroid for menu animation."""
        # Create velocity vector from x and y components
        vel = Vector2(self.vel_x, self.vel_y)
        
        # If not moving, don't emit particles
        if vel.length() == 0:
            return
            
        # Normalized reverse of velocity for particle position
        back_dir = -vel.normalize()
        
        # Position slightly offset from the asteroid center in the opposite direction of movement
        offset_x = back_dir.x * (self.radius * 0.8)
        offset_y = back_dir.y * (self.radius * 0.8)
        
        # Add some random spread perpendicular to movement direction
        perp_dir = Vector2(-back_dir.y, back_dir.x)  # Perpendicular vector
        spread = random.uniform(-0.5, 0.5)
        offset_x += perp_dir.x * self.radius * spread
        offset_y += perp_dir.y * self.radius * spread
        
        # Emission position
        emit_x = self.x + offset_x
        emit_y = self.y + offset_y
        
        # Fire velocity is opposite of asteroid movement with some variation
        vel_base = -vel * 0.3  # 30% of asteroid speed in opposite direction
        vel_range = (
            (vel_base.x - 15, vel_base.x + 15),  # X velocity range
            (vel_base.y - 15, vel_base.y + 15)   # Y velocity range
        )
        
        # Particle size and count based on asteroid type
        particle_count = 3 + (self.asteroid_type // 2)  # 3-6 particles based on type
        size_multiplier = 0.6 + (self.asteroid_type * 0.1)  # Bigger for higher types
        size_base = 2 * size_multiplier
        size_range = (size_base * 0.6, size_base * 1.4)
        
        # Lifetime based on asteroid type (more dangerous = longer fire trails)
        lifetime_range = (0.2 + (self.asteroid_type * 0.05), 0.4 + (self.asteroid_type * 0.1))
        
        # Emit particles
        particle_system.emit_particles(
            emit_x, emit_y,
            ASTEROID_PARTICLE_COLORS,
            particle_count,
            vel_range,
            size_range,
            lifetime_range,
            gravity=False,
            fade=True
        )

# --- Menu Player Class ---
class MenuPlayer:
    def __init__(self):
        self.image = pygame.transform.scale(PLAYER_IMG, (PLAYER_SIZE, PLAYER_SIZE))
        self.image.set_colorkey((0, 0, 0))
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2 + 150
        self.angle = 0
        self.radius = 100
        self.speed = 30  # Degrees per second
        
    def update(self, dt):
        # Move in a circular path
        self.angle += self.speed * dt
        self.angle %= 360
        
        # Calculate position on the circle
        self.x = SCREEN_WIDTH // 2 + self.radius * math.cos(math.radians(self.angle))
        self.y = SCREEN_HEIGHT // 2 + 150 + self.radius * math.sin(math.radians(self.angle))
        
    def draw(self, surface):
        # Calculate angle for player to face the center of the circle
        rotation_angle = (self.angle + 90) % 360
        
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.image, -rotation_angle)
        # Get new rect after rotation
        rect = rotated_image.get_rect(center=(self.x, self.y))
        # Draw the rotated image
        surface.blit(rotated_image, rect.topleft)

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # Load and scale the player graphic
        self.image = pygame.transform.scale(PLAYER_IMG, (PLAYER_SIZE, PLAYER_SIZE))
        
        # Make the background transparent
        self.image.set_colorkey((0, 0, 0))
        
        # Create circular collision mask
        self.radius = PLAYER_SIZE // 2
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        
        # Store original image for animations
        self.original_image = self.image.copy()
        self.pos = Vector2(pos)
        self.velocity = Vector2(0, 0)  # Current velocity (for smooth movement)
        self.target_velocity = Vector2(0, 0)  # Target velocity
        self.acceleration = 1200  # Acceleration rate (pixels/second²)
        self.deceleration = 900   # Deceleration rate (pixels/second²)
        self.max_speed = PLAYER_SPEED
        
        # Thrust animation variables
        self.thrusting = False
        self.thrust_direction = Vector2(0, 0)
        self.particle_timer = 0
        self.particle_interval = 0.02  # Emit particles every 0.02 seconds
        
        # Initialize player health
        self.health = PLAYER_MAX_HEALTH
        # Add invulnerability timer for when player takes damage
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.0  # 1 second of invulnerability after hit
        self.flash_timer = 0
        self.is_flashing = False

    def update(self, dt, joystick=None): # Added joystick update logic
        # Handle player input and calculate target velocity
        keys = pygame.key.get_pressed()
        direction = Vector2(0, 0)

        # Keyboard input
        if keys[K_LEFT] or keys[K_a]:
            direction.x = -1
        if keys[K_RIGHT] or keys[K_d]:
            direction.x = 1
        if keys[K_UP] or keys[K_w]:
            direction.y = -1
        if keys[K_DOWN] or keys[K_s]:
            direction.y = 1

        # Joystick input (basic axis 0/1)
        if joystick:
            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)
            # Add a small deadzone
            if abs(axis_x) > 0.2:
                direction.x = axis_x
            if abs(axis_y) > 0.2:
                direction.y = axis_y

        # Normalize diagonal movement
        if direction.length() > 0:
            self.thrusting = True  # Player is actively thrusting
            self.thrust_direction = direction.normalize()
            self.target_velocity = self.thrust_direction * self.max_speed
        else:
            self.thrusting = False
            self.target_velocity = Vector2(0, 0)
            
        # Smooth movement with acceleration and deceleration
        if self.thrusting:
            # Accelerate toward target velocity
            if self.velocity.length() < self.target_velocity.length():
                accel_vector = self.thrust_direction * self.acceleration * dt
                self.velocity += accel_vector
                # Ensure we don't exceed the target velocity
                if self.velocity.length() > self.target_velocity.length():
                    self.velocity = self.target_velocity.copy()
        else:
            # Decelerate when not thrusting
            if self.velocity.length() > 0:
                # Calculate deceleration vector in the opposite direction of movement
                if self.velocity.length() > 0:  # Ensure we have a non-zero velocity
                    decel_dir = -self.velocity.normalize()
                    decel_amount = min(self.deceleration * dt, self.velocity.length())
                    self.velocity += decel_dir * decel_amount
                    
                    # Stop completely if velocity is very small
                    if self.velocity.length() < 10:
                        self.velocity = Vector2(0, 0)
        
        # Apply velocity to position
        self.pos += self.velocity * dt
        
        # Keep player on screen
        self.pos.x = max(PLAYER_SIZE // 2, min(SCREEN_WIDTH - PLAYER_SIZE // 2, self.pos.x))
        self.pos.y = max(PLAYER_SIZE // 2, min(SCREEN_HEIGHT - PLAYER_SIZE // 2, self.pos.y))

        self.rect.center = self.pos
        
        # Emit thruster particles if thrusting
        if self.thrusting:
            self.particle_timer += dt
            if self.particle_timer >= self.particle_interval:
                self.particle_timer = 0
                self.emit_thruster_particles()
        
        # Update invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer += dt
            if self.invulnerable_timer >= self.invulnerable_duration:
                self.invulnerable = False
                self.invulnerable_timer = 0
                # Restore original image when invulnerability ends
                self.image = self.original_image.copy()
            else:
                # Flash effect during invulnerability
                self.flash_timer += dt
                if self.flash_timer >= 0.1:  # Toggle flash every 0.1 seconds
                    self.flash_timer = 0
                    self.is_flashing = not self.is_flashing
                    
                    if self.is_flashing:
                        # Make player semi-transparent when flashing
                        self.image = self.original_image.copy()
                        self.image.set_alpha(128)
                    else:
                        # Restore normal visibility
                        self.image = self.original_image.copy()
    
    def take_damage(self, amount):
        """Reduce player health and trigger invulnerability."""
        if not self.invulnerable:
            self.health -= amount
            self.health = max(0, self.health)  # Don't go below 0
            self.invulnerable = True
            self.invulnerable_timer = 0
            self.flash_timer = 0
            self.is_flashing = True
            
            # Start flashing immediately
            self.image = self.original_image.copy()
            self.image.set_alpha(128)
            
            return True  # Damage was applied
        return False  # Player was invulnerable, no damage
        
    def emit_thruster_particles(self):
        """Emit thruster particles behind the player in the opposite direction of movement."""
        if not self.thrusting or self.thrust_direction.length() == 0:
            return
            
        # Reverse thrust direction to get the back of the ship
        back_dir = -self.thrust_direction
        
        # Calculate emission offset from the player's center
        offset_x = back_dir.x * (self.radius * 0.8)  # 80% of the player's radius
        offset_y = back_dir.y * (self.radius * 0.8)
        
        # Add some random spread perpendicular to the thrust direction
        perp_dir = Vector2(-back_dir.y, back_dir.x)  # Perpendicular vector
        spread_factor = 0.4
        offset_x += perp_dir.x * self.radius * random.uniform(-spread_factor, spread_factor)
        offset_y += perp_dir.y * self.radius * random.uniform(-spread_factor, spread_factor)
        
        # Emission position
        emit_x = self.pos.x + offset_x
        emit_y = self.pos.y + offset_y
        
        # Velocity is opposite of player movement but faster
        vel_magnitude = random.uniform(100, 200)  # Speed of particles
        vel_x = back_dir.x * vel_magnitude
        vel_y = back_dir.y * vel_magnitude
        
        # Add some random variation to velocity
        vel_variation = 30
        vel_range = (
            (vel_x - vel_variation, vel_x + vel_variation),
            (vel_y - vel_variation, vel_y + vel_variation)
        )
        
        # Size range for thruster particles
        size_range = (1.5, 3.5)
        
        # Lifetime range for thruster particles
        lifetime_range = (0.2, 0.4)
        
        # Number of particles to emit depends on speed
        particle_count = int(3 + (self.velocity.length() / self.max_speed) * 3)
        
        # Emit thruster particles
        particle_system.emit_particles(
            emit_x, emit_y,
            PLAYER_THRUSTER_COLORS,
            particle_count,
            vel_range,
            size_range,
            lifetime_range,
            gravity=False,
            fade=True
        )

# --- Helper Functions --- 
def weighted_random_choice(weights_dict):
    """
    Select a random key from a dictionary based on the weight values.
    
    Args:
        weights_dict: Dictionary with keys as options and values as weights.
        
    Returns:
        A randomly selected key based on the weights.
    """
    options = list(weights_dict.keys())
    weights = list(weights_dict.values())
    
    # Generate a random value based on the sum of weights
    total = sum(weights)
    rand_val = random.uniform(0, total)
    
    # Find the option that corresponds to the random value
    cumulative = 0
    for i, weight in enumerate(weights):
        cumulative += weight
        if rand_val <= cumulative:
            return options[i]
    
    # Fallback (shouldn't reach here unless weights sum to 0)
    return options[0] if options else None

# --- Asteroid Class ---
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # Select asteroid type based on weighted probability
        self.asteroid_type = weighted_random_choice(ASTEROID_TYPE_WEIGHTS)
        
        # Determine size category based on asteroid type restrictions
        allowed_sizes = ASTEROID_SIZE_RESTRICTIONS[self.asteroid_type]
        self.size_category = random.choice(allowed_sizes)
        size_range = ASTEROID_SIZES[self.size_category]
        
        # Random size within the category's range - now square (1:1 aspect ratio)
        size = random.randint(size_range["min"], size_range["max"])
        
        # Adjust speed based on size category
        base_speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        speed_multiplier = ASTEROID_SPEED_MULTIPLIERS[self.size_category]
        speed_magnitude = base_speed * speed_multiplier

        # Calculate damage based on type and size
        self.base_damage = ASTEROID_BASE_DAMAGE[self.asteroid_type]
        size_multiplier = ASTEROID_SIZE_DAMAGE_MULTIPLIERS[self.size_category]
        self.damage = int(self.base_damage * size_multiplier)

        # Choose spawn edge and set initial position/velocity
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        pos = Vector2(0, 0) # Initialize pos vector
        vel = Vector2(0, 0) # Initialize vel vector

        if edge == 'top':
            pos.x = random.randint(0, SCREEN_WIDTH)
            pos.y = -size / 2
            vel.x = random.uniform(-1, 1)
            vel.y = 1
        elif edge == 'bottom':
            pos.x = random.randint(0, SCREEN_WIDTH)
            pos.y = SCREEN_HEIGHT + size / 2
            vel.x = random.uniform(-1, 1)
            vel.y = -1
        elif edge == 'left':
            pos.x = -size / 2
            pos.y = random.randint(0, SCREEN_HEIGHT)
            vel.x = 1
            vel.y = random.uniform(-1, 1)
        else: # edge == 'right'
            pos.x = SCREEN_WIDTH + size / 2
            pos.y = random.randint(0, SCREEN_HEIGHT)
            vel.x = -1
            vel.y = random.uniform(-1, 1)

        # Normalize velocity and apply speed magnitude
        if vel.length() > 0:
            self.vel = vel.normalize() * speed_magnitude
        else: # Avoid zero vector if random rolls are both 0
            self.vel = Vector2(0, speed_magnitude) # Default downwards

        # Use the selected asteroid type image
        self.image = pygame.transform.smoothscale(ASTEROID_IMGS[self.asteroid_type], (size, size))
        
        # Make the background transparent
        self.image.set_colorkey((0, 0, 0))
        
        # Create circular collision mask
        self.radius = size // 2
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.original_image = self.image.copy()
        
        # Store precise position
        self.pos = Vector2(pos)
        
        # Store size category for future use (e.g., damage calculation)
        self.size_category = self.size_category
        
        # Rotation variables for asteroids
        self.angle = 0
        self.rotation_speed = random.uniform(-60, 60)  # Degrees per second
        
        # Particle emission variables
        self.particle_timer = 0
        self.particle_interval = 0.05  # Emit particles every 0.05 seconds
        
        # Higher asteroid types have more intense fire effects
        self.particle_count = min(3 + self.asteroid_type, 8)  # 3-8 particles per emission
        self.particle_size_multiplier = 0.6 + (self.asteroid_type * 0.1)  # Size increases with type
        
    def update(self, dt, joystick=None): # Added joystick=None to match Player signature
        # Update position
        self.pos += self.vel * dt
        
        # Rotate the asteroid
        self.angle += self.rotation_speed * dt
        self.angle %= 360
        
        # Apply rotation to image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Keep the same center point after rotation
        self.rect = self.image.get_rect(center=self.pos)
        
        # Emit fire particles behind the asteroid
        self.particle_timer += dt
        if self.particle_timer >= self.particle_interval:
            self.particle_timer = 0
            self.emit_fire_particles()
        
        # Remove asteroids that go far off-screen
        buffer = max(self.rect.width, self.rect.height) * 2
        if (self.rect.right < -buffer or
            self.rect.left > SCREEN_WIDTH + buffer or
            self.rect.bottom < -buffer or
            self.rect.top > SCREEN_HEIGHT + buffer):
            self.kill() # Remove sprite from all groups
            
    def emit_fire_particles(self):
        """Emit fire particles trailing behind the asteroid."""
        # Calculate position offset (opposite of velocity)
        if self.vel.length() == 0:
            return
            
        # Normalized reverse of velocity for particle position
        back_dir = -self.vel.normalize()
        
        # Position slightly offset from the asteroid center in the opposite direction of movement
        offset_x = back_dir.x * (self.radius * 0.8)
        offset_y = back_dir.y * (self.radius * 0.8)
        
        # Add some random spread perpendicular to movement direction
        perp_dir = Vector2(-back_dir.y, back_dir.x)  # Perpendicular vector
        spread = random.uniform(-0.5, 0.5)
        offset_x += perp_dir.x * self.radius * spread
        offset_y += perp_dir.y * self.radius * spread
        
        # Emission position
        emit_x = self.pos.x + offset_x
        emit_y = self.pos.y + offset_y
        
        # Fire velocity is opposite of asteroid movement with some variation
        vel_base = -self.vel * 0.3  # 30% of asteroid speed in opposite direction
        vel_range = (
            (vel_base.x - 15, vel_base.x + 15),  # X velocity range
            (vel_base.y - 15, vel_base.y + 15)   # Y velocity range
        )
        
        # Size based on asteroid type
        size_base = 2 * self.particle_size_multiplier
        size_range = (size_base * 0.6, size_base * 1.4)
        
        # Lifetime based on asteroid type (more dangerous = longer fire trails)
        lifetime_range = (0.2 + (self.asteroid_type * 0.05), 0.4 + (self.asteroid_type * 0.1))
        
        # Emit particles
        particle_system.emit_particles(
            emit_x, emit_y,
            ASTEROID_PARTICLE_COLORS,
            self.particle_count,
            vel_range,
            size_range,
            lifetime_range,
            gravity=False,
            fade=True
        )

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

# Create the particle system (moved up to be defined before any usage)
particle_system = ParticleSystem(max_particles=500)  # Increased for more particle effects

# --- Game Variables ---
# Create the Player sprite instance
player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_SIZE * 1.5))
all_sprites.add(player) # Add player to the 'all_sprites' group

score = 0
game_over = False
# Timer for asteroid spawning (uses seconds now)
asteroid_spawn_timer = 0.0
next_spawn_interval = random.uniform(ASTEROID_SPAWN_RATE * 0.5, ASTEROID_SPAWN_RATE * 1.5)

# --- Joystick Setup ---
joystick = None
joystick_count = pygame.joystick.get_count()
if joystick_count > 0:
    joystick = pygame.joystick.Joystick(0) # Use the first joystick
    joystick.init()
    print(f"Initialized Joystick: {joystick.get_name()}")
else:
    print("No joystick detected.")

# --- Game Functions ---
def reset_game():
    global score, game_over, asteroid_spawn_timer, next_spawn_interval, player, fade_alpha, transition_timer, stars, particle_system
    all_sprites.empty() # Clear all sprites
    asteroids.empty()   # Clear asteroids specifically
    score = 0
    game_over = False
    asteroid_spawn_timer = 0.0 # Reset spawn timer
    next_spawn_interval = random.uniform(ASTEROID_SPAWN_RATE * 0.5, ASTEROID_SPAWN_RATE * 1.5) # Reset spawn interval
    fade_alpha = 255
    transition_timer = 0
    
    # Clear particles
    particle_system = ParticleSystem(max_particles=500)

    # Recreate player and add to groups
    player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_SIZE * 1.5))
    all_sprites.add(player)
    
    # Create a new set of stars
    stars = [Star() for _ in range(NUM_STARS)]

def change_music(music_file, volume=0.5):
    """Change background music with cross-fade."""
    try:
        pygame.mixer.music.fadeout(MUSIC_FADE_DURATION)
        pygame.time.delay(MUSIC_FADE_DURATION // 2)  # Wait for half the fade out time
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=-1)
    except pygame.error as e:
        print(f"Error changing music: {e}")

def fade_in(surface, dt):
    """Fade screen in from black."""
    global fade_alpha, transition_timer
    
    transition_timer += dt
    fade_alpha = max(0, int(255 * (1 - transition_timer / FADE_DURATION)))
    
    if fade_alpha > 0:
        fade_surface.set_alpha(fade_alpha)
        surface.blit(fade_surface, (0, 0))
        
    return fade_alpha <= 0  # Return True when fade is complete

def fade_out(surface, dt):
    """Fade screen out to black."""
    global fade_alpha, transition_timer
    
    transition_timer += dt
    fade_alpha = min(255, int(255 * (transition_timer / FADE_DURATION)))
    
    if fade_alpha < 255:
        fade_surface.set_alpha(fade_alpha)
        surface.blit(fade_surface, (0, 0))
        
    return fade_alpha >= 255  # Return True when fade is complete

def update_stars(dt):
    """Update all stars."""
    for star in stars:
        star.update(dt)

def draw_stars():
    """Draw all stars."""
    for star in stars:
        star.draw(screen)

# --- Screen Functions ---
def show_start_screen():
    global menu_asteroids, menu_player, transition_timer, fade_alpha, particle_system
    
    # Initialize menu elements if they don't exist
    if 'menu_asteroids' not in globals():
        global menu_asteroids
        menu_asteroids = [MenuAsteroid() for _ in range(10)]
        
    if 'menu_player' not in globals():
        global menu_player
        menu_player = MenuPlayer()
    
    # Reset particle system
    particle_system = ParticleSystem(max_particles=500)
    
    # Change to menu music if not already playing
    if not hasattr(show_start_screen, 'music_started'):
        change_music(MENU_MUSIC)
        show_start_screen.music_started = True
    
    screen.fill(BACKGROUND_COLOR)
    
    # Draw stars
    draw_stars()
    
    # Update and draw menu asteroids
    for asteroid in menu_asteroids:
        asteroid.update(1/60)  # Assume 60 FPS for menu animation
        asteroid.draw(screen)
    
    # Update and draw menu player
    menu_player.update(1/60)
    menu_player.draw(screen)

    # --- Draw Logo --- #
    # Get logo rect and center it
    logo_rect = LOGO_IMG.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(LOGO_IMG, logo_rect)

    # --- Draw Instructions --- #
    # Render instruction text
    start_text_en = "Press any key or joystick button to start"
    start_surface = instruction_font.render(start_text_en, True, SCORE_COLOR)
    start_rect = start_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + logo_rect.height // 2)) # Position below logo

    screen.blit(start_surface, start_rect)
    
    # Handle fade
    if transition_timer < FADE_DURATION:
        fade_in(screen, 1/60)
    
    pygame.display.flip()

    waiting = True
    while waiting:
        dt = clock.tick(60) / 1000.0
        
        # Update stars
        update_stars(dt)
        
        # Update particles
        particle_system.update(dt)
        
        # Update menu animations and emit particles
        for asteroid in menu_asteroids:
            asteroid.update(dt)
            # Emit particles occasionally from menu asteroids
            if random.random() < 0.2:  # 20% chance each frame
                asteroid.emit_fire_particles()
                
        menu_player.update(dt)
        
        # Emit thruster particles from menu player too
        if random.random() < 0.3:  # 30% chance per frame
            # Calculate particle position behind player
            angle_rad = math.radians(menu_player.angle)
            back_x = menu_player.x - math.cos(angle_rad) * menu_player.radius * 0.7
            back_y = menu_player.y - math.sin(angle_rad) * menu_player.radius * 0.7
            
            # Emit thruster particles
            particle_system.emit_particles(
                back_x, back_y,
                PLAYER_THRUSTER_COLORS,
                3,  # Number of particles
                ((math.cos(angle_rad) * -50, math.cos(angle_rad) * -100),  # X velocity
                 (math.sin(angle_rad) * -50, math.sin(angle_rad) * -100)), # Y velocity
                (1.5, 3.0),  # Size range
                (0.3, 0.6),  # Lifetime range
                gravity=False,
                fade=True
            )
        
        # Redraw screen
        screen.fill(BACKGROUND_COLOR)
        draw_stars()
        
        # Draw particles first (behind everything)
        particle_system.draw(screen)
        
        for asteroid in menu_asteroids:
            asteroid.draw(screen)
        menu_player.draw(screen)
        
        # Redraw logo and instructions
        screen.blit(LOGO_IMG, logo_rect)
        screen.blit(start_surface, start_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
                # Begin transition to countdown
                fade_alpha = 0
                transition_timer = 0
                waiting = False

def show_countdown():
    """Show countdown before gameplay starts."""
    global transition_timer, fade_alpha, particle_system
    
    # Change to game music
    change_music(GAME_MUSIC)
    
    # Reset the particle system for a fresh start
    particle_system = ParticleSystem(max_particles=500)
    
    countdown_start_time = pygame.time.get_ticks() / 1000  # Current time in seconds
    
    # Initialize fade-in effect
    transition_timer = 0
    fade_alpha = 255
    
    counting = True
    while counting:
        dt = clock.tick(60) / 1000.0
        current_time = pygame.time.get_ticks() / 1000
        elapsed = current_time - countdown_start_time
        
        # Calculate current countdown number
        count_num = COUNTDOWN_DURATION - int(elapsed)
        
        if count_num <= 0:
            # Countdown finished
            counting = False
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Update stars
        update_stars(dt)
        
        # Update particle system
        particle_system.update(dt)
        
        # Clear screen
        screen.fill(BACKGROUND_COLOR)
        
        # Draw stars
        draw_stars()
        
        # Draw particles behind sprites
        particle_system.draw(screen)
        
        # Draw the countdown number
        if count_num > 0:
            count_text = str(count_num)
            count_surface = countdown_font.render(count_text, True, COUNTDOWN_COLOR)
            count_rect = count_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(count_surface, count_rect)
            
            # Draw "Get Ready!" text
            ready_text = "Get Ready!"
            ready_surface = instruction_font.render(ready_text, True, COUNTDOWN_COLOR)
            ready_rect = ready_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(ready_surface, ready_rect)
        
        # Handle fade effect
        if elapsed < FADE_DURATION:
            fade_in(screen, dt)
            
        pygame.display.flip()
    
    # Reset transition for the next state
    transition_timer = 0
    fade_alpha = 0

def show_game_over_screen(score):
    """Show the game over screen with score."""
    global transition_timer, fade_alpha, menu_asteroids, particle_system
    
    # Change to game over music
    change_music(GAME_OVER_MUSIC)
    
    # Initialize menu asteroids for animation
    menu_asteroids = [MenuAsteroid() for _ in range(10)]
    
    # Start with a fresh particle system
    particle_system = ParticleSystem(max_particles=500)
    
    # Start with a fade-in
    transition_timer = 0
    fade_alpha = 255
    
    screen.fill(BACKGROUND_COLOR)
    
    # Draw stars
    draw_stars()
    
    # Draw "Game Over" text
    game_over_text = "Game Over"
    game_over_surface = game_over_font.render(game_over_text, True, SCORE_COLOR)
    game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(game_over_surface, game_over_rect)
    
    # Draw death message
    death_text = "Your ship was destroyed!"
    death_surface = instruction_font.render(death_text, True, SCORE_COLOR)
    death_rect = death_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(death_surface, death_rect)
    
    # Draw final score
    score_text = f"Final Score: {int(score)}"
    score_surface = instruction_font.render(score_text, True, SCORE_COLOR)
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(score_surface, score_rect)
    
    # Draw restart instruction
    restart_text = "Press any key to play again"
    restart_surface = instruction_font.render(restart_text, True, SCORE_COLOR)
    restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
    screen.blit(restart_surface, restart_rect)
    
    # Apply fade effect
    fade_in(screen, 1/60)
    
    pygame.display.flip()
    
    # Wait for keypress to restart
    waiting = True
    while waiting:
        dt = clock.tick(60) / 1000.0
        
        # Update stars
        update_stars(dt)
        
        # Update particles
        particle_system.update(dt)
        
        # Update menu asteroids and emit particles
        for asteroid in menu_asteroids:
            asteroid.update(dt)
            # Emit particles occasionally
            if random.random() < 0.2:  # 20% chance each frame
                asteroid.emit_fire_particles()
        
        # Clear screen
        screen.fill(BACKGROUND_COLOR)
        
        # Draw stars
        draw_stars()
        
        # Draw particles
        particle_system.draw(screen)
        
        # Draw asteroids
        for asteroid in menu_asteroids:
            asteroid.draw(screen)
        
        # Redraw all text
        screen.blit(game_over_surface, game_over_rect)
        screen.blit(death_surface, death_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(restart_surface, restart_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Exit instead of just breaking the loop
            if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
                # Start transition to menu
                transition_timer = 0
                fade_alpha = 0
                waiting = False # Will transition back to PLAYING in main loop

def draw_health_bar(screen, health, max_health):
    """Draw the player's health bar in the corner of the screen."""
    # Position the health bar in the top left corner with a small margin
    x = 10
    y = SCREEN_HEIGHT - HEALTH_BAR_HEIGHT - 10
    
    # Calculate width of health portion
    health_width = int((health / max_health) * HEALTH_BAR_WIDTH)
    
    # Draw background
    pygame.draw.rect(screen, HEALTH_BAR_BACKGROUND_COLOR, 
                    (x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
    
    # Draw health portion
    pygame.draw.rect(screen, HEALTH_BAR_COLOR, 
                    (x, y, health_width, HEALTH_BAR_HEIGHT))
    
    # Draw border
    pygame.draw.rect(screen, HEALTH_BAR_BORDER_COLOR, 
                    (x - HEALTH_BAR_BORDER, y - HEALTH_BAR_BORDER, 
                     HEALTH_BAR_WIDTH + (HEALTH_BAR_BORDER * 2), 
                     HEALTH_BAR_HEIGHT + (HEALTH_BAR_BORDER * 2)), 
                    HEALTH_BAR_BORDER)
    
    # Draw text showing exact health value
    health_text = f"Health: {health}/{max_health}"
    health_surface = score_font.render(health_text, True, HEALTH_BAR_BORDER_COLOR)
    health_rect = health_surface.get_rect(midleft=(x + 10, y + HEALTH_BAR_HEIGHT // 2))
    screen.blit(health_surface, health_rect)

# Initialize stars
stars = [Star() for _ in range(NUM_STARS)]

# Initialize transition variables
transition_timer = 0
fade_alpha = 255

# --- Game Loop ---
running = True
game_state = START # Start in the START state

while running:
    # --- Delta Time Calculation ---
    dt = clock.tick(60) / 1000.0
    if dt > 0.1: # Prevent large dt spikes if lagging
        dt = 0.1

    # --- State Machine Logic ---
    if game_state == START:
        show_start_screen()
        reset_game() # Reset variables before starting countdown
        game_state = COUNTDOWN # Transition to countdown
    
    elif game_state == COUNTDOWN:
        show_countdown()
        game_state = PLAYING  # Transition to playing

    elif game_state == PLAYING:
        # --- Event Handling (for PLAYING state) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update stars
        update_stars(dt)
        
        # Update particle system
        particle_system.update(dt)
        
        # Update Sprites
        all_sprites.update(dt, joystick)

        # Asteroid Spawning
        asteroid_spawn_timer += dt
        if asteroid_spawn_timer >= next_spawn_interval:
            asteroid_spawn_timer = 0
            next_spawn_interval = random.uniform(ASTEROID_SPAWN_RATE * 0.5, ASTEROID_SPAWN_RATE * 1.5)
            new_asteroid = Asteroid()
            all_sprites.add(new_asteroid)
            asteroids.add(new_asteroid)

        # Collision Detection
        hits = pygame.sprite.spritecollide(player, asteroids, False, pygame.sprite.collide_circle)
        if hits and not player.invulnerable:
            for asteroid in hits:
                # Apply damage from asteroid
                damage_applied = player.take_damage(asteroid.damage)
                if damage_applied:
                    print(f"Hit by asteroid type {asteroid.asteroid_type} (size: {asteroid.size_category}), dealing {asteroid.damage} damage!")
                    # Check if player died
                    if player.health <= 0:
                        # Start transition to game over
                        transition_timer = 0
                        fade_alpha = 0
                        game_state = GAME_OVER
                    # Only apply damage from one asteroid if multiple hits in the same frame
                    break

        # Scoring
        score += dt * 10

        # Drawing (for PLAYING state)
        screen.fill(BACKGROUND_COLOR)
        
        # Draw stars
        draw_stars()
        
        # Draw particles behind sprites
        particle_system.draw(screen)
        
        # Draw all sprites
        all_sprites.draw(screen)

        # Render score (English)
        score_text_en = f"Score: {int(score)}"
        score_surface = score_font.render(score_text_en, True, SCORE_COLOR)
        screen.blit(score_surface, (10, 10))
        
        # Draw the health bar
        draw_health_bar(screen, player.health, PLAYER_MAX_HEALTH)

    elif game_state == GAME_OVER:
        show_game_over_screen(score)
        game_state = START # Go back to start screen after game over input

    # --- Update Display ---
    pygame.display.flip()

# --- Quit Pygame ---
pygame.quit()
sys.exit() 