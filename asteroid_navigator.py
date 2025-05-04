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
PLAYER_SIZE = 40 # Keep for now, image will be scaled to this
PLAYER_SPEED = 300 # Pixels per second
ASTEROID_MIN_SIZE = 15
ASTEROID_MAX_SIZE = 50 # Reverted
ASTEROID_MIN_SPEED = 50  # Pixels per second # Reverted
ASTEROID_MAX_SPEED = 200 # Pixels per second # Reverted
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
    ASTEROID_IMG = pygame.image.load(os.path.join("assets", "images", "asteroid.png")).convert_alpha()
    LOGO_IMG = pygame.image.load(os.path.join("assets", "images", "logo.png")).convert_alpha() # Load logo
except pygame.error as e:
    print(f"Error loading image: {e}")
    # Optionally, create fallback surfaces if images fail to load
    PLAYER_IMG = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
    PLAYER_IMG.fill((0, 255, 0)) # Green fallback
    ASTEROID_IMG = pygame.Surface((ASTEROID_MAX_SIZE, ASTEROID_MAX_SIZE)) # Create a surface large enough
    ASTEROID_IMG.set_colorkey((0,0,0))
    pygame.draw.ellipse(ASTEROID_IMG, (128, 128, 128), (0, 0, ASTEROID_MAX_SIZE, ASTEROID_MAX_SIZE)) # Grey fallback

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
        border_thickness = 2 # Adjust border thickness if needed

        # Load and scale the player graphic first
        # Scale to fit inside the border
        graphic_size = PLAYER_SIZE - border_thickness * 2
        player_graphic = pygame.transform.scale(PLAYER_IMG, (graphic_size, graphic_size))

        # Create the surface with final player size
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((0, 0, 0)) # Black background

        # Draw the white border
        border_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        pygame.draw.rect(self.image, (255, 255, 255), border_rect, border_thickness)

        # Blit the player graphic onto the black background, offset by border
        graphic_rect = player_graphic.get_rect(center=(PLAYER_SIZE // 2, PLAYER_SIZE // 2))
        self.image.blit(player_graphic, graphic_rect.topleft)

        # Use this combined surface as the sprite's image
        self.original_image = self.image.copy() # Keep original if needed later
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.speed = PLAYER_SPEED

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

# --- Asteroid Class ---
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Random size now determines the height
        height = random.randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)
        width = height * 2 # Enforce 2:1 aspect ratio

        speed_magnitude = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)

        # Choose spawn edge and set initial position/velocity (adjust for width/height)
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        pos = Vector2(0, 0) # Initialize pos vector
        vel = Vector2(0, 0) # Initialize vel vector

        if edge == 'top':
            pos.x = random.randint(0, SCREEN_WIDTH) # Position based on screen width
            pos.y = -height / 2 # Adjust for height
            vel.x = random.uniform(-1, 1)
            vel.y = 1
        elif edge == 'bottom':
            pos.x = random.randint(0, SCREEN_WIDTH)
            pos.y = SCREEN_HEIGHT + height / 2 # Adjust for height
            vel.x = random.uniform(-1, 1)
            vel.y = -1
        elif edge == 'left':
            pos.x = -width / 2 # Adjust for width
            pos.y = random.randint(0, SCREEN_HEIGHT) # Position based on screen height
            vel.x = 1
            vel.y = random.uniform(-1, 1)
        else: # edge == 'right'
            pos.x = SCREEN_WIDTH + width / 2 # Adjust for width
            pos.y = random.randint(0, SCREEN_HEIGHT)
            vel.x = -1
            vel.y = random.uniform(-1, 1)

        # Normalize velocity and apply speed magnitude
        if vel.length() > 0:
            self.vel = vel.normalize() * speed_magnitude
        else: # Avoid zero vector if random rolls are both 0
            self.vel = Vector2(0, speed_magnitude) # Default downwards

        # Scale the loaded asteroid graphic to the calculated width and height
        asteroid_graphic = pygame.transform.smoothscale(ASTEROID_IMG, (width, height))

        # Create a red background surface
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0)) # Red background

        # Blit the asteroid graphic onto the red background
        self.image.blit(asteroid_graphic, (0, 0))

        self.original_image = self.image.copy()

        self.rect = self.image.get_rect(center=pos) # Use pos vector for center
        # Store precise position
        self.pos = Vector2(pos) # Use pos vector

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

def show_game_over_screen(current_score):
    screen.fill(BACKGROUND_COLOR)

    # Render GAME OVER text (English)
    game_over_text_en = "GAME OVER"
    game_over_surface = game_over_font.render(game_over_text_en, True, (255, 0, 0)) # Red
    game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

    # Render Final Score text (English)
    final_score_text = f"Final Score: {int(current_score)}"
    score_surface = score_font.render(final_score_text, True, SCORE_COLOR)
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Render Restart instruction text (English)
    restart_text_en = "Press any key or joystick button to restart"
    restart_surface = instruction_font.render(restart_text_en, True, SCORE_COLOR)
    restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))

    screen.blit(game_over_surface, game_over_rect)
    screen.blit(score_surface, score_rect)
    screen.blit(restart_surface, restart_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(60) # Keep clock ticking
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Exit directly if quit from game over screen
            if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
                waiting = False # Will transition back to PLAYING in main loop

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
        hits = pygame.sprite.spritecollide(player, asteroids, False, pygame.sprite.collide_mask)
        if hits:
            game_state = GAME_OVER # Change state on collision
            # Music stop removed - keep playing
            # try:
            #     pygame.mixer.music.stop()
            # except pygame.error as e:
            #     print(f"Error stopping music: {e}")

        # Scoring
        score += dt * 10

        # Drawing (for PLAYING state)
        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)

        # Render score (English)
        score_text_en = f"Score: {int(score)}"
        score_surface = score_font.render(score_text_en, True, SCORE_COLOR)
        screen.blit(score_surface, (10, 10))

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