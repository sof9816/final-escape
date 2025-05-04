"""
Asteroid entity for Asteroid Navigator.
"""
import random
import pygame
from pygame.math import Vector2
from src.utils.helpers import weighted_random_choice
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ASTEROID_SIZES, ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED,
    ASTEROID_SPEED_MULTIPLIERS, ASTEROID_TYPE_WEIGHTS, ASTEROID_SIZE_RESTRICTIONS,
    ASTEROID_BASE_DAMAGE, ASTEROID_SIZE_DAMAGE_MULTIPLIERS
)

class Asteroid(pygame.sprite.Sprite):
    """
    Asteroid obstacle that damages the player on collision.
    Asteroids come in different types (0-6) and sizes (small, medium, large).
    """
    
    def __init__(self, asteroid_images):
        """
        Initialize an asteroid with random properties.
        
        Args:
            asteroid_images: Dictionary of asteroid images by type
        """
        super().__init__()
        
        # Select asteroid type based on weighted probability
        self.asteroid_type = weighted_random_choice(ASTEROID_TYPE_WEIGHTS)
        
        # Determine size category based on asteroid type restrictions
        allowed_sizes = ASTEROID_SIZE_RESTRICTIONS[self.asteroid_type]
        self.size_category = random.choice(allowed_sizes)
        size_range = ASTEROID_SIZES[self.size_category]
        
        # Random size within the category's range
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
        pos = Vector2(0, 0)  # Initialize pos vector
        vel = Vector2(0, 0)  # Initialize vel vector

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
        else:  # edge == 'right'
            pos.x = SCREEN_WIDTH + size / 2
            pos.y = random.randint(0, SCREEN_HEIGHT)
            vel.x = -1
            vel.y = random.uniform(-1, 1)

        # Normalize velocity and apply speed magnitude
        if vel.length() > 0:
            self.vel = vel.normalize() * speed_magnitude
        else:  # Avoid zero vector if random rolls are both 0
            self.vel = Vector2(0, speed_magnitude)  # Default downwards

        # Use the selected asteroid type image
        self.image = pygame.transform.smoothscale(asteroid_images[self.asteroid_type], (size, size))
        
        # Make the background transparent
        self.image.set_colorkey((0, 0, 0))
        
        # Create circular collision mask
        self.radius = size // 2
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.original_image = self.image.copy()
        
        # Store precise position
        self.pos = Vector2(pos)
        
    def update(self, dt, joystick=None):  # joystick=None to match Player signature
        """
        Update asteroid position.
        
        Args:
            dt: Delta time
            joystick: Unused, included for compatibility with sprite group updates
        """
        self.pos += self.vel * dt
        self.rect.center = self.pos  # Update rect center from pos

        # Remove asteroids that go far off-screen
        buffer = max(self.rect.width, self.rect.height) * 2
        if (self.rect.right < -buffer or
            self.rect.left > SCREEN_WIDTH + buffer or
            self.rect.bottom < -buffer or
            self.rect.top > SCREEN_HEIGHT + buffer):
            self.kill()  # Remove sprite from all groups 