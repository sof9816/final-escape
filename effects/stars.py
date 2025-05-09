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
    
    def __init__(self, screen_width=None, screen_height=None):
        """Initialize a star with random properties.
        
        Args:
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        self.x = random.randint(0, self.screen_width)
        self.y = random.randint(0, self.screen_height)
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
        
        # If star is offscreen, respawn at the top
        if self.y > self.screen_height:
            self.y = 0
            self.x = random.randint(0, self.screen_width)
            
    def draw(self, surface):
        """Draw the star to the surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Apply opacity
        color_with_opacity = (*self.color, self.opacity)
        
        # Draw the star as a small rect or circle based on size
        if self.size == 1:
            # Draw tiny star as a single pixel with opacity
            pixel_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            pixel_surface.fill(color_with_opacity)
            surface.blit(pixel_surface, (int(self.x), int(self.y)))
        else:
            # Draw larger star as a circle with opacity
            radius = self.size // 2
            star_surface = pygame.Surface((self.size + 2, self.size + 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, color_with_opacity, (radius + 1, radius + 1), radius)
            surface.blit(star_surface, (int(self.x), int(self.y)))

class StarField:
    """Collection of stars for background effect."""
    
    def __init__(self, num_stars=NUM_STARS, screen_width=None, screen_height=None):
        """Initialize the star field.
        
        Args:
            num_stars: Number of stars to create
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        self.stars = []
        for _ in range(num_stars):
            self.stars.append(Star(self.screen_width, self.screen_height))
    
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
            
    def set_opacity(self, opacity_percent):
        """Set the opacity for all stars.
        
        Args:
            opacity_percent: Opacity as a percentage (0-100)
        """
        opacity = int(opacity_percent * 255 / 100)
        for star in self.stars:
            star.opacity = opacity 
            
    def set_screen_size(self, width, height):
        """Update the screen size for all stars.
        
        Args:
            width: New screen width
            height: New screen height
        """
        self.screen_width = width
        self.screen_height = height
        
        # Update existing stars to use new dimensions
        for star in self.stars:
            star.screen_width = width
            star.screen_height = height
            
            # Reposition stars that would now be off-screen
            if star.x > width:
                star.x = random.randint(0, width)
            if star.y > height:
                star.y = random.randint(0, height) 