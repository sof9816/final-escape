import pygame
import sys
import random
import os # Import os for path joining
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
PLAYING = 1
GAME_OVER = 2

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

# Load background music *AFTER* mixer init
# Start music ONCE and let it loop
try:
    music_path = os.path.join("assets", "sound", "ost.ogg")
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5) # Adjust volume (0.0 to 1.0)
    pygame.mixer.music.play(loops=-1) # Play indefinitely from the start
except pygame.error as e:
    print(f"Error loading or playing music: {e}")

clock = pygame.time.Clock()

# --- Font Loading ---
# Use default fonts directly
default_font_path = None # Use pygame default
score_font = pygame.font.Font(default_font_path, SCORE_FONT_SIZE)
game_over_font = pygame.font.Font(default_font_path, GAME_OVER_FONT_SIZE)
title_font = pygame.font.Font(default_font_path, TITLE_FONT_SIZE)
instruction_font = pygame.font.Font(default_font_path, INSTRUCTION_FONT_SIZE)

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
        self.speed = PLAYER_SPEED
        
        # Initialize player health
        self.health = PLAYER_MAX_HEALTH
        # Add invulnerability timer for when player takes damage
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.0  # 1 second of invulnerability after hit
        self.flash_timer = 0
        self.is_flashing = False

    def update(self, dt, joystick=None): # Added joystick update logic
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

        # Normalize diagonal movement and apply speed * dt
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt

        # Keep player on screen
        self.pos.x = max(PLAYER_SIZE // 2, min(SCREEN_WIDTH - PLAYER_SIZE // 2, self.pos.x))
        self.pos.y = max(PLAYER_SIZE // 2, min(SCREEN_HEIGHT - PLAYER_SIZE // 2, self.pos.y))

        self.rect.center = self.pos
        
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

    def update(self, dt, joystick=None): # Added joystick=None to match Player signature
        self.pos += self.vel * dt
        self.rect.center = self.pos # Update rect center from pos

        # Remove asteroids that go far off-screen
        buffer = max(self.rect.width, self.rect.height) * 2
        if (self.rect.right < -buffer or
            self.rect.left > SCREEN_WIDTH + buffer or
            self.rect.bottom < -buffer or
            self.rect.top > SCREEN_HEIGHT + buffer):
            self.kill() # Remove sprite from all groups

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

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
    global score, game_over, asteroid_spawn_timer, next_spawn_interval, player
    all_sprites.empty() # Clear all sprites
    asteroids.empty()   # Clear asteroids specifically
    score = 0
    game_over = False
    asteroid_spawn_timer = 0.0 # Reset spawn timer
    next_spawn_interval = random.uniform(ASTEROID_SPAWN_RATE * 0.5, ASTEROID_SPAWN_RATE * 1.5) # Reset spawn interval

    # Recreate player and add to groups
    player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_SIZE * 1.5))
    all_sprites.add(player)
    # Music restart removed - it plays continuously now
    # try:
    #     pygame.mixer.music.play(loops=-1)
    # except pygame.error as e:
    #     print(f"Error restarting music: {e}")

# --- Screen Functions ---
def show_start_screen():
    screen.fill(BACKGROUND_COLOR)

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
    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(60) # Keep clock ticking
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Exit directly if quit from start screen
            if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
                waiting = False # Exit waiting loop to start game

def show_game_over_screen(score):
    """Show the game over screen with score."""
    screen.fill(BACKGROUND_COLOR)
    
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
    
    pygame.display.flip()
    
    # Wait for keypress to restart
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Exit instead of just breaking the loop
            if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
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
        reset_game() # Reset variables before starting to play
        game_state = PLAYING # Transition to playing

    elif game_state == PLAYING:
        # --- Event Handling (for PLAYING state) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle restart logic directly here (Removed - handled in GAME_OVER state)
            # if game_over:
            #     if event.type == KEYDOWN:
            #         reset_game()
            #     if event.type == JOYBUTTONDOWN:
            #          if event.button == 0: # Check for button 0 specifically
            #              reset_game()

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
                        game_state = GAME_OVER
                    # Only apply damage from one asteroid if multiple hits in the same frame
                    break

        # Scoring
        score += dt * 10

        # Drawing (for PLAYING state)
        screen.fill(BACKGROUND_COLOR)
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

    # --- Update Display (Common for all states if drawing happens in state funcs) ---
    # This is handled within the show_ functions and the PLAYING state drawing block
    # If needed, can have a final flip here, but current structure handles it.
    pygame.display.flip()

# --- Quit Pygame ---
pygame.quit()
sys.exit() 