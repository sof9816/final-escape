"""
Menu animation entities for Final Escape game.
"""
import pygame
import random
import math
import os
from pygame.math import Vector2
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SIZE,
    ASTEROID_SIZES, ASTEROID_PARTICLE_COLORS
)

class MenuAsteroid:
    """Asteroid entity for menu animation."""
    
    def __init__(self, particle_system, asset_loader):
        """Initialize a menu asteroid with random properties.
        
        Args:
            particle_system: ParticleSystem instance for visual effects
            asset_loader: AssetLoader instance for loading images
        """
        self.particle_system = particle_system
        
        # Random asteroid type (weighted toward less dangerous types for menu)
        self.asteroid_type = random.randint(0, 3)  # Only show a0-a3 in menu
        
        # Random size (medium to large for better visibility)
        size_range = (35, 55)
        self.size = random.randint(size_range[0], size_range[1])
        
        # Load and scale asteroid image using a path relative to the resolution directory
        # asset_loader.load_image will construct the full path (e.g., assets/images/2x/a0.png)
        asteroid_relative_path = f"a{self.asteroid_type}.png"
        
        self.image_original = asset_loader.load_image(
            asteroid_relative_path, # Pass relative path
            scale=(self.size, self.size)
        )
        self.image = self.image_original.copy()
        
        # Random position (anywhere on screen)
        self.position = Vector2(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )
        
        # Random velocity (slower than in-game)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(20, 60)
        self.velocity = Vector2(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )
        
        # Rotation
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-30, 30)
        
        # Particle effects
        self.emit_cooldown = 0
        self.emit_rate = 0.2
        
    def update(self, dt):
        """Update the menu asteroid position and rotation.
        
        Args:
            dt: Time delta in seconds
        """
        # Move asteroid
        self.position += self.velocity * dt
        
        # Wrap around screen edges
        if self.position.x < -self.size:
            self.position.x = SCREEN_WIDTH + self.size
        elif self.position.x > SCREEN_WIDTH + self.size:
            self.position.x = -self.size
            
        if self.position.y < -self.size:
            self.position.y = SCREEN_HEIGHT + self.size
        elif self.position.y > SCREEN_HEIGHT + self.size:
            self.position.y = -self.size
            
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
        # Update particle cooldown
        self.emit_cooldown -= dt
        
    def draw(self, surface):
        """Draw the menu asteroid.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.image_original, self.rotation)
        rect = rotated_image.get_rect(center=self.position)
        surface.blit(rotated_image, rect)
        
    def emit_fire_particles(self):
        """Emit fire particle effects behind the asteroid."""
        if not self.particle_system or self.emit_cooldown > 0:
            return
            
        # Only higher asteroid types emit particles
        if self.asteroid_type < 2:
            return
            
        # Reset cooldown
        self.emit_cooldown = self.emit_rate
        
        # Random direction for particles
        angle = random.uniform(0, math.pi * 2)
        offset_x = math.cos(angle) * (self.size * 0.4)
        offset_y = math.sin(angle) * (self.size * 0.4)
        
        # Emit position
        emit_x = self.position.x + offset_x
        emit_y = self.position.y + offset_y
        
        # Velocity (away from asteroid center)
        vel_base_x = offset_x * 0.5
        vel_base_y = offset_y * 0.5
        
        velocity_range = (
            (vel_base_x - 5, vel_base_x + 5),
            (vel_base_y - 5, vel_base_y + 5)
        )
        
        # Emit particles
        self.particle_system.emit_particles(
            emit_x, emit_y,
            ASTEROID_PARTICLE_COLORS,
            count=1,
            velocity_range=velocity_range,
            size_range=(2, 4),
            lifetime_range=(0.3, 0.7),
            fade=True
        )

class MenuPlayer:
    """Player entity for menu animation."""
    
    def __init__(self, particle_system, asset_loader):
        """Initialize a menu player.
        
        Args:
            particle_system: ParticleSystem instance for visual effects
            asset_loader: AssetLoader instance for loading images
        """
        self.particle_system = particle_system
        
        # Load player image using the appropriate resolution directory
        res_dir = asset_loader.image_size_dir  # Get the resolution dir (1x, 2x, 3x)
        # Construct the "old style" path for the ship, as requested
        ship_path = os.path.join("assets/images", res_dir, "ship.png")
        
        # Load player image
        self.image_original = asset_loader.load_image(
            ship_path, # Pass the pre-constructed path
            scale=(PLAYER_SIZE, PLAYER_SIZE)
        )
        self.image = self.image_original.copy()
        
        # Circular path parameters
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.radius = 150  # Circle radius
        self.angle = 0
        self.orbit_speed = 0.5  # Radians per second
        
        # Calculate initial position
        self.position = Vector2(
            self.center_x + math.cos(self.angle) * self.radius,
            self.center_y + math.sin(self.angle) * self.radius
        )
        
    def update(self, dt):
        """Update the menu player's position.
        
        Args:
            dt: Time delta in seconds
        """
        # Move in a circular path
        self.angle += self.orbit_speed * dt
        self.position.x = self.center_x + math.cos(self.angle) * self.radius
        self.position.y = self.center_y + math.sin(self.angle) * self.radius
        
    def draw(self, surface):
        """Draw the menu player.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Calculate angle for player to face the center of the circle
        facing_angle = math.degrees(math.atan2(
            self.center_y - self.position.y,
            self.center_x - self.position.x
        ))
        
        # Rotate player image to face center (90 degree offset for sprite orientation)
        rotated_image = pygame.transform.rotate(self.image_original, -facing_angle + 90)
        rect = rotated_image.get_rect(center=self.position)
        surface.blit(rotated_image, rect) 