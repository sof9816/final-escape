"""
Countdown scene for Asteroid Navigator.
"""
import pygame
from src.constants import (
    BACKGROUND_COLOR, COUNTDOWN_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT,
    FADE_DURATION, COUNTDOWN_DURATION
)
from src.scenes.scene import Scene
from src.entities.star import StarField
from src.utils.helpers import change_music, create_fade_surface, fade_in

class CountdownScene(Scene):
    """Countdown scene shown before gameplay starts."""
    
    def __init__(self, screen, assets):
        """
        Initialize the countdown scene.
        
        Args:
            screen: Pygame display surface
            assets: AssetLoader instance
        """
        super().__init__(screen, assets)
        self.next_scene = "PLAYING"
        
        # Create starfield
        self.star_field = StarField(100, SCREEN_WIDTH)
        
        # Setup fade transition
        self.fade_surface = create_fade_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.transition_timer = 0
        self.fade_alpha = 255
        
        # Get fonts
        self.countdown_font = assets.get_font("countdown")
        self.instruction_font = assets.get_font("instruction")
        
        # Countdown timer
        self.countdown_start_time = pygame.time.get_ticks() / 1000  # Current time in seconds
        
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
        
        # Check if countdown is complete
        current_time = pygame.time.get_ticks() / 1000
        elapsed = current_time - self.countdown_start_time
        
        # Calculate current countdown number
        self.count_num = COUNTDOWN_DURATION - int(elapsed)
        
        if self.count_num <= 0:
            # Countdown finished
            self.done = True
        
        # Update fade transition
        if elapsed < FADE_DURATION:
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
        
        # Draw the countdown number
        if self.count_num > 0:
            count_text = str(self.count_num)
            count_surface = self.countdown_font.render(count_text, True, COUNTDOWN_COLOR)
            count_rect = count_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(count_surface, count_rect)
            
            # Draw "Get Ready!" text
            ready_text = "Get Ready!"
            ready_surface = self.instruction_font.render(ready_text, True, COUNTDOWN_COLOR)
            ready_rect = ready_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(ready_surface, ready_rect)
        
        # Draw fade overlay if transitioning
        if self.transition_timer < FADE_DURATION:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0)) 