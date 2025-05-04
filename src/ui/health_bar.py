"""
Health bar UI component for Asteroid Navigator.
"""
import pygame
from src.constants import (
    HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, HEALTH_BAR_BORDER,
    HEALTH_BAR_COLOR, HEALTH_BAR_BACKGROUND_COLOR, HEALTH_BAR_BORDER_COLOR
)

class HealthBar:
    """Health bar UI component that displays player health."""
    
    def __init__(self, screen_height, font):
        """
        Initialize the health bar.
        
        Args:
            screen_height: Height of the game screen
            font: Font for rendering health text
        """
        self.screen_height = screen_height
        self.font = font
        self.width = HEALTH_BAR_WIDTH
        self.height = HEALTH_BAR_HEIGHT
        self.border = HEALTH_BAR_BORDER
        self.color = HEALTH_BAR_COLOR
        self.bg_color = HEALTH_BAR_BACKGROUND_COLOR
        self.border_color = HEALTH_BAR_BORDER_COLOR
        
        # Position the health bar in the top left corner with a small margin
        self.x = 10
        self.y = self.screen_height - self.height - 10
        
    def draw(self, surface, current_health, max_health):
        """
        Draw the health bar on the given surface.
        
        Args:
            surface: Surface to draw on
            current_health: Current player health
            max_health: Maximum possible health
        """
        # Calculate width of health portion
        health_width = int((current_health / max_health) * self.width)
        
        # Draw background
        pygame.draw.rect(
            surface, 
            self.bg_color, 
            (self.x, self.y, self.width, self.height)
        )
        
        # Draw health portion
        pygame.draw.rect(
            surface, 
            self.color, 
            (self.x, self.y, health_width, self.height)
        )
        
        # Draw border
        pygame.draw.rect(
            surface, 
            self.border_color, 
            (
                self.x - self.border, 
                self.y - self.border, 
                self.width + (self.border * 2), 
                self.height + (self.border * 2)
            ), 
            self.border
        )
        
        # Draw text showing exact health value
        health_text = f"Health: {current_health}/{max_health}"
        health_surface = self.font.render(health_text, True, self.border_color)
        health_rect = health_surface.get_rect(
            midleft=(self.x + 10, self.y + self.height // 2)
        )
        surface.blit(health_surface, health_rect) 