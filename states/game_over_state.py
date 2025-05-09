"""
Game over state for Final Escape game.
"""
import pygame
import random
import time
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR,
    GAME_OVER_FONT_SIZE, SCORE_COLOR, INSTRUCTION_FONT_SIZE,
    FADE_DURATION, STATE_MENU
)

class GameOverState:
    """The game over state shown when the player dies."""
    
    def __init__(self, star_field, particle_system, asset_loader=None, screen_width=None, screen_height=None):
        """Initialize the game over state.
        
        Args:
            star_field: StarField instance for background stars
            particle_system: ParticleSystem instance for effects
            asset_loader: Optional AssetLoader instance for loading fonts
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        self.star_field = star_field
        self.particle_system = particle_system
        self.asset_loader = asset_loader
        
        # Store screen dimensions
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        # Setup fonts - try to use custom fonts if asset_loader is provided
        if asset_loader:
            assets = asset_loader.load_game_assets()
            self.game_over_font = assets["fonts"]["game_over"] if "fonts" in assets and "game_over" in assets["fonts"] else pygame.font.Font(None, GAME_OVER_FONT_SIZE)
            self.instruction_font = assets["fonts"]["instruction"] if "fonts" in assets and "instruction" in assets["fonts"] else pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        else:
            # Fallback to default fonts
            self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
            self.instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        
        # Store final score
        self.final_score = 0
        
        # Simple delay to prevent accidental key presses
        self.allow_transition = False
        self.delay_timer = 0
        self.delay_threshold = 1.0  # 1 second before allowing input
        
        # Transition flag
        self.transition_requested = False
        
        # Instruction text animation
        self.instruction_alpha = 255
        self.fade_direction = -1  # -1 for fade out, 1 for fade in
        self.fade_speed = 200  # Alpha change per second
        
        print("GameOverState initialized")
        
    def set_score(self, score):
        """Set the final score to display.
        
        Args:
            score: The final score value
        """
        self.final_score = score
        self.allow_transition = False
        self.delay_timer = 0
        self.transition_requested = False
        print(f"Final score set: {score}")
        
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            STATE_MENU if transitioning, None otherwise
        """
        # Only handle keypresses once delay has passed
        if not self.allow_transition:
            return None
            
        # Check for any input 
        if (event.type == pygame.KEYDOWN or 
            event.type == pygame.MOUSEBUTTONDOWN or
            event.type == pygame.JOYBUTTONDOWN):
            print("Input detected in game over state - transitioning to menu")
            self.transition_requested = True
            return STATE_MENU
            
        return None
                
    def update(self, dt):
        """Update the game over state.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            STATE_MENU if transitioning, None otherwise
        """
        # Update timer for transition delay
        if not self.allow_transition:
            self.delay_timer += dt
            if self.delay_timer >= self.delay_threshold:
                self.allow_transition = True
                print("Game over state ready for transition")
        
        # Update stars
        self.star_field.update(dt)
        
        # Update particles
        self.particle_system.update(dt)
        
        # Update instruction text animation
        self.instruction_alpha += self.fade_direction * self.fade_speed * dt
        if self.instruction_alpha <= 100:
            self.instruction_alpha = 100
            self.fade_direction = 1
        elif self.instruction_alpha >= 255:
            self.instruction_alpha = 255
            self.fade_direction = -1
        
        # Check if transition was requested via event
        if self.transition_requested:
            print("Transition requested - returning to menu from game over state")
            self.transition_requested = False  # Reset flag to prevent multiple transitions
            return STATE_MENU
        
        return None
            
    def draw(self, surface):
        """Draw the game over state.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Clear screen
        surface.fill(BACKGROUND_COLOR)
        
        # Draw stars
        self.star_field.draw(surface)
        
        # Draw particles
        self.particle_system.draw(surface)
        
        # Draw game over text
        game_over_text = "GAME OVER"
        game_over_surface = self.game_over_font.render(game_over_text, True, (255, 255, 255))
        game_over_rect = game_over_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        surface.blit(game_over_surface, game_over_rect)
        
        # Draw score
        score_text = f"Score: {int(self.final_score)}"
        score_surface = self.game_over_font.render(score_text, True, SCORE_COLOR)
        score_rect = score_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(score_surface, score_rect)
        
        # Draw instruction text with pulsing effect
        instruction_text = "Press any key to return to menu"
        instruction_surface = self.instruction_font.render(instruction_text, True, (255, 255, 255))
        instruction_rect = instruction_surface.get_rect(center=(self.screen_width // 2, self.screen_height * 3 // 4))
        
        # Create a surface with alpha for the pulsing effect
        alpha_surface = pygame.Surface(instruction_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, 0))
        alpha_surface.blit(instruction_surface, (0, 0))
        alpha_surface.set_alpha(int(self.instruction_alpha))
        
        surface.blit(alpha_surface, instruction_rect) 