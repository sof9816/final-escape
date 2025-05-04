"""
Star entity for background effect in Asteroid Navigator.
"""
import random
import pygame
from src.constants import STAR_SIZES, STAR_COLORS, STAR_SPEEDS, SCREEN_HEIGHT

class Star:
    """Background star for parallax scrolling effect."""
    
    def __init__(self, screen_width):
        """
        Initialize a star.
        
        Args:
            screen_width: Width of the game screen
        """
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.choice(STAR_SIZES)
        self.color = random.choice(STAR_COLORS)
        self.speed = random.choice(STAR_SPEEDS)
        
    def update(self, dt):
        """
        Update star position.
        
        Args:
            dt: Delta time
        """
        # Move stars downward
        self.y += self.speed * dt
        
        # If star goes off-screen, reset it to the top
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_HEIGHT)
            
    def draw(self, surface):
        """
        Draw the star.
        
        Args:
            surface: Surface to draw on
        """
        pygame.draw.circle(
            surface, 
            self.color, 
            (int(self.x), int(self.y)), 
            self.size
        )

class StarField:
    """Manages a collection of stars for the background."""
    
    def __init__(self, num_stars, screen_width):
        """
        Initialize the star field.
        
        Args:
            num_stars: Number of stars to create
            screen_width: Width of the game screen
        """
        self.stars = [Star(screen_width) for _ in range(num_stars)]
        
    def update(self, dt):
        """
        Update all stars.
        
        Args:
            dt: Delta time
        """
        for star in self.stars:
            star.update(dt)
            
    def draw(self, surface):
        """
        Draw all stars.
        
        Args:
            surface: Surface to draw on
        """
        for star in self.stars:
            star.draw(surface) 