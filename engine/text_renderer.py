"""
TextRenderer utility for Final Escape game.
Provides consistent text rendering throughout the game.
"""
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class TextRenderer:
    """
    Handles text rendering with consistent font usage throughout the game.
    """
    def __init__(self, asset_loader):
        """
        Initialize the text renderer with the game's asset loader.
        
        Args:
            asset_loader: AssetLoader instance containing loaded fonts
        """
        self.asset_loader = asset_loader
        
    def render_text(self, text, font_name, color=(255, 255, 255), centered=False, position=None,
                   anchor="topleft", shadow=False, shadow_color=(40, 40, 40), shadow_offset=2):
        """
        Render text with optional centering, positioning, and shadow effect.
        
        Args:
            text: Text to render
            font_name: Name of the font to use (must be loaded in asset_loader)
            color: RGB color tuple
            centered: Whether to center on screen
            position: Position tuple (x, y) or None for auto-centering
            anchor: Positioning anchor ("topleft", "center", etc.)
            shadow: Whether to add text shadow
            shadow_color: Color for the shadow
            shadow_offset: Offset for the shadow in pixels
            
        Returns:
            Tuple of (surface, rect) for the rendered text
        """
        # Get the font from the asset loader's assets dictionary
        font = None
        if "fonts" in self.asset_loader.assets and font_name in self.asset_loader.assets["fonts"]:
            font = self.asset_loader.assets["fonts"][font_name]
        if not font:
            # Fallback to default font if the requested one is not found
            font = pygame.font.Font(None, 30)
            
        # Create main text surface
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        # Apply positioning based on parameters
        if centered and position is None:
            # Center on screen
            text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        elif position is not None:
            # Use specified position with the given anchor
            setattr(text_rect, anchor, position)
            
        # If shadow effect is requested, create a combined surface
        if shadow:
            # Create a surface large enough for text + shadow
            combined_surface = pygame.Surface(
                (text_rect.width + shadow_offset, text_rect.height + shadow_offset),
                pygame.SRCALPHA
            )
            
            # Render shadow first
            shadow_surface = font.render(text, True, shadow_color)
            
            # Blit shadow and main text
            combined_surface.blit(shadow_surface, (shadow_offset, shadow_offset))
            combined_surface.blit(text_surface, (0, 0))
            
            # Update the surface and adjust the rect
            shadow_rect = combined_surface.get_rect()
            shadow_rect.topleft = text_rect.topleft
            return combined_surface, shadow_rect
            
        return text_surface, text_rect
        
    def render_title(self, text, color=(255, 255, 255), position=None):
        """
        Render text using the title font.
        
        Args:
            text: Text to render
            color: RGB color tuple
            position: Position tuple (x, y) or None for auto-centering
            
        Returns:
            Tuple of (surface, rect) for the rendered text
        """
        return self.render_text(
            text, "title", color, centered=True, position=position,
            anchor="center", shadow=True
        )
        
    def render_score(self, score, color=(255, 255, 255), position=(10, 10)):
        """
        Render score text.
        
        Args:
            score: Score value (int)
            color: RGB color tuple
            position: Position tuple (x, y)
            
        Returns:
            Tuple of (surface, rect) for the rendered text
        """
        return self.render_text(
            f"Score: {score}", "score", color, position=position,
            anchor="topleft", shadow=True
        )
        
    def render_game_over(self, text, color=(255, 255, 255), position=None):
        """
        Render game over text.
        
        Args:
            text: Text to render
            color: RGB color tuple
            position: Position tuple (x, y) or None for auto-centering
            
        Returns:
            Tuple of (surface, rect) for the rendered text
        """
        return self.render_text(
            text, "game_over", color, centered=True, position=position,
            anchor="center", shadow=True
        )
        
    def render_countdown(self, text, color=(255, 255, 255)):
        """
        Render countdown number.
        
        Args:
            text: Text to render
            color: RGB color tuple
            
        Returns:
            Tuple of (surface, rect) for the rendered text
        """
        return self.render_text(
            text, "countdown", color, centered=True,
            anchor="center", shadow=True, shadow_offset=4
        )
        
    def render_instruction(self, text, color=(255, 255, 255), position=None, line_spacing=5):
        """
        Render instruction text, handling multiple lines.
        
        Args:
            text: Text to render, may include newlines
            color: RGB color tuple
            position: Position tuple (x, y) or None for auto-centering
            line_spacing: Extra spacing between lines in pixels
            
        Returns:
            List of tuples (surface, rect) for each line
        """
        lines = text.split("\n")
        rendered_lines = []
        
        for i, line in enumerate(lines):
            line_surface, line_rect = self.render_text(
                line, "instruction", color, centered=True, 
                anchor="center", shadow=True
            )
            
            # If position is specified, adjust vertical position based on line number
            if position is not None:
                line_y = position[1] + i * (line_rect.height + line_spacing)
                line_rect.centery = line_y
                
            # For auto-centered text, adjust vertical position based on line number
            # and total number of lines
            else:
                total_height = len(lines) * line_rect.height + (len(lines) - 1) * line_spacing
                start_y = (SCREEN_HEIGHT - total_height) // 2
                line_y = start_y + i * (line_rect.height + line_spacing)
                line_rect.centery = line_y
                line_rect.centerx = SCREEN_WIDTH // 2
                
            rendered_lines.append((line_surface, line_rect))
            
        return rendered_lines 