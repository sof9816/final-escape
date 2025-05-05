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
        self.opacity = 153  # 60% of 255 for reduced opacity
        
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
        # Create a semitransparent surface for the star
        star_surface = pygame.Surface((self.size * 2 + 1, self.size * 2 + 1), pygame.SRCALPHA)
        # Draw the star with reduced opacity
        pygame.draw.circle(
            star_surface, 
            (*self.color, self.opacity),  # RGB + Alpha 
            (self.size + 1, self.size + 1), 
            self.size
        )
        # Blit the transparent surface to the main surface
        surface.blit(star_surface, (int(self.x) - self.size - 1, int(self.y) - self.size - 1))

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