"""
Asset loader for Final Escape.
Handles loading and caching of game assets like images and sounds,
with support for multiple image resolutions based on screen size.
"""
import os
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SIZE, ASTEROID_SIZES,
    SCORE_FONT_SIZE, GAME_OVER_FONT_SIZE, TITLE_FONT_SIZE, 
    INSTRUCTION_FONT_SIZE, COUNTDOWN_FONT_SIZE
)

class AssetLoader:
    """
    Manages loading, scaling, and caching of game assets.
    """
    def __init__(self):
        self.images = {}  # Cache for loaded images
        self.sounds = {}  # Cache for loaded sounds
        self.music = {}   # Cache for music paths
        self.fonts = {}   # Cache for fonts
        self.text_renderer = None  # Will be set by the Game class
        self.assets = None  # Will be populated by load_game_assets
        
        # Determine appropriate image size based on screen dimensions
        if SCREEN_WIDTH <= 640:
            self.image_size_dir = "1x"
        elif SCREEN_WIDTH <= 800:
            self.image_size_dir = "2x"
        else:
            self.image_size_dir = "3x"
            
        print(f"Using {self.image_size_dir} image assets for screen size {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        
        # Initialize Pygame if not already done
        if not pygame.get_init():
            pygame.init()
        
        # Initialize the mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
    def load_image(self, path, convert_alpha=True, scale=None, use_size_dir=False):
        """
        Load an image from the specified path, applying conversions and scaling if needed.
        
        Args:
            path: Path to the image file
            convert_alpha: Whether to convert the image for alpha transparency
            scale: Optional tuple (width, height) to scale the image
            use_size_dir: Whether to use the size directory (1x, 2x, 3x) based on screen resolution
            
        Returns:
            Loaded and processed pygame.Surface
        """
        # Modify path for resolution-specific assets if needed
        if use_size_dir:
            # Extract base directory and filename
            base_dir = os.path.dirname(path)
            filename = os.path.basename(path)
            
            # Create new path with size directory
            resolution_path = os.path.join(base_dir, self.image_size_dir, filename)
            
            # Use resolution path if it exists, otherwise fall back to original
            if os.path.exists(resolution_path):
                path = resolution_path
            else:
                print(f"Warning: Resolution-specific asset not found: {resolution_path}")
        
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
    
    def load_font(self, name, size):
        """
        Load a font with caching.
        
        Args:
            name: Font name or path
            size: Font size
            
        Returns:
            Loaded pygame.font.Font
        """
        # Check if already cached
        cache_key = f"{name}_{size}"
        if cache_key in self.fonts:
            return self.fonts[cache_key]
        
        try:
            # Check if it's a file path
            if os.path.exists(name):
                font = pygame.font.Font(name, size)
            else:
                # Try to use a system font
                font = pygame.font.SysFont(name, size)
                
            # Cache the loaded font
            self.fonts[cache_key] = font
            return font
            
        except pygame.error as e:
            print(f"Error loading font {name}: {e}")
            
            # Return a default font as fallback
            return pygame.font.Font(None, size)
    
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
    
    def create_text_logo(self, text="FINAL ESCAPE", size=TITLE_FONT_SIZE, color=(255, 255, 255)):
        """
        Create a text-based logo with glow effects.
        
        Args:
            text: The text to render as logo
            size: Font size
            color: Main text color
            
        Returns:
            Rendered logo surface
        """
        try:
            # Try to load the bold font for the logo
            font_path = "assets/fonts/PixelifySans-Bold.ttf"
            if os.path.exists(font_path):
                logo_font = self.load_font(font_path, size)
            else:
                logo_font = pygame.font.Font(None, size)
                
            # Create the main text surface
            text_surface = logo_font.render(text, True, color)
            
            # Create a slightly larger surface to add a glow/shadow effect
            padding = 20
            logo_width = text_surface.get_width() + padding * 2
            logo_height = text_surface.get_height() + padding * 2
            
            # Create the logo surface with alpha channel for glow effects
            logo_surface = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
            
            # Center the text on the surface
            text_pos = ((logo_width - text_surface.get_width()) // 2, 
                        (logo_height - text_surface.get_height()) // 2)
            
            # Add a glow effect
            glow_colors = [
                (100, 100, 255, 100),  # Light blue with alpha
                (80, 80, 200, 150),    # Medium blue with alpha
                (60, 60, 150, 200)     # Darker blue with alpha
            ]
            
            for i, glow_color in enumerate(glow_colors):
                offset = 3 - i
                glow_text = logo_font.render(text, True, glow_color)
                logo_surface.blit(glow_text, (text_pos[0] + offset, text_pos[1] + offset))
            
            # Draw the main text on top
            logo_surface.blit(text_surface, text_pos)
            
            return logo_surface
            
        except Exception as e:
            print(f"Error creating text logo: {e}")
            # Return a simple text surface as fallback
            fallback_font = pygame.font.Font(None, size)
            return fallback_font.render(text, True, color)
    
    def load_game_assets(self):
        """
        Load all game assets at once.
        
        Returns:
            Dictionary containing all loaded assets
        """
        # Base asset paths
        base_images_dir = "assets/images"
        fonts_dir = "assets/fonts"
        sound_dir = "assets/sound"
        
        # Path to resolution-specific assets
        res_dir = os.path.join(base_images_dir, self.image_size_dir)
        
        # Resolution-specific player and asteroid images
        ship_path = os.path.join(res_dir, "ship.png")
        
        self.assets = {
            # Load player image (ship) from the appropriate resolution directory
            "player_img": self.load_image(ship_path, scale=(PLAYER_SIZE, PLAYER_SIZE)),
            
            # Container for asteroid images
            "asteroid_imgs": {},
            
            # Music paths
            "music": {
                "menu": os.path.join(sound_dir, "Lone Knight in the Stars(Menu Scene).ogg"),
                "game": os.path.join(sound_dir, "Pixel Knight Asteroid Chase(Game Scene).ogg"),
                "game_over": os.path.join(sound_dir, "Asteroid Knight(Game Over).ogg")
            },
            
            # Fonts
            "fonts": {}
        }
        
        # Load asteroid images (a0-a6) from the appropriate resolution directory
        for i in range(7):
            a_path = os.path.join(res_dir, f"a{i}.png")
            max_size = ASTEROID_SIZES["large"]["max"]
            self.assets["asteroid_imgs"][i] = self.load_image(a_path, scale=(max_size, max_size))
            
        # Load fonts
        try:
            # Check for custom fonts
            font_files = {
                "regular": os.path.join(fonts_dir, "PixelifySans-Regular.ttf"),
                "medium": os.path.join(fonts_dir, "PixelifySans-Medium.ttf"),
                "semibold": os.path.join(fonts_dir, "PixelifySans-SemiBold.ttf"),
                "bold": os.path.join(fonts_dir, "PixelifySans-Bold.ttf")
            }
            
            # Load fonts if they exist
            self.assets["fonts"]["score"] = self.load_font(
                font_files["regular"] if os.path.exists(font_files["regular"]) else None, 
                SCORE_FONT_SIZE
            )
            
            self.assets["fonts"]["game_over"] = self.load_font(
                font_files["bold"] if os.path.exists(font_files["bold"]) else None, 
                GAME_OVER_FONT_SIZE
            )
            
            self.assets["fonts"]["title"] = self.load_font(
                font_files["bold"] if os.path.exists(font_files["bold"]) else None, 
                TITLE_FONT_SIZE
            )
            
            self.assets["fonts"]["instruction"] = self.load_font(
                font_files["medium"] if os.path.exists(font_files["medium"]) else None, 
                INSTRUCTION_FONT_SIZE
            )
            
            self.assets["fonts"]["countdown"] = self.load_font(
                font_files["bold"] if os.path.exists(font_files["bold"]) else None, 
                COUNTDOWN_FONT_SIZE
            )
            
            # Create text logo
            self.assets["logo_img"] = self.create_text_logo("FINAL ESCAPE")
            
        except Exception as e:
            print(f"Error loading fonts or creating logo: {e}")
            # Create a fallback logo
            fallback_font = pygame.font.Font(None, TITLE_FONT_SIZE)
            self.assets["logo_img"] = fallback_font.render("FINAL ESCAPE", True, (255, 255, 255))
        
        return self.assets
        
    def get_text_renderer(self):
        """Get the text renderer instance."""
        return self.text_renderer
        
    def get_font(self, name):
        """Get a font by name from the loaded assets."""
        if self.assets and "fonts" in self.assets and name in self.assets["fonts"]:
            return self.assets["fonts"][name]
        return pygame.font.Font(None, 30)  # Return a default font as fallback 