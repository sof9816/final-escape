"""
Game state for Asteroid Navigator game.
"""
import pygame
import random
import math
from pygame.math import Vector2
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR,
    SCORE_FONT_SIZE, SCORE_COLOR, ASTEROID_SPAWN_RATE,
    HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, HEALTH_BAR_BORDER,
    HEALTH_BAR_COLOR, HEALTH_BAR_BACKGROUND_COLOR, HEALTH_BAR_BORDER_COLOR,
    PLAYER_MAX_HEALTH, FADE_DURATION, STATE_GAME_OVER,
    DIFFICULTY_SPAWN_RATE_MULTIPLIERS, DIFFICULTY_ASTEROID_VARIETY,
    DIFFICULTY_SIZE_RESTRICTIONS, INSTRUCTION_FONT_SIZE,
    # Power-up related constants
    POWERUP_TYPES, POWERUP_BOOM_ID, POWERUP_HEALTH_ID,
    SOUND_POWERUP_COLLECT,
    POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX, MAX_ACTIVE_POWERUPS,
    # Boom effect constants
    POWERUP_BOOM_EFFECT_RADIUS_FACTOR, POWERUP_BOOM_FLASH_DURATION, POWERUP_BOOM_FLASH_COLOR, 
    SOUND_EXPLOSION_MAIN, # Already imported by PowerUp, but good to have explicitly if GameState uses it directly
    SOUND_ASTEROID_EXPLODE, POWERUP_BOOM_CHAIN_EXPLOSIONS, POWERUP_BOOM_CHAIN_DELAY,
    ASTEROID_PARTICLE_COLORS # Import for asteroid destruction particles
)
from entities.player import Player
from entities.asteroid import Asteroid
from entities.powerup import PowerUp, PowerUpGroup # Import the new PowerUpGroup
from settings.settings_manager import SettingsManager

