"""
Asset loading functionality for Asteroid Navigator.
Centralizes loading of images, sounds and fonts.
"""
import os
import pygame
from src.constants import (
    PLAYER_IMG_PATH, ASTEROID_IMG_DIR, LOGO_IMG_PATH, 
    MENU_MUSIC_PATH, GAME_MUSIC_PATH, GAME_OVER_MUSIC_PATH,
    PLAYER_SIZE, SCORE_FONT_SIZE, GAME_OVER_FONT_SIZE, 
    TITLE_FONT_SIZE, INSTRUCTION_FONT_SIZE, COUNTDOWN_FONT_SIZE,
    SCREEN_WIDTH, SCREEN_HEIGHT
)

class AssetLoader:
    """Handles loading and storing of game assets."""
    
    def __init__(self):
        """Initialize the asset loader."""
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.asteroid_images = {}
        # Determine which set of assets to load based on screen resolution
        self.resolution_suffix = self._determine_resolution_suffix()
        print(f"Using resolution suffix: {self.resolution_suffix} for screen {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    def _determine_resolution_suffix(self):
        """
        Determine which resolution of assets to load based on screen size.
        
        Returns:
            String suffix for asset filenames: "_small", "_medium", or "" (for full size)
        """
        if SCREEN_WIDTH <= 640 and SCREEN_HEIGHT <= 480:
            return "_small"  # Use small assets (e.g. player_small.png)
        elif SCREEN_WIDTH <= 800 and SCREEN_HEIGHT <= 600:
            return "_medium"  # Use medium assets (e.g. player_medium.png)
        else:
            return ""  # Use default/full size assets (e.g. player.png)

    def load_all(self):
        """Load all game assets."""
        self._load_images()
        self._load_sounds()
        self._load_fonts()
        
    def _load_images(self):
        """Load all game images."""
        try:
            # Load and convert images with appropriate resolution
            self.images["player"] = self._load_image_with_resolution(PLAYER_IMG_PATH)
            self.images["logo"] = self._load_image_with_resolution(LOGO_IMG_PATH)
            
            # Load all asteroid images (a0-a6)
            for i in range(7):  # 0 to 6
                img_path = os.path.join(ASTEROID_IMG_DIR, f"a{i}.png")
                self.asteroid_images[i] = self._load_image_with_resolution(img_path)
                
        except pygame.error as e:
            print(f"Error loading image: {e}")
            # Create fallback surfaces if images fail to load
            self.images["player"] = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.images["player"].fill((0, 255, 0))  # Green fallback
            
            # Create fallback surfaces for logo
            self.images["logo"] = pygame.Surface((400, 200))
            self.images["logo"].fill((255, 255, 255))
            
            # Create fallback surfaces for asteroids
            for i in range(7):  # 0 to 6
                fallback = pygame.Surface((60, 60))
                fallback.set_colorkey((0, 0, 0))
                # Use different colors for different asteroid types in fallback
                color = (128 + i * 18, 128 - i * 18, 128)
                pygame.draw.ellipse(fallback, color, (0, 0, 60, 60))
                self.asteroid_images[i] = fallback

    def _load_image_with_resolution(self, image_path):
        """
        Load the appropriate resolution of an image based on the screen size.
        
        Args:
            image_path: Base path to the image file
            
        Returns:
            Loaded pygame.Surface
        """
        # Split the path into name and extension
        name, ext = os.path.splitext(image_path)
        
        # Create new path with resolution suffix before extension
        resolution_path = f"{name}{self.resolution_suffix}{ext}"
        
        # Try to load the resolution-specific version first
        try:
            if os.path.exists(resolution_path):
                print(f"Loading resolution-specific image: {resolution_path}")
                return pygame.image.load(resolution_path).convert_alpha()
            else:
                # Fall back to original image if resolution-specific one doesn't exist
                print(f"Resolution-specific image not found, using: {image_path}")
                return pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading image {resolution_path} or {image_path}: {e}")
            # Let the calling function handle the fallback
            raise

    def _load_sounds(self):
        """Load all game sounds and music."""
        try:
            self.sounds["menu_music"] = MENU_MUSIC_PATH
            self.sounds["game_music"] = GAME_MUSIC_PATH 
            self.sounds["game_over_music"] = GAME_OVER_MUSIC_PATH
        except Exception as e:
            print(f"Error loading sound files: {e}")

    def _load_fonts(self):
        """Load all game fonts."""
        # Use default font
        default_font_path = None  # Use pygame default
        self.fonts["score"] = pygame.font.Font(default_font_path, SCORE_FONT_SIZE)
        self.fonts["game_over"] = pygame.font.Font(default_font_path, GAME_OVER_FONT_SIZE)
        self.fonts["title"] = pygame.font.Font(default_font_path, TITLE_FONT_SIZE)
        self.fonts["instruction"] = pygame.font.Font(default_font_path, INSTRUCTION_FONT_SIZE)
        self.fonts["countdown"] = pygame.font.Font(default_font_path, COUNTDOWN_FONT_SIZE)

    def get_image(self, name):
        """Get an image by name."""
        return self.images.get(name)

    def get_asteroid_image(self, index):
        """Get an asteroid image by index."""
        return self.asteroid_images.get(index)
        
    def get_sound(self, name):
        """Get a sound by name."""
        return self.sounds.get(name)
        
    def get_font(self, name):
        """Get a font by name."""
        return self.fonts.get(name) 