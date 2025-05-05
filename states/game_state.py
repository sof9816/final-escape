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
    DIFFICULTY_SIZE_RESTRICTIONS, INSTRUCTION_FONT_SIZE
)
from entities.player import Player
from entities.asteroid import Asteroid
from settings.settings_manager import SettingsManager

class GameState:
    """The main gameplay state."""
    
    def __init__(self, asset_loader, star_field, particle_system):
        """Initialize the game state.
        
        Args:
            asset_loader: AssetLoader instance for loading assets
            star_field: StarField instance for background stars
            particle_system: ParticleSystem instance for effects
        """
        self.asset_loader = asset_loader
        self.star_field = star_field
        self.particle_system = particle_system
        
        # Load settings
        self.settings_manager = SettingsManager()
        self.difficulty = self.settings_manager.get_difficulty()
        
        # Setup fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        
        # Create player
        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), particle_system, asset_loader)
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
            
    def reset(self):
        """Reset the game state for a new game."""
        # Load settings again (in case they were changed)
        new_difficulty = self.settings_manager.get_difficulty()
        difficulty_changed = new_difficulty != self.difficulty
        self.difficulty = new_difficulty
        
        # Clear sprite groups
        self.all_sprites.empty()
        self.asteroids.empty()
        
        # Create new player
        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.particle_system, self.asset_loader)
        self.all_sprites.add(self.player)
        
        # Reset game variables
        self.score = 0
        self.asteroid_spawn_timer = 0
        self.next_spawn_interval = self._get_spawn_interval()
        
        # Reset transition variables
        self.transition_out = False
        self.fade_alpha = 0
        self.transition_timer = 0
        
        # Always show difficulty at game start
        self.show_difficulty_message = True
        self.difficulty_message_timer = 3.0
        
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
                center_x = SCREEN_WIDTH // 2
                center_y = SCREEN_HEIGHT // 2
                
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
        spawn_rate_multiplier = DIFFICULTY_SPAWN_RATE_MULTIPLIERS.get(self.difficulty, 1.0)
        base_interval = ASTEROID_SPAWN_RATE / spawn_rate_multiplier
        return random.uniform(base_interval * 0.8, base_interval * 1.2)
    
    def _choose_asteroid_type(self):
        """Choose an asteroid type based on difficulty.
        
        Returns:
            tuple: (type_id, size_category)
        """
        # Get the weights for the current difficulty
        weights = DIFFICULTY_ASTEROID_VARIETY.get(self.difficulty, DIFFICULTY_ASTEROID_VARIETY["Normal Space"])
        
        # Create a list of types with their weights
        weighted_types = []
        for type_id, weight in weights.items():
            weighted_types.extend([type_id] * weight)
        
        # Choose a random type from the weighted list
        type_id = random.choice(weighted_types)
        
        # Choose a size based on the allowed sizes for this type and difficulty
        allowed_sizes = DIFFICULTY_SIZE_RESTRICTIONS.get(
            self.difficulty, DIFFICULTY_SIZE_RESTRICTIONS["Normal Space"]
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
            
            # If transition complete, change to game over state
            if self.transition_timer >= FADE_DURATION:
                return STATE_GAME_OVER
                
            return None
        
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
            
            # Choose asteroid type and size based on difficulty
            type_id, size_category = self._choose_asteroid_type()
            
            # Create new asteroid
            new_asteroid = Asteroid(
                self.particle_system, 
                self.asset_loader,
                type_id=type_id,
                size_category=size_category,
                difficulty=self.difficulty  # Pass the current difficulty to the asteroid
            )
            self.all_sprites.add(new_asteroid)
            self.asteroids.add(new_asteroid)
            
        # Collision detection
        hits = pygame.sprite.spritecollide(self.player, self.asteroids, False, pygame.sprite.collide_circle)
        for asteroid in hits:
            if not self.player.invulnerable:
                # Apply damage from asteroid
                damage_applied = self.player.take_damage(asteroid.damage)
                if damage_applied:
                    # Check if player died
                    if self.player.health <= 0:
                        # Start transition to game over
                        self.transition_out = True
                        self.transition_timer = 0
                        break
        
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
        
        # Draw all sprites
        self.all_sprites.draw(surface)
        
        # Draw score
        score_text = f"Score: {int(self.score)}"
        score_surface = self.score_font.render(score_text, True, SCORE_COLOR)
        surface.blit(score_surface, (10, 10))
        
        # Draw difficulty with color coding
        difficulty_colors = {
            "Empty Space": (0, 255, 0),  # Green for easiest
            "Normal Space": (255, 255, 0),  # Yellow for normal
            "We did not agree on that": (255, 165, 0),  # Orange for medium
            "You kidding": (255, 100, 0),  # Dark orange for hard
            "Hell No!!!": (255, 0, 0)  # Red for hardest
        }
        difficulty_color = difficulty_colors.get(self.difficulty, SCORE_COLOR)
        
        difficulty_text = f"Difficulty: {self.difficulty}"
        difficulty_surface = self.score_font.render(difficulty_text, True, difficulty_color)
        difficulty_rect = difficulty_surface.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        
        # Add a subtle background for better visibility
        bg_rect = difficulty_rect.inflate(20, 10)
        bg_rect.topright = (SCREEN_WIDTH - 5, 5)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 128))  # Semi-transparent black
        surface.blit(bg_surface, bg_rect)
        
        # Draw the difficulty text
        surface.blit(difficulty_surface, difficulty_rect)
        
        # Draw health bar
        self.draw_health_bar(surface)
        
        # Draw fade overlay for transition
        if self.transition_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            surface.blit(fade_surface, (0, 0))
            
        # Draw difficulty notification
        if self.show_difficulty_message:
            # Calculate alpha (fade out towards the end)
            alpha = min(255, int(255 * (self.difficulty_message_timer / 0.5))) if self.difficulty_message_timer < 0.5 else 255
            
            # Difficulty-specific color
            difficulty_colors = {
                "Empty Space": (0, 255, 0),  # Green for easiest
                "Normal Space": (255, 255, 0),  # Yellow for normal
                "We did not agree on that": (255, 165, 0),  # Orange for medium
                "You kidding": (255, 100, 0),  # Dark orange for hard
                "Hell No!!!": (255, 0, 0)  # Red for hardest
            }
            color = difficulty_colors.get(self.difficulty, (255, 255, 255))
            
            # Create message
            message = f"Difficulty: {self.difficulty}"
            message_surface = self.message_font.render(message, True, color)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            
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
            
            subtitle = difficulty_descriptions.get(self.difficulty, "")
            if subtitle:
                subtitle_surface = self.message_font.render(subtitle, True, color)
                subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, message_rect.bottom + 10))
                
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
        y = SCREEN_HEIGHT - HEALTH_BAR_HEIGHT - 10
        
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