class GameState:
    """The main gameplay state."""
    
    def __init__(self, asset_loader, star_field, particle_system, screen_width=None, screen_height=None):
        """Initialize the game state.
        
        Args:
            asset_loader: AssetLoader instance for loading assets
            star_field: StarField instance for background stars
            particle_system: ParticleSystem instance for effects
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        self.asset_loader = asset_loader
        self.star_field = star_field
        self.particle_system = particle_system
        
        # Store screen dimensions
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        # Load settings
        self.settings_manager = SettingsManager()
        
        # Setup fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.powerups = PowerUpGroup() # Use our custom PowerUpGroup instead of pygame.sprite.Group
        
        # Create player
        # Ensure assets are loaded before creating the player if not already
        if self.asset_loader.assets is None:
            self.asset_loader.load_game_assets() # Should ideally be called once before state creation
        self.player = Player(
            (self.screen_width // 2, self.screen_height // 2), 
            self.asset_loader.assets["player_img"], # Pass the pre-loaded image
            particle_system
        )
        self.all_sprites.add(self.player)
        
        # Game variables
        self.score = 0
        self.asteroid_spawn_timer = 0
        self.next_spawn_interval = self._get_spawn_interval()
        
        # Transition variables
        self.transition_out = False
        self.fade_alpha = 0
        self.transition_timer = 0
        
        # Joystick (optional)
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            
        # Difficulty notification
        self.show_difficulty_message = True
        self.difficulty_message_timer = 3.0  # Display for 3 seconds

        # Boom Power-up effect state
        self.boom_effect_active = False
        self.boom_flash_timer = 0.0
        self.boom_center = None
        self.scheduled_sounds = [] # List of (sound_asset, delay_timer)
        
        # Independent power-up spawn timer
        self.powerup_spawn_timer = 0.0
        self.next_powerup_spawn_interval = self._get_next_powerup_spawn_interval()
            
    def reset(self):
        """Reset the game state for a new game."""
        # Always recreate the settings_manager to ensure we have the latest settings
        self.settings_manager = SettingsManager()
        
        # Get the most current settings
        current_difficulty = self.settings_manager.get_difficulty()
        
        # Store previous difficulty to check if it changed
        previous_difficulty = getattr(self, 'difficulty', None)
        
        # Update the instance variable
        self.difficulty = current_difficulty
        
        # Determine if the difficulty changed
        difficulty_changed = current_difficulty != previous_difficulty
        
        # Log for debugging
        print(f"Game reset: Difficulty is now {current_difficulty} (was {previous_difficulty})")
        
        # Clear sprite groups
        self.all_sprites.empty()
        self.asteroids.empty()
        self.powerups.empty() # Clear power-ups on reset
        
        # Create new player
        # Ensure assets are loaded
        if self.asset_loader.assets is None: # Should not happen if init loaded them
            self.asset_loader.load_game_assets()
        self.player = Player(
            (self.screen_width // 2, self.screen_height // 2), 
            self.asset_loader.assets["player_img"], # Pass the pre-loaded image
            self.particle_system # Pass the particle_system from GameState
        )
        self.all_sprites.add(self.player)
        
        # Reset game variables
        self.score = 0
        self.asteroid_spawn_timer = 0
        self.next_spawn_interval = self._get_spawn_interval()
        
        # Reset transition variables
        self.transition_out = False
        self.fade_alpha = 0
        self.transition_timer = 0
        
        # Reset independent powerup spawning
        self.powerup_spawn_timer = 0.0
        self.next_powerup_spawn_interval = self._get_next_powerup_spawn_interval()
        
        # Always show difficulty at game start
        self.show_difficulty_message = True
        self.difficulty_message_timer = 3.0

        # Reset Boom Power-up effect state
        self.boom_effect_active = False
        self.boom_flash_timer = 0.0
        self.boom_center = None
        self.scheduled_sounds = []
        
        # Create difficulty notification particles if difficulty changed
        if difficulty_changed:
            # Get difficulty-specific color
            difficulty_colors = {
                "Empty Space": (0, 255, 0),  # Green for easiest
                "Normal Space": (255, 255, 0),  # Yellow for normal
                "We did not agree on that": (255, 165, 0),  # Orange for medium
                "You kidding": (255, 100, 0),  # Dark orange for hard
                "Hell No!!!": (255, 0, 0)  # Red for hardest
            }
            color = difficulty_colors.get(self.difficulty, (255, 255, 255))
            
            # Create particle burst in the center of the screen
            if self.particle_system:
                center_x = self.screen_width // 2
                center_y = self.screen_height // 2
                
                # Create a starburst of particles
                for angle in range(0, 360, 10):
                    # Convert angle to radians
                    angle_rad = angle * (3.14159 / 180)
                    
                    # Calculate direction
                    dir_x = math.cos(angle_rad)
                    dir_y = math.sin(angle_rad)
                    
                    # Create velocity based on direction
                    speed = random.uniform(100, 150)
                    vel_x = dir_x * speed
                    vel_y = dir_y * speed
                    
                    # Create a particle
                    self.particle_system.emit_particles(
                        center_x, center_y,
                        [color],
                        count=1,
                        velocity_range=((vel_x*0.9, vel_x*1.1), (vel_y*0.9, vel_y*1.1)),
                        size_range=(3, 5),
                        lifetime_range=(1.0, 1.5),
                        fade=True
                    )
    
    def _get_spawn_interval(self):
        """Calculate spawn interval based on difficulty.
        
        Returns:
            float: Spawn interval in seconds
        """
        # Always get the latest difficulty setting
        current_difficulty = self.settings_manager.get_difficulty()
        spawn_rate_multiplier = DIFFICULTY_SPAWN_RATE_MULTIPLIERS.get(current_difficulty, 1.0)
        base_interval = ASTEROID_SPAWN_RATE / spawn_rate_multiplier
        return random.uniform(base_interval * 0.8, base_interval * 1.2)
    
    def _get_next_powerup_spawn_interval(self):
        """Calculate the next interval for an independent power-up spawn attempt."""
        # Return to normal spawn intervals
        return random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)
    
    def _choose_asteroid_type(self):
        """Choose an asteroid type based on difficulty.
        
        Returns:
            tuple: (type_id, size_category)
        """
        # Always get the latest difficulty setting
        current_difficulty = self.settings_manager.get_difficulty()
        # Get the weights for the current difficulty
        weights = DIFFICULTY_ASTEROID_VARIETY.get(current_difficulty, DIFFICULTY_ASTEROID_VARIETY["Normal Space"])
        
        # Create a list of types with their weights
        weighted_types = []
        for type_id, weight in weights.items():
            weighted_types.extend([type_id] * weight)
        
        # Choose a random type from the weighted list
        type_id = random.choice(weighted_types)
        
        # Choose a size based on the allowed sizes for this type and difficulty
        allowed_sizes = DIFFICULTY_SIZE_RESTRICTIONS.get(
            current_difficulty, DIFFICULTY_SIZE_RESTRICTIONS["Normal Space"]
        ).get(type_id, ["small"])
        
        size_category = random.choice(allowed_sizes)
        
        return type_id, size_category
        
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            String with next state name if transitioning, None otherwise
        """
        # No specific event handling needed for gameplay
        # Player input is handled in the update method
        return None
        
    def update(self, dt):
        """Update the game state.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            String with next state name if transitioning, None otherwise
        """
        # Skip updates if transitioning out
        if self.transition_out:
            self.transition_timer += dt
            self.fade_alpha = min(255, int(255 * (self.transition_timer / FADE_DURATION)))
            
            if self.transition_timer >= FADE_DURATION:
                return STATE_GAME_OVER
            return None # Return early if transitioning

        # Handle Boom Effect Logic (before other updates if it affects them)
        if self.boom_effect_active:
            # This flag is set by PowerUp.activate(), effect processing starts here
            if self.boom_center: # Ensure boom_center was set
                explosion_radius = min(self.screen_width, self.screen_height) * POWERUP_BOOM_EFFECT_RADIUS_FACTOR
                asteroids_destroyed_count = 0
                
                for asteroid in list(self.asteroids): # Iterate over a copy for safe removal
                    distance = self.boom_center.distance_to(asteroid.position)
                    if distance < explosion_radius + asteroid.radius: # Consider asteroid's own radius
                        # Create particle explosion for this asteroid
                        if self.particle_system:
                            self.particle_system.emit_particles(
                                asteroid.rect.centerx, asteroid.rect.centery,
                                ASTEROID_PARTICLE_COLORS, # Use imported constant
                                count=random.randint(15, 25), # More particles for explosion
                                velocity_range=((-200, 200), (-200, 200)), # Wider spread
                                size_range=(2, 5),
                                lifetime_range=(0.5, 1.0),
                                fade=True
                            )
                        asteroid.kill() # Remove asteroid
                        asteroids_destroyed_count += 1
                        self.score += 50 # Bonus score for power-up destruction

                # Schedule chained/delayed explosion sounds
                num_sounds_to_play = min(asteroids_destroyed_count, POWERUP_BOOM_CHAIN_EXPLOSIONS)
                sound_asset = self.asset_loader.assets["sounds"].get("asteroid_explode")
                if sound_asset:
                    for i in range(num_sounds_to_play):
                        self.scheduled_sounds.append((sound_asset, i * POWERUP_BOOM_CHAIN_DELAY))
                
                self.boom_center = None # Consume the boom center, effect applied
            self.boom_effect_active = False # Reset active flag, flash timer will handle visuals

        # Process scheduled sounds
        if self.scheduled_sounds:
            for i in range(len(self.scheduled_sounds) - 1, -1, -1): # Iterate backwards for safe removal
                sound_asset, delay = self.scheduled_sounds[i]
                delay -= dt
                if delay <= 0:
                    sound_asset.play()
                    self.scheduled_sounds.pop(i)
                else:
                    self.scheduled_sounds[i] = (sound_asset, delay)

        # Update flash timer (even if effect_active was reset, flash continues)
        if self.boom_flash_timer > 0:
            self.boom_flash_timer -= dt
            if self.boom_flash_timer < 0:
                self.boom_flash_timer = 0
        
        # Update stars
        self.star_field.update(dt)
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Update all sprites
        self.all_sprites.update(dt, self.joystick)
        
        # Asteroid spawning
        self.asteroid_spawn_timer += dt
        if self.asteroid_spawn_timer >= self.next_spawn_interval:
            self.asteroid_spawn_timer = 0
            self.next_spawn_interval = self._get_spawn_interval()
            current_difficulty = self.settings_manager.get_difficulty()

            # Spawn an asteroid (power-up spawning is now separate)
            type_id, size_category = self._choose_asteroid_type()
            new_asteroid = Asteroid(
                self.particle_system, 
                self.asset_loader,
                type_id=type_id,
                size_category=size_category,
                difficulty=current_difficulty,
                screen_width=self.screen_width,
                screen_height=self.screen_height
            )
            self.all_sprites.add(new_asteroid)
            self.asteroids.add(new_asteroid)

        # Independent Power-up spawning
        self.powerup_spawn_timer += dt
        if self.powerup_spawn_timer >= self.next_powerup_spawn_interval:
            self.powerup_spawn_timer = 0  # Reset timer
            self.next_powerup_spawn_interval = self._get_next_powerup_spawn_interval()
            if len(self.powerups) < MAX_ACTIVE_POWERUPS:
                self.spawn_powerup() 
            else:
                print(f"Max active powerups ({MAX_ACTIVE_POWERUPS}) reached. Skipping spawn.")

        # Collision detection for asteroids
        asteroid_hits = pygame.sprite.spritecollide(self.player, self.asteroids, False, pygame.sprite.collide_circle)
        for asteroid in asteroid_hits:
            if not self.player.invulnerable:
                damage_applied = self.player.take_damage(asteroid.damage)
                if damage_applied:
                    if self.player.health <= 0:
                        self.transition_out = True
                        self.transition_timer = 0
                        break
        
        # Use our new check_powerup_collisions method
        self.check_powerup_collisions()
        
        # Update score based on time survived
        self.score += dt * 10
        
        # Update difficulty message timer
        if self.show_difficulty_message:
            self.difficulty_message_timer -= dt
            if self.difficulty_message_timer <= 0:
                self.show_difficulty_message = False
        
        return None
            
    def draw(self, surface):
        """Draw the game state.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Clear screen
        surface.fill(BACKGROUND_COLOR)
        
        # Draw stars
        self.star_field.draw(surface)
        
        # Draw particles
        self.particle_system.draw(surface)
        
        # Check for powerups that need to emit particles
        for powerup in self.powerups:
            if hasattr(powerup, 'emit_particles') and powerup.emit_particles:
                powerup.emit_particles = False  # Reset the flag
                self.particle_system.emit_particles(
                    powerup.position.x, powerup.position.y,
                    powerup.particle_colors,
                    count=5,
                    velocity_range=((-40, 40), (-40, 40)),
                    size_range=(1, 2),
                    lifetime_range=(0.3, 0.6),
                    fade=True
                )
        
        # Draw all sprites except powerups
        sprites_without_powerups = [sprite for sprite in self.all_sprites.sprites() 
                                  if sprite not in self.powerups.sprites()]
        for sprite in sprites_without_powerups:
            surface.blit(sprite.image, sprite.rect)
            
        # Draw powerups with custom drawing
        self.powerups.draw(surface)
        
        # Draw score
        score_text = f"Score: {int(self.score)}"
        score_surface = self.score_font.render(score_text, True, SCORE_COLOR)
        surface.blit(score_surface, (10, 10))
        
        # Get current difficulty
        current_difficulty = self.settings_manager.get_difficulty()
        
        # Draw difficulty with color coding
        difficulty_colors = {
            "Empty Space": (0, 255, 0),  # Green for easiest
            "Normal Space": (255, 255, 0),  # Yellow for normal
            "We did not agree on that": (255, 165, 0),  # Orange for medium
            "You kidding": (255, 100, 0),  # Dark orange for hard
            "Hell No!!!": (255, 0, 0)  # Red for hardest
        }
        difficulty_color = difficulty_colors.get(current_difficulty, SCORE_COLOR)
        
        difficulty_text = f"Difficulty: {current_difficulty}"
        difficulty_surface = self.score_font.render(difficulty_text, True, difficulty_color)
        difficulty_rect = difficulty_surface.get_rect(topright=(self.screen_width - 10, 10))
        
        # Add a subtle background for better visibility
        bg_rect = difficulty_rect.inflate(20, 10)
        bg_rect.topright = (self.screen_width - 5, 5)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 128))  # Semi-transparent black
        surface.blit(bg_surface, bg_rect)
        
        # Draw the difficulty text
        surface.blit(difficulty_surface, difficulty_rect)
        
        # Draw health bar
        self.draw_health_bar(surface)
        
        # Draw fade overlay for transition
        if self.transition_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            surface.blit(fade_surface, (0, 0))
            
        # Draw boom flash effect if active
        if self.boom_flash_timer > 0:
            flash_alpha = 255 * (self.boom_flash_timer / POWERUP_BOOM_FLASH_DURATION)
            flash_alpha = min(255, max(0, int(flash_alpha))) # Clamp between 0-255
            
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.fill(POWERUP_BOOM_FLASH_COLOR)
            flash_surface.set_alpha(flash_alpha)
            surface.blit(flash_surface, (0,0))

        # Draw difficulty notification
        if self.show_difficulty_message:
            # Calculate alpha (fade out towards the end)
            alpha = min(255, int(255 * (self.difficulty_message_timer / 0.5))) if self.difficulty_message_timer < 0.5 else 255
            
            # Get current difficulty
            current_difficulty = self.settings_manager.get_difficulty()
            
            # Difficulty-specific color
            difficulty_colors = {
                "Empty Space": (0, 255, 0),  # Green for easiest
                "Normal Space": (255, 255, 0),  # Yellow for normal
                "We did not agree on that": (255, 165, 0),  # Orange for medium
                "You kidding": (255, 100, 0),  # Dark orange for hard
                "Hell No!!!": (255, 0, 0)  # Red for hardest
            }
            color = difficulty_colors.get(current_difficulty, (255, 255, 255))
            
            # Create message
            message = f"Difficulty: {current_difficulty}"
            message_surface = self.message_font.render(message, True, color)
            message_rect = message_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            
            # Create a background for better visibility
            bg_rect = message_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, int(200 * (alpha / 255))))  # Semi-transparent black with fade
            
            # Apply alpha to message
            message_surface.set_alpha(alpha)
            
            # Draw both
            surface.blit(bg_surface, bg_rect)
            surface.blit(message_surface, message_rect)
            
            # Add a subtitle based on difficulty
            difficulty_descriptions = {
                "Empty Space": "Relaxed navigation mode",
                "Normal Space": "Standard asteroid density",
                "We did not agree on that": "Increased hazards ahead!",
                "You kidding": "Seriously dangerous conditions!",
                "Hell No!!!": "Virtually unsurvivable!"
            }
            
            subtitle = difficulty_descriptions.get(current_difficulty, "")
            if subtitle:
                subtitle_surface = self.message_font.render(subtitle, True, color)
                subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, message_rect.bottom + 10))
                
                # Apply alpha
                subtitle_surface.set_alpha(alpha)
                
                # Draw
                surface.blit(subtitle_surface, subtitle_rect)
            
    def draw_health_bar(self, surface):
        """Draw the player's health bar.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Position the health bar in the top left corner with a small margin
        x = 10
        y = self.screen_height - HEALTH_BAR_HEIGHT - 10
        
        # Calculate width of health portion
        health_width = int((self.player.health / PLAYER_MAX_HEALTH) * HEALTH_BAR_WIDTH)
        
        # Draw background
        pygame.draw.rect(surface, HEALTH_BAR_BACKGROUND_COLOR, 
                        (x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        
        # Draw health portion
        pygame.draw.rect(surface, HEALTH_BAR_COLOR, 
                        (x, y, health_width, HEALTH_BAR_HEIGHT))
        
        # Draw border
        pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, 
                        (x - HEALTH_BAR_BORDER, y - HEALTH_BAR_BORDER, 
                         HEALTH_BAR_WIDTH + (HEALTH_BAR_BORDER * 2), 
                         HEALTH_BAR_HEIGHT + (HEALTH_BAR_BORDER * 2)), 
                        HEALTH_BAR_BORDER)
        
        # Draw text showing exact health value
        health_text = f"Health: {int(self.player.health)}/{PLAYER_MAX_HEALTH}"
        health_surface = self.score_font.render(health_text, True, HEALTH_BAR_BORDER_COLOR)
        health_rect = health_surface.get_rect(midleft=(x + 10, y + HEALTH_BAR_HEIGHT // 2))
        surface.blit(health_surface, health_rect)

    def spawn_powerup(self):
        """Attempt to spawn a power-up in the game."""
        # Use direct probability distribution for more controlled spawning
        power_type_roll = random.random()
        
        # 25% chance of BOOM power-up
        if power_type_roll < 0.25:
            powerup_type_id = POWERUP_BOOM_ID
        else:
            # 75% chance of health power-up, distributed among different amounts
            health_roll = random.random()
            
            if health_roll < 0.6:  # 60% of health (or 45% of all) is 25% health
                powerup_type_id = f"{POWERUP_HEALTH_ID}_25"
            elif health_roll < 0.9:  # 30% of health (or 22.5% of all) is 50% health
                powerup_type_id = f"{POWERUP_HEALTH_ID}_50"
            else:  # 10% of health (or 7.5% of all) is 100% health
                powerup_type_id = f"{POWERUP_HEALTH_ID}_100"
        
        details = POWERUP_TYPES[powerup_type_id]
        # Compute a random position just outside the screen to drift in
        edge = random.choice(["top", "left", "right"])
        if edge == "top":
            x = random.randint(50, self.screen_width - 50)
            y = -50
        elif edge == "left":
            x = -50
            y = random.randint(50, self.screen_height // 2)
        else:  # right
            x = self.screen_width + 50
            y = random.randint(50, self.screen_height // 2)

        powerup_img = self.asset_loader.assets["powerup_imgs"].get(powerup_type_id)
        if powerup_img is None:
            print(f"[ERROR] Image for {powerup_type_id} not found in powerup_imgs")
            return

        amount = details.get("amount") if powerup_type_id.startswith(POWERUP_HEALTH_ID) else None
        new_powerup = PowerUp(
            (x, y),
            powerup_type_id,
            powerup_img,
            self.screen_width,
            self.screen_height,
            amount=amount
        )
        self.all_sprites.add(new_powerup)
        self.powerups.add(new_powerup)
        # Create spawn particles for the powerup
        self.create_powerup_particles(new_powerup.position, 'spawn')

    def check_powerup_collisions(self):
        """Check if the player has collected any power-ups and activate them."""
        # Check for collisions with power-ups
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True, pygame.sprite.collide_circle)
        
        # Process each collected power-up
        for powerup in powerup_hits:
            # Create collection particles before activating (which removes the powerup)
            self.create_powerup_particles(powerup.position, 'collect')
            
            # Activate the power-up effect (each power-up knows what to do)
            powerup.activate(self)
            
            # Play collection sound
            if self.asset_loader.assets["sounds"]["powerup_collect"]:
                self.asset_loader.assets["sounds"]["powerup_collect"].play()

    def create_powerup_particles(self, position, effect_type):
        """Create particles for powerup spawn or collection effects.
        
        Args:
            position (Vector2): Position to create particles
            effect_type (str): Either 'spawn' or 'collect'
        """
        if effect_type == 'spawn':
            # Spawn effect: Gentle outward particles with blue/white colors
            colors = [
                (100, 200, 255),  # Light blue
                (150, 220, 255),  # Lighter blue
                (200, 240, 255),  # Almost white blue
                (255, 255, 255)   # White
            ]
            
            # Emit fewer particles for spawn (subtle effect)
            self.particle_system.emit_particles(
                position.x, position.y,
                colors,
                count=15,
                velocity_range=((-60, 60), (-60, 60)),
                size_range=(1, 3),
                lifetime_range=(0.6, 1.2),
                fade=True
            )
        
        elif effect_type == 'collect':
            # Collection effect: More energetic particles with bright white/yellow colors
            colors = [
                (255, 255, 200),  # Very light yellow
                (255, 255, 150),  # Light yellow
                (255, 255, 100),  # Yellow
                (255, 255, 50),   # Bright yellow
                (255, 255, 255)   # White
            ]
            
            # Emit more particles for collection (prominent effect)
            self.particle_system.emit_particles(
                position.x, position.y,
                colors,
                count=30,
                velocity_range=((-100, 100), (-100, 100)),
                size_range=(1, 4),
                lifetime_range=(0.5, 1.0),
                fade=True
            ) 