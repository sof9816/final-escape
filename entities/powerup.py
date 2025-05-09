"""
Power-up entity for Final Escape game.
"""
import pygame
import random
import os
from pygame.math import Vector2
from constants import (
    POWERUP_SIZE, POWERUP_BOOM_ID, 
    SOUND_EXPLOSION_MAIN, POWERUP_BOOM_FLASH_DURATION
)

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
        self.image = powerup_image_surface # Use the pre-loaded and scaled image
        self.rect = self.image.get_rect(center=initial_position)

        self.position = Vector2(initial_position)
        
        # Movement properties (e.g., slow drift or stationary)
        # For now, let's make them stationary or drift slowly
        self.velocity = Vector2(random.uniform(-20, 20), random.uniform(20, 50)) # Slow downward drift

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = self.rect.width // 2


    def update(self, dt, joystick=None): # joystick is unused but often part of group update signatures
        """Update the power-up's position and state.

        Args:
            dt (float): Time delta since the last frame.
            joystick: Unused, for compatibility.
        """
        self.position += self.velocity * dt
        self.rect.center = self.position

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