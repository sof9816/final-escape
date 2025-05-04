"""
Game state for Asteroid Navigator game.
"""
import pygame
import random
from pygame.math import Vector2
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR,
    SCORE_FONT_SIZE, SCORE_COLOR, ASTEROID_SPAWN_RATE,
    HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, HEALTH_BAR_BORDER,
    HEALTH_BAR_COLOR, HEALTH_BAR_BACKGROUND_COLOR, HEALTH_BAR_BORDER_COLOR,
    PLAYER_MAX_HEALTH, FADE_DURATION, STATE_GAME_OVER
)
from entities.player import Player
from entities.asteroid import Asteroid

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
        
        # Setup fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        
        # Create player
        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), particle_system, asset_loader)
        self.all_sprites.add(self.player)
        
        # Game variables
        self.score = 0
        self.asteroid_spawn_timer = 0
        self.next_spawn_interval = ASTEROID_SPAWN_RATE
        
        # Transition variables
        self.transition_out = False
        self.fade_alpha = 0
        self.transition_timer = 0
        
        # Joystick (optional)
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            
    def reset(self):
        """Reset the game state for a new game."""
        # Clear sprite groups
        self.all_sprites.empty()
        self.asteroids.empty()
        
        # Create new player
        self.player = Player((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.particle_system, self.asset_loader)
        self.all_sprites.add(self.player)
        
        # Reset game variables
        self.score = 0
        self.asteroid_spawn_timer = 0
        self.next_spawn_interval = ASTEROID_SPAWN_RATE
        
        # Reset transition variables
        self.transition_out = False
        self.fade_alpha = 0
        self.transition_timer = 0
        
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
            self.next_spawn_interval = random.uniform(ASTEROID_SPAWN_RATE * 0.5, ASTEROID_SPAWN_RATE * 1.5)
            
            # Create new asteroid
            new_asteroid = Asteroid(self.particle_system, self.asset_loader)
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
        
        # Draw health bar
        self.draw_health_bar(surface)
        
        # Draw fade overlay for transition
        if self.transition_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            surface.blit(fade_surface, (0, 0))
            
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