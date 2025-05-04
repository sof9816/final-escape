"""
Menu-specific entities for Asteroid Navigator.
These objects are used in the menu screens for visual effects.
"""
import math
import random
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SIZE

class MenuAsteroid:
    """Background asteroid for menu screens."""
    
    def __init__(self, asteroid_images):
        """
        Initialize a menu asteroid.
        
        Args:
            asteroid_images: Dictionary of asteroid images by type
        """
        self.size = random.randint(20, 60)
        self.x = random.randint(-100, SCREEN_WIDTH + 100)
        self.y = random.randint(-100, SCREEN_HEIGHT + 100)
        self.vel_x = random.uniform(-30, 30)
        self.vel_y = random.uniform(-30, 30)
        self.rotation = 0
        self.rotation_speed = random.uniform(-50, 50)
        
        # Choose a random asteroid type
        asteroid_type = random.randint(0, 6)
        self.image = pygame.transform.scale(
            asteroid_images[asteroid_type], 
            (self.size, self.size)
        )
        self.image.set_colorkey((0, 0, 0))  # Make background transparent
        
    def update(self, dt):
        """
        Update asteroid position and rotation.
        
        Args:
            dt: Delta time
        """
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
        """
        Draw the asteroid.
        
        Args:
            surface: Surface to draw on
        """
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        # Get new rect after rotation
        rect = rotated_image.get_rect(center=(self.x, self.y))
        # Draw the rotated image
        surface.blit(rotated_image, rect.topleft)

class MenuPlayer:
    """Animated player ship for menu screens."""
    
    def __init__(self, player_image):
        """
        Initialize a menu player.
        
        Args:
            player_image: Player ship image
        """
        self.image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.image.set_colorkey((0, 0, 0))
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2 + 150
        self.angle = 0
        self.radius = 100
        self.speed = 30  # Degrees per second
        
    def update(self, dt):
        """
        Update player position along circular path.
        
        Args:
            dt: Delta time
        """
        # Move in a circular path
        self.angle += self.speed * dt
        self.angle %= 360
        
        # Calculate position on the circle
        self.x = SCREEN_WIDTH // 2 + self.radius * math.cos(math.radians(self.angle))
        self.y = SCREEN_HEIGHT // 2 + 150 + self.radius * math.sin(math.radians(self.angle))
        
    def draw(self, surface):
        """
        Draw the player ship.
        
        Args:
            surface: Surface to draw on
        """
        # Calculate angle for player to face the center of the circle
        rotation_angle = (self.angle + 90) % 360
        
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.image, -rotation_angle)
        # Get new rect after rotation
        rect = rotated_image.get_rect(center=(self.x, self.y))
        # Draw the rotated image
        surface.blit(rotated_image, rect.topleft) 