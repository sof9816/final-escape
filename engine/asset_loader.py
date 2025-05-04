"""
Asset loader for the Asteroid Navigator game.
Handles loading and caching of game assets like images and sounds.
"""
import os
import pygame
from constants import PLAYER_SIZE, ASTEROID_SIZES
from constants import (
    PLAYER_IMAGE_PATH, LOGO_IMAGE_PATH, ASTEROID_IMAGE_PATTERN,
    MENU_MUSIC_PATH, GAME_MUSIC_PATH, GAME_OVER_MUSIC_PATH
)

class AssetLoader:
    """
    Manages loading, scaling, and caching of game assets.
    """
    def __init__(self):
        self.images = {}  # Cache for loaded images
        self.sounds = {}  # Cache for loaded sounds
        self.music = {}   # Cache for music paths
        
        # Initialize Pygame if not already done
        if not pygame.get_init():
            pygame.init()
        
        # Initialize the mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
    def load_image(self, path, convert_alpha=True, scale=None):
        """
        Load an image from the specified path, applying conversions and scaling if needed.
        
        Args:
            path: Path to the image file
            convert_alpha: Whether to convert the image for alpha transparency
            scale: Optional tuple (width, height) to scale the image
            
        Returns:
            Loaded and processed pygame.Surface
        """
        # Check if already cached
        cache_key = f"{path}_{scale}"
        if cache_key in self.images:
            return self.images[cache_key]
        
        try:
            if convert_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
                
            if scale:
                image = pygame.transform.scale(image, scale)
                
            # Cache the loaded image
            self.images[cache_key] = image
            return image
            
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
            
            # Create a fallback surface
            fallback = pygame.Surface(scale if scale else (50, 50))
            fallback.fill((255, 0, 255))  # Bright magenta to indicate error
            return fallback
    
    def load_sound(self, path, volume=1.0):
        """
        Load a sound effect from the specified path.
        
        Args:
            path: Path to the sound file
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            Loaded pygame.mixer.Sound
        """
        # Check if already cached
        if path in self.sounds:
            return self.sounds[path]
        
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            
            # Cache the loaded sound
            self.sounds[path] = sound
            return sound
            
        except pygame.error as e:
            print(f"Error loading sound {path}: {e}")
            return None
    
    def play_music(self, music_path, volume=0.5, loops=-1, fade_ms=1000):
        """
        Start playing music with optional fade-in.
        
        Args:
            music_path: Path to the music file
            volume: Volume level (0.0 to 1.0)
            loops: Number of times to loop (-1 for infinite)
            fade_ms: Fade-in time in milliseconds
        """
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
            pygame.time.delay(fade_ms // 2)  # Wait for half the fade out time
            
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            
        except pygame.error as e:
            print(f"Error playing music {music_path}: {e}")
    
    def stop_music(self, fade_ms=1000):
        """
        Stop the currently playing music with fade-out.
        
        Args:
            fade_ms: Fade-out time in milliseconds
        """
        pygame.mixer.music.fadeout(fade_ms)
    
    def load_game_assets(self):
        """
        Load all game assets at once.
        
        Returns:
            Dictionary containing all loaded assets
        """
        assets = {
            "player_img": self.load_image(PLAYER_IMAGE_PATH, scale=(PLAYER_SIZE, PLAYER_SIZE)),
            "logo_img": self.load_image(LOGO_IMAGE_PATH),
            "asteroid_imgs": {},
            "music": {
                "menu": MENU_MUSIC_PATH,
                "game": GAME_MUSIC_PATH,
                "game_over": GAME_OVER_MUSIC_PATH
            }
        }
        
        # Load asteroid images (a0-a6)
        for i in range(7):
            path = ASTEROID_IMAGE_PATTERN.format(i)
            max_size = ASTEROID_SIZES["large"]["max"]
            assets["asteroid_imgs"][i] = self.load_image(path, scale=(max_size, max_size))
        
        return assets 