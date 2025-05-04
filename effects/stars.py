"""
Background star effects for Asteroid Navigator game.
"""
import pygame
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    NUM_STARS, STAR_SIZES, STAR_COLORS, STAR_SPEEDS
)

class Star:
    """Individual star object for background effect."""
    
    def __init__(self):
        """Initialize a star with random properties."""
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.choice(STAR_SIZES)
        self.color = random.choice(STAR_COLORS)
        self.speed = random.choice(STAR_SPEEDS)
        
    def update(self, dt):
        """Update the star position.
        
        Args:
            dt: Time delta in seconds
        """
        # Move stars downward
        self.y += self.speed * dt
        
        # Wrap around when off-screen
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        """Draw the star on the given surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class StarField:
    """Manager for a field of background stars."""
    
    def __init__(self, num_stars=NUM_STARS):
        """Initialize the star field.
        
        Args:
            num_stars: Number of stars to create
        """
        self.stars = [Star() for _ in range(num_stars)]
        
    def update(self, dt):
        """Update all stars.
        
        Args:
            dt: Time delta in seconds
        """
        for star in self.stars:
            star.update(dt)
            
    def draw(self, surface):
        """Draw all stars.
        
        Args:
            surface: Pygame surface to draw on
        """
        for star in self.stars:
            star.draw(surface) 