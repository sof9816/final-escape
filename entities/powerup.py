"""
Power-up entity for Final Escape game.
"""
import pygame
import random
import os
import math
from pygame.math import Vector2
from constants import (
    POWERUP_SIZE, POWERUP_BOOM_ID, 
    SOUND_EXPLOSION_MAIN, POWERUP_BOOM_FLASH_DURATION
)

# Define color themes for different power-up types
POWERUP_COLOR_THEMES = {
    POWERUP_BOOM_ID: {
        "glow_color": (255, 100, 50),  # Orange-red for boom/explosion
        "particle_colors": [
            (255, 165, 0),    # Orange
            (255, 140, 0),    # Dark Orange
            (255, 99, 71),    # Tomato
            (255, 69, 0)      # Red-Orange
        ]
    },
    # Add more themes for future power-up types here
    "default": {
        "glow_color": (255, 255, 255),  # White default glow
        "particle_colors": [
            (200, 200, 255),  # Light blue
            (150, 150, 255),  # Blue
            (100, 100, 255),  # Medium blue
            (255, 255, 255)   # White
        ]
    }
}

class PowerUpGroup(pygame.sprite.Group):
    """Custom sprite group for power-ups that handles special drawing."""
    
    def draw(self, surface):
        """Override the default Group draw method to use the power-up's custom draw method.
        
        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        sprites = self.sprites()
        
        if not sprites:
            return
            
        for powerup in sprites:
            powerup.draw(surface)

class PowerUp(pygame.sprite.Sprite):
    """PowerUp class representing collectible items with special effects."""

    def __init__(self, initial_position, powerup_type_id, powerup_image_surface, screen_width, screen_height):
        """Initialize a power-up.

        Args:
            initial_position (tuple): The (x, y) coordinates for the power-up.
            powerup_type_id (str): The identifier for the type of power-up (e.g., "boom").
            powerup_image_surface (pygame.Surface): The pre-loaded image for this power-up.
            screen_width (int): Width of the game screen.
            screen_height (int): Height of the game screen.
        """
        super().__init__()
        
        self.type_id = powerup_type_id
        if powerup_image_surface is None:
            # Create a fallback image if none provided
            fallback_img = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(fallback_img, (255, 0, 255), (POWERUP_SIZE//2, POWERUP_SIZE//2), POWERUP_SIZE//2)
            self.original_image = fallback_img
        else:
            self.original_image = powerup_image_surface  # Store the original image
        
        self.image = self.original_image.copy()  # Use a copy that we can modify
        self.rect = self.image.get_rect(center=initial_position)

        self.position = Vector2(initial_position)
        
        # Movement properties (e.g., slow drift or stationary)
        # For now, let's make them stationary or drift slowly
        self.velocity = Vector2(random.uniform(-20, 20), random.uniform(20, 50)) # Slow downward drift

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = self.rect.width // 2
        
        # Get color theme for this powerup type
        color_theme = POWERUP_COLOR_THEMES.get(self.type_id, POWERUP_COLOR_THEMES["default"])
        
        # Animation and effect properties
        self.pulse_factor = 0  # Controls the pulse animation
        self.pulse_speed = 4  # Speed of pulsing
        self.pulse_direction = 1  # 1 for increasing, -1 for decreasing
        self.rotation = 0  # For subtle rotation
        self.rotation_speed = 30  # Degrees per second
        self.alpha = 255  # For fade effect
        self.glow_color = color_theme["glow_color"]
        self.particle_colors = color_theme["particle_colors"]
        self.glow_radius = int(self.radius * 1.5)  # 50% larger than the powerup
        self.creation_time = pygame.time.get_ticks() / 1000.0  # Time in seconds when powerup was created
        
        # Occasionally emit particles for more visibility
        self.particle_timer = 0
        self.particle_interval = random.uniform(0.3, 0.7)  # Random interval between particle bursts


    def update(self, dt, joystick=None): # joystick is unused but often part of group update signatures
        """Update the power-up's position and state.

        Args:
            dt (float): Time delta since the last frame.
            joystick: Unused, for compatibility.
        """
        self.position += self.velocity * dt
        self.rect.center = self.position

        # Update animation effects
        # Pulsing animation
        self.pulse_factor += self.pulse_speed * self.pulse_direction * dt
        if self.pulse_factor > 1.0:
            self.pulse_factor = 1.0
            self.pulse_direction = -1
        elif self.pulse_factor < 0.0:
            self.pulse_factor = 0.0
            self.pulse_direction = 1
            
        # Rotation animation
        self.rotation += self.rotation_speed * dt
        if self.rotation >= 360:
            self.rotation -= 360
            
        # Update particle timer for occasional sparkle effects
        self.particle_timer -= dt
        if self.particle_timer <= 0:
            self.particle_timer = self.particle_interval
            # Signal that we need to emit particles - actual emission happens in game state
            # This property will be checked by the game state during drawing
            self.emit_particles = True
        else:
            self.emit_particles = False
            
        # Apply visual effects to self.image for compatibility with standard sprite drawing
        self._update_image()
            
        # Remove if it drifts off screen (e.g., bottom edge)
        if self.rect.top > self.screen_height + self.rect.height:
            self.kill()
        elif self.rect.left > self.screen_width + self.rect.width:
            self.kill()
        elif self.rect.right < -self.rect.width:
            self.kill()
        # Optionally, if it can also drift upwards off screen
        # elif self.rect.bottom < -self.rect.height:
        #     self.kill()
            
    def _update_image(self):
        """Update the image attribute with visual effects for standard sprite drawing."""
        # Create a new surface for the rotated image with alpha channel
        rotated_image = pygame.transform.rotate(self.original_image, self.rotation)
        
        # Scale based on pulse (subtle effect: 90%-110% of original size)
        scale_factor = 0.9 + 0.2 * self.pulse_factor
        scaled_size = (int(rotated_image.get_width() * scale_factor), 
                      int(rotated_image.get_height() * scale_factor))
        
        # Scale the rotated image
        scaled_image = pygame.transform.scale(rotated_image, scaled_size)
        
        # Update self.image and self.rect
        self.image = scaled_image
        # Preserve center position
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def draw(self, surface):
        """Draw the power-up with visual effects.
        
        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        # Create a new surface with per-pixel alpha for glow effect
        glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        
        # Calculate glow intensity based on pulse factor (0.5 to 1.0 range for minimum visibility)
        glow_intensity = int(128 + 127 * self.pulse_factor)  # 128-255 range
        
        # Draw the outer glow (larger, more transparent)
        outer_radius = self.glow_radius
        pygame.draw.circle(
            glow_surface,
            (*self.glow_color, glow_intensity // 2),  # RGBA with half intensity
            (self.glow_radius, self.glow_radius),
            outer_radius
        )
        
        # Draw the inner glow (smaller, more opaque)
        inner_radius = int(self.glow_radius * 0.7)
        pygame.draw.circle(
            glow_surface, 
            (*self.glow_color, glow_intensity),  # RGBA with full intensity
            (self.glow_radius, self.glow_radius),
            inner_radius
        )
        
        # Draw the glow at powerup position
        glow_pos = (
            int(self.position.x - self.glow_radius),
            int(self.position.y - self.glow_radius)
        )
        surface.blit(glow_surface, glow_pos)
        
        # Draw the powerup sprite on top of the glow
        surface.blit(self.image, self.rect)

    def activate(self, game_state_instance):
        """
        Activate the power-up's effect.
        This method will be implemented with specific logic for each power-up type.
        Args:
            game_state_instance: The instance of the game state, to allow interaction.
        """
        print(f"Power-up {self.type_id} collected by player.")

        if self.type_id == POWERUP_BOOM_ID:
            print(f"Activating BOOM power-up effect.")
            game_state_instance.boom_effect_active = True # Signal GameState to handle the effect
            game_state_instance.boom_flash_timer = POWERUP_BOOM_FLASH_DURATION
            game_state_instance.boom_center = game_state_instance.player.position.copy()
            
            # Play main explosion sound
            explosion_sound = game_state_instance.asset_loader.assets["sounds"].get("explosion_main")
            if explosion_sound:
                explosion_sound.play()
            else:
                print("Warning: explosion_main sound not found or loaded.")

        # Common logic for all power-ups after activation (e.g., removal)
        self.kill() # Remove power-up sprite from all groups 