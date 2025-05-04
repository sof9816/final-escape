"""
Start/menu scene for Asteroid Navigator.
"""
import pygame
from pygame.locals import KEYDOWN, JOYBUTTONDOWN
from src.constants import BACKGROUND_COLOR, SCORE_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, FADE_DURATION
from src.scenes.scene import Scene
from src.entities.star import StarField
from src.entities.menu_objects import MenuAsteroid, MenuPlayer
from src.utils.helpers import change_music, create_fade_surface, fade_in

class StartScene(Scene):
    """Start/menu scene with title and animation."""
    
    def __init__(self, screen, assets, skip_music=False):
        """
        Initialize the start scene.
        
        Args:
            screen: Pygame display surface
            assets: AssetLoader instance
            skip_music: If True, don't start the music (used when music is already playing)
        """
        super().__init__(screen, assets)
        self.next_scene = "COUNTDOWN"
        
        # Create starfield
        self.star_field = StarField(100, SCREEN_WIDTH)
        
        # Create menu elements
        self.menu_asteroids = [MenuAsteroid(assets.asteroid_images) for _ in range(10)]
        self.menu_player = MenuPlayer(assets.get_image("player"))
        
        # Setup fade transition
        self.fade_surface = create_fade_surface(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.transition_timer = 0
        self.fade_alpha = 255
        
        # Get fonts
        self.instruction_font = assets.get_font("instruction")
        
        # Start music (only if not skipped)
        if not skip_music:
            change_music(assets.get_sound("menu_music"))
        
        # Prepare text
        self.start_text = self.instruction_font.render(
            "Press any key or joystick button to start", 
            True, 
            SCORE_COLOR
        )
        self.start_text_rect = self.start_text.get_rect(
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
                # Begin transition to countdown
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
        self.menu_player.update(dt)
        
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
        self.menu_player.draw(self.screen)
        
        # Draw logo
        logo_rect = self.assets.get_image("logo").get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        )
        self.screen.blit(self.assets.get_image("logo"), logo_rect)
        
        # Draw instructions
        self.screen.blit(self.start_text, self.start_text_rect)
        
        # Draw fade overlay if transitioning
        if self.transition_timer < FADE_DURATION:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0)) 