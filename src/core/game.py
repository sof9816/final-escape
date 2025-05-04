"""
Game class for Asteroid Navigator.
Manages the game loop, scene transitions, and input.
"""
import sys
import pygame
from pygame.locals import QUIT
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FADE_DURATION
from src.core.asset_loader import AssetLoader
from src.scenes.start_scene import StartScene
from src.scenes.countdown_scene import CountdownScene
from src.scenes.game_scene import GameScene
from src.scenes.game_over_scene import GameOverScene
from src.utils.helpers import change_music

class Game:
    """Main game class that manages the game loop and scenes."""
    
    def __init__(self):
        """Initialize the game."""
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()  # Initialize sound
        
        # Create the screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroid Navigator")
        
        # Create clock for timing
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Set up joystick if available
        self.joystick = None
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)  # Use first joystick
            self.joystick.init()
            print(f"Initialized Joystick: {self.joystick.get_name()}")
        else:
            print("No joystick detected.")
        
        # Load assets
        self.assets = AssetLoader()
        self.assets.load_all()
        
        # Start menu music immediately (before scene creation)
        change_music(self.assets.get_sound("menu_music"))
        
        # Create initial scenes
        self.scenes = self._create_scenes()
        
        # Set current scene
        self.current_scene_key = "START"
        self.current_scene = self.scenes[self.current_scene_key]
        
        
    def _create_scenes(self):
        """Create and return all game scenes."""
        return {
            "START": StartScene(self.screen, self.assets, skip_music=True),  # Skip music on initial creation
            "COUNTDOWN": CountdownScene(self.screen, self.assets),
            "PLAYING": GameScene(self.screen, self.assets),
            "GAME_OVER": None  # Created dynamically when game over with score
        }
        
    def run(self):
        """Run the main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0
            if dt > 0.1:  # Prevent large dt spikes if lagging
                dt = 0.1
                
            # Handle events
            events = pygame.event.get()
            self.handle_events(events)
            
            # Update current scene
            self.current_scene.update(dt, self.joystick)
            
            # Draw current scene
            self.current_scene.draw()
            
            # Check for scene change
            self.check_scene_transition()
            
            # Update display
            pygame.display.flip()
        
        # Clean up and exit
        pygame.quit()
        sys.exit()
        
    def handle_events(self, events):
        """
        Handle global events and pass to current scene.
        
        Args:
            events: List of pygame events
        """
        for event in events:
            if event.type == QUIT:
                self.running = False
                
        # Let the current scene handle events too
        if self.current_scene.process_events(events):
            self.running = False
            
    def check_scene_transition(self):
        """Check if the current scene is done and transition if necessary."""
        next_scene_key = self.current_scene.get_next_scene()
        
        if next_scene_key:
            # Scene is ready to transition
            
            # Special case: When going from GAME_OVER to START
            if self.current_scene_key == "GAME_OVER" and next_scene_key == "START":
                # Completely reset the game
                self.scenes = self._create_scenes()
                self.current_scene_key = next_scene_key
                self.current_scene = self.scenes[self.current_scene_key]
                
                # Start the menu music
                change_music(self.assets.get_sound("menu_music"))
               
            
            # Special case: When going from START to COUNTDOWN
            if self.current_scene_key == "START" and next_scene_key == "COUNTDOWN":
                # Start music
                change_music(self.assets.get_sound("game_music"))
                # Ensure we're using a fresh countdown scene
                self.scenes["COUNTDOWN"] = CountdownScene(self.screen, self.assets)
            # Special case: When going from COUNTDOWN to PLAYING
            elif self.current_scene_key == "COUNTDOWN" and next_scene_key == "PLAYING":
                # Create a fresh PLAYING scene
                self.scenes["PLAYING"] = GameScene(self.screen, self.assets)
            
            # Create GAME_OVER scene dynamically when needed
            elif next_scene_key == "GAME_OVER":
                # Special case: create game over scene with final score
                score = 0
                if isinstance(self.current_scene, GameScene):
                    score = self.current_scene.get_score()
                self.scenes["GAME_OVER"] = GameOverScene(self.screen, self.assets, score)
            
            # Switch to the next scene
            self.current_scene_key = next_scene_key
            self.current_scene = self.scenes[self.current_scene_key]
            
    def reset_game(self):
        """Reset the game by recreating all scenes."""
        # Recreate all scenes
        self.scenes = self._create_scenes() 