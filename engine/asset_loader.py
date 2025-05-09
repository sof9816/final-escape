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
    INSTRUCTION_FONT_SIZE, COUNTDOWN_FONT_SIZE,
    POWERUP_TYPES, POWERUP_SIZE,
    SOUND_POWERUP_COLLECT, SOUND_EXPLOSION_MAIN, SOUND_ASTEROID_EXPLODE
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
            
    def load_image(self, relative_path, convert_alpha=True, scale=None):
        """
        Load an image from a path relative to 'assets/images/{resolution_dir}/', 
        applying conversions and scaling if needed.
        
        Args:
            relative_path: Relative path to the image file (e.g., "ship.png", "power-ups/boom.png")
            convert_alpha: Whether to convert the image for alpha transparency
            scale: Optional tuple (width, height) to scale the image
            
        Returns:
            Loaded and processed pygame.Surface
        """
        # Determine how to construct the full_path based on relative_path format
        if relative_path.startswith("assets/images/"):
            # "Old style" or pre-constructed path - use mostly as is.
            # This assumes self.image_size_dir might be part of it, or it's a direct 1x path.
            full_path = relative_path
            # We could add a check here: if self.image_size_dir is not in full_path and it's not 1x, print a warning.
            # For now, assume if it starts with "assets/images/", it's intended as a specific path.
            print(f"AssetLoader: Using provided path for image: {full_path}")
        else:
            # "New style" - path is relative to the current resolution directory
            full_path = os.path.join("assets/images", self.image_size_dir, relative_path)
            # print(f"AssetLoader: Constructed path for image: {full_path} (from relative: '{relative_path}')")

        # Check if the resolution-specific asset exists
        if not os.path.exists(full_path):
            # If the original path was already an "old style" specific path, don't try 1x fallback again unless it was NOT a 1x path.
            # If it was a "new style" constructed path, try 1x.
            attempt_1x_fallback = not relative_path.startswith("assets/images/") or not "/1x/" in relative_path
            
            if attempt_1x_fallback:
                print(f"AssetLoader: Image not found at '{full_path}'. Attempting 1x fallback.")
                fallback_path = os.path.join("assets/images", "1x", relative_path) # For new style, relative_path is simple
                if relative_path.startswith("assets/images/"): # If old style, need to reconstruct 1x path carefully
                    # e.g., assets/images/2x/ship.png -> assets/images/1x/ship.png
                    parts = relative_path.split(os.sep)
                    if len(parts) > 2 and parts[0] == "assets" and parts[1] == "images":
                        parts[2] = "1x"
                        fallback_path = os.path.join(*parts)
                    else: # Cannot reliably make a 1x path from this old style
                        fallback_path = None 

                if fallback_path and os.path.exists(fallback_path):
                    print(f"AssetLoader: Falling back to 1x: {fallback_path}")
                    full_path = fallback_path
                else:
                    print(f"AssetLoader: Image also not found in 1x fallback (tried '{fallback_path if fallback_path else 'N/A'}').")
                    print(f"AssetLoader: Using magenta fallback for '{relative_path}' scaled to {scale if scale else 'original'}.")
                    fallback_surface = pygame.Surface(scale if scale else (50, 50))
                    fallback_surface.fill((255, 0, 255))
                    error_cache_key = f"{relative_path}_{self.image_size_dir}_{scale}_error"
                    self.images[error_cache_key] = fallback_surface
                    return fallback_surface
            else:
                # Path was specific (e.g. assets/images/1x/file.png) and not found, no further fallback.
                print(f"AssetLoader: Specific path '{full_path}' not found. Using magenta fallback for '{relative_path}'.")
                fallback_surface = pygame.Surface(scale if scale else (50, 50))
                fallback_surface.fill((255, 0, 255))
                error_cache_key = f"{relative_path}_{self.image_size_dir}_{scale}_error"
                self.images[error_cache_key] = fallback_surface
                return fallback_surface

        # Check if already cached using the relative_path as part of the key for uniqueness
        cache_key = f"{relative_path}_{self.image_size_dir}_{scale}"
        if cache_key in self.images:
            return self.images[cache_key]
        
        try:
            if convert_alpha:
                image = pygame.image.load(full_path).convert_alpha()
            else:
                image = pygame.image.load(full_path).convert()
                
            if scale:
                image = pygame.transform.scale(image, scale)
                
            # Cache the loaded image
            self.images[cache_key] = image
            return image
            
        except pygame.error as e:
            print(f"Error loading image {full_path}: {e}")
            
            # Create a fallback surface
            fallback = pygame.Surface(scale if scale else (50, 50))
            fallback.fill((255, 0, 255))  # Bright magenta to indicate error
            self.images[cache_key] = fallback # Cache fallback under the specific path to avoid re-attempts
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
            # Handle case where a default system/pygame font is explicitly requested
            if name is None:
                # Attempt to load a default system font.
                # pygame.font.Font(None, size) is often used for the "default" font.
                # pygame.font.SysFont(None, size) might also work or be more explicit for system default.
                # For robustness, we can try Font(None, size) first.
                try:
                    font = pygame.font.Font(None, size)
                except pygame.error:
                    # Fallback if Font(None, size) fails (should be rare for basic default)
                    print(f"Warning: pygame.font.Font(None, {size}) failed. Trying SysFont as absolute fallback.")
                    font = pygame.font.SysFont(None, size) # This should ideally find *something*
            # Check if it's a file path (only if name is not None)
            elif os.path.exists(name):
                font = pygame.font.Font(name, size)
            else:
                # Try to use a system font if name is provided but file doesn't exist
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
            Loaded pygame.mixer.Sound or None if file doesn't exist
        """
        # Check if already cached
        if path in self.sounds:
            return self.sounds[path]
        
        # Check if the file exists
        if not os.path.exists(path):
            print(f"Sound file not found: {path}")
            self.sounds[path] = None  # Cache the missing sound to avoid repeated file checks
            return None
            
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            
            # Cache the loaded sound
            self.sounds[path] = sound
            return sound
            
        except pygame.error as e:
            print(f"Error loading sound {path}: {e}")
            self.sounds[path] = None  # Cache the failed sound to avoid repeated errors
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
        # These are now less critical as load_image constructs paths from relative_path
        # base_images_dir = "assets/images" 
        fonts_dir = "assets/fonts"
        sound_dir = "assets/sound" # Still used for sounds
        
        # Path to resolution-specific assets is handled by load_image
        # res_dir = os.path.join(base_images_dir, self.image_size_dir)
        
        # Player image relative path
        ship_relative_path = "ship.png"
        
        self.assets = {
            # Load player image (ship)
            "player_img": self.load_image(ship_relative_path, scale=(PLAYER_SIZE, PLAYER_SIZE)),
            
            # Container for asteroid images
            "asteroid_imgs": {},

            # Container for power-up images
            "powerup_imgs": {},
            
            # Music paths (direct paths, not using load_image)
            "music": {
                "menu": os.path.join(sound_dir, "Lone Knight in the Stars(Menu Scene).ogg"),
                "game": os.path.join(sound_dir, "Pixel Knight Asteroid Chase(Game Scene).ogg"),
                "game_over": os.path.join(sound_dir, "Asteroid Knight(Game Over).ogg")
            },
            
            # Sound effects
            "sounds": {
                "menu_navigate": self.load_sound(os.path.join(sound_dir, "menu_navigate.wav"), volume=0.4),
                "menu_select": self.load_sound(os.path.join(sound_dir, "menu_select.wav"), volume=0.5),
                # New sounds
                "powerup_collect": self.load_sound(SOUND_POWERUP_COLLECT, volume=0.9),
                "explosion_main": self.load_sound(SOUND_EXPLOSION_MAIN, volume=0.8),
                "asteroid_explode": self.load_sound(SOUND_ASTEROID_EXPLODE, volume=0.1)
            },
            
            # Fonts - Ensure this key exists
            "fonts": {}
        }
        
        # Initialize fonts with fallbacks first to ensure keys always exist
        default_font_regular = pygame.font.Font(None, SCORE_FONT_SIZE) # Generic default for sizes
        default_font_medium = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        default_font_bold_title = pygame.font.Font(None, TITLE_FONT_SIZE)
        default_font_bold_game_over = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
        default_font_bold_countdown = pygame.font.Font(None, COUNTDOWN_FONT_SIZE)

        self.assets["fonts"]["score"] = self.load_font(None, SCORE_FONT_SIZE) # Will use SysFont or default
        self.assets["fonts"]["game_over"] = self.load_font(None, GAME_OVER_FONT_SIZE)
        self.assets["fonts"]["title"] = self.load_font(None, TITLE_FONT_SIZE)
        self.assets["fonts"]["instruction"] = self.load_font(None, INSTRUCTION_FONT_SIZE)
        self.assets["fonts"]["countdown"] = self.load_font(None, COUNTDOWN_FONT_SIZE)

        # Load asteroid images (a0-a6)
        for i in range(7):
            a_relative_path = f"a{i}.png" # Asteroids are at the root of the res_dir
            max_size = ASTEROID_SIZES["large"]["max"] # Example scaling, adjust as needed
            # self.assets["asteroid_imgs"][i] = self.load_image(a_path, scale=(max_size, max_size))
            # The asteroid entity itself handles loading its specific image and scaling now.
            # We can pre-load them here if desired, or let entities load them.
            # For consistency with how asteroids are loaded in Asteroid class, let's remove direct loading here
            # and ensure Asteroid class uses the new load_image method correctly.
            # AssetLoader will still cache them if Asteroid class calls load_image.
            pass # Asteroid images are loaded by the Asteroid class itself using asset_loader.load_image

        # Load power-up images
        for powerup_id, details in POWERUP_TYPES.items():
            powerup_relative_path = os.path.join("power-ups", details["image_file"])
            self.assets["powerup_imgs"][powerup_id] = self.load_image(
                powerup_relative_path, 
                scale=(POWERUP_SIZE, POWERUP_SIZE)
            )
            
        # Load fonts
        try:
            # Check for custom fonts
            font_files = {
                "regular": os.path.join(fonts_dir, "PixelifySans-Regular.ttf"),
                "medium": os.path.join(fonts_dir, "PixelifySans-Medium.ttf"),
                "semibold": os.path.join(fonts_dir, "PixelifySans-SemiBold.ttf"),
                "bold": os.path.join(fonts_dir, "PixelifySans-Bold.ttf")
            }
            
            # Load fonts if they exist, overwriting the fallbacks
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
            print(f"Error loading custom fonts or creating logo: {e}. Fallback fonts will be used.")
            # Fallback logo is created
            fallback_font = pygame.font.Font(None, TITLE_FONT_SIZE)
            self.assets["logo_img"] = fallback_font.render("FINAL ESCAPE", True, (255, 255, 255))
            # Fonts have already been set to fallbacks if custom loading failed or files are missing.
        
        return self.assets
        
    def get_text_renderer(self):
        """Get the text renderer instance."""
        return self.text_renderer
        
    def get_font(self, name):
        """Get a font by name from the loaded assets."""
        if self.assets and "fonts" in self.assets and name in self.assets["fonts"]:
            return self.assets["fonts"][name]
        return pygame.font.Font(None, 30)  # Return a default font as fallback 