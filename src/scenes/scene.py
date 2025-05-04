"""
Base Scene class for Asteroid Navigator.
"""
import pygame

class Scene:
    """Base class for all game scenes with common functionality."""
    
    def __init__(self, screen, assets):
        """
        Initialize the scene.
        
        Args:
            screen: Pygame display surface
            assets: AssetLoader instance
        """
        self.screen = screen
        self.assets = assets
        self.next_scene = None  # ID of the next scene to transition to
        self.done = False  # Set to True when the scene is complete
        
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
        pass
        
    def draw(self):
        """Draw scene elements on the screen."""
        pass
        
    def get_next_scene(self):
        """
        Get the next scene to transition to.
        
        Returns:
            str or None: ID of the next scene, or None if no transition
        """
        return self.next_scene if self.done else None 