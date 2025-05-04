"""
Game over state for Asteroid Navigator game.
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
    
    def __init__(self, star_field, particle_system):
        """Initialize the game over state.
        
        Args:
            star_field: StarField instance for background stars
            particle_system: ParticleSystem instance for effects
        """
        self.star_field = star_field
        self.particle_system = particle_system
        
        # Setup fonts
        self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
        self.instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        
        # Store final score
        self.final_score = 0
        
        # Simple delay to prevent accidental key presses
        self.allow_transition = False
        self.delay_timer = 0
        self.delay_threshold = 1.0  # 1 second before allowing transition
        
        # IMPROVED: Add a transition flag that will be checked in multiple places
        self.transition_requested = False
        # Keep track of the last time we checked for input
        self.last_input_check = 0
        # Add a direct transition counter as a failsafe
        self.direct_transition_timer = 0
        self.direct_transition_threshold = 3.0  # Force transition after 3 seconds of being ready
        
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
        self.direct_transition_timer = 0
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
            
        # IMPROVED: Check for more event types
        if (event.type == pygame.KEYDOWN or 
            event.type == pygame.MOUSEBUTTONDOWN or
            event.type == pygame.JOYBUTTONDOWN):
            print("Input detected in game over state via event - transitioning to menu")
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
        
        # IMPROVED: Once we're allowed to transition, start the direct transition timer
        if self.allow_transition:
            self.direct_transition_timer += dt
            
            # IMPROVED: Check for input every frame once we're ready
            # This is more reliable than waiting for events
            if any(pygame.key.get_pressed()) or pygame.mouse.get_pressed()[0]:
                print("Input detected in game over state via polling - transitioning to menu")
                self.transition_requested = True
                
            # IMPROVED: Force transition after threshold as a failsafe
            if self.direct_transition_timer >= self.direct_transition_threshold:
                print("Direct transition timer expired - forcing transition to menu")
                self.transition_requested = True
        
        # Update stars
        self.star_field.update(dt)
        
        # Update particles
        self.particle_system.update(dt)
        
        # IMPROVED: Check if transition was requested from any method
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
        
        # Draw "Game Over" text
        game_over_text = "Game Over"
        game_over_surface = self.game_over_font.render(game_over_text, True, SCORE_COLOR)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        surface.blit(game_over_surface, game_over_rect)
        
        # Draw death message
        death_text = "Your ship was destroyed!"
        death_surface = self.instruction_font.render(death_text, True, SCORE_COLOR)
        death_rect = death_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(death_surface, death_rect)
        
        # Draw final score
        score_text = f"Final Score: {int(self.final_score)}"
        score_surface = self.instruction_font.render(score_text, True, SCORE_COLOR)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        surface.blit(score_surface, score_rect)
        
        # Only show restart instruction after delay
        if self.allow_transition:
            restart_text = "Press any key to play again"
            restart_surface = self.instruction_font.render(restart_text, True, SCORE_COLOR)
            restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            surface.blit(restart_surface, restart_rect) 