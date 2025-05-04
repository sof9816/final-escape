"""
Game over scene for Asteroid Navigator.
"""
import pygame
from pygame.locals import KEYDOWN, JOYBUTTONDOWN
from src.constants import (
    BACKGROUND_COLOR, SCORE_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, FADE_DURATION
)
from src.scenes.scene import Scene
from src.entities.star import StarField
from src.entities.menu_objects import MenuAsteroid
from src.utils.helpers import change_music, create_fade_surface, fade_in

class GameOverScene(Scene):
    """Game over scene shown when the player is defeated."""
    
    def __init__(self, screen, assets, score=0):
        """
        Initialize the game over scene.
        
        Args:
            screen: Pygame display surface
            assets: AssetLoader instance
            score: Final score from the game scene
        """
        super().__init__(screen, assets)
        self.next_scene = "START"
        self.score = score
        
        # Create starfield
        self.star_field = StarField(100, SCREEN_WIDTH)
        
        # Create menu elements for animation
        self.menu_asteroids = [MenuAsteroid(assets.asteroid_images) for _ in range(10)]
        
        # Setup fade transition
        self.fade_surface = create_fade_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.transition_timer = 0
        self.fade_alpha = 255
        
        # Get fonts
        self.game_over_font = assets.get_font("game_over")
        self.instruction_font = assets.get_font("instruction")
        
        # Start music
        change_music(assets.get_sound("game_over_music"))
        
        # Prepare text
        self.game_over_text = self.game_over_font.render("Game Over", True, SCORE_COLOR)
        self.game_over_rect = self.game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        )
        
        self.death_text = self.instruction_font.render(
            "Your ship was destroyed!", True, SCORE_COLOR
        )
        self.death_rect = self.death_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        
        self.score_text = self.instruction_font.render(
            f"Final Score: {int(self.score)}", True, SCORE_COLOR
        )
        self.score_rect = self.score_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        )
        
        self.restart_text = self.instruction_font.render(
            "Press any key to play again", True, SCORE_COLOR
        )
        self.restart_rect = self.restart_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        )
        
    def process_events(self, events):
        """
        Process input events.
        
        Args:
            events: List of pygame events to process
            
        Returns:
            bool: True if the game should quit
        """
        for event in events:
            if event.type == pygame.QUIT:
                return True
            if event.type == KEYDOWN or event.type == JOYBUTTONDOWN:
                # Begin transition to start menu
                self.done = True
                
        return False
                
    def update(self, dt, joystick=None):
        """
        Update scene elements.
        
        Args:
            dt: Delta time
            joystick: Optional joystick for control
        """
        # Update stars
        self.star_field.update(dt)
        
        # Update menu animations
        for asteroid in self.menu_asteroids:
            asteroid.update(dt)
        
        # Update fade transition
        if self.transition_timer < FADE_DURATION:
            self.transition_timer, self.fade_alpha, _ = fade_in(
                self.screen,
                self.fade_surface,
                dt,
                self.transition_timer,
                FADE_DURATION
            )
        
    def draw(self):
        """Draw scene elements on the screen."""
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw stars
        self.star_field.draw(self.screen)
        
        # Draw menu objects
        for asteroid in self.menu_asteroids:
            asteroid.draw(self.screen)
        
        # Draw text
        self.screen.blit(self.game_over_text, self.game_over_rect)
        self.screen.blit(self.death_text, self.death_rect)
        self.screen.blit(self.score_text, self.score_rect)
        self.screen.blit(self.restart_text, self.restart_rect)
        
        # Draw fade overlay if transitioning
        if self.transition_timer < FADE_DURATION:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0)) 