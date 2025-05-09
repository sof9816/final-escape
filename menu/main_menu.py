"""
Main Menu for Final Escape game.
"""
import pygame
from constants import STATE_COUNTDOWN, STATE_SETTINGS, SCREEN_WIDTH, SCREEN_HEIGHT
from menu.menu_component import Menu
from settings.settings_manager import SettingsManager

class MainMenu(Menu):
    """Main menu for Final Escape."""
    
    def __init__(self, asset_loader, screen_width=None, screen_height=None):
        """Initialize the main menu.
        
        Args:
            asset_loader: AssetLoader instance for loading fonts
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        # Store screen dimensions
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        # Get assets to restore the pixel font
        assets = asset_loader.load_game_assets()
        
        # Get fonts from the asset loader
        title_font = assets["fonts"]["title"] if "fonts" in assets and "title" in assets["fonts"] else None
        item_font = assets["fonts"]["instruction"] if "fonts" in assets and "instruction" in assets["fonts"] else None
        
        # Initialize the base menu with title
        super().__init__("FINAL ESCAPE", title_font, item_font, asset_loader, self.screen_width, self.screen_height)
        
        # Title border attributes
        self.title_border_color = (0, 150, 255)  # Light blue border
        self.title_border_width = 2
        self.title_color = (255, 255, 255)  # White text
        
        # Initialize settings manager to access saved settings
        self.settings_manager = SettingsManager()
        
        # Define menu actions
        def start_game():
            print("Starting the game with settings:")
            print(f"- Difficulty: {self.settings_manager.get_difficulty()}")
            print(f"- Sound: {'ON' if self.settings_manager.get_sound_enabled() else 'OFF'}")
            print(f"- Star Opacity: {self.settings_manager.get_star_opacity()}%")
            
            # Create a visual effect for game start
            if self.select_sound and self.settings_manager.get_sound_enabled():
                self.select_sound.play()
                
            # Show notification
            self.show_notification("Launching game...", 1.0)
                
            # Return the state to transition to
            return STATE_COUNTDOWN
            
        def open_settings():
            print("Opening settings")
            if self.select_sound and self.settings_manager.get_sound_enabled():
                self.select_sound.play()
                
            # Show notification
            self.show_notification("Opening settings...", 0.8)
                
            return STATE_SETTINGS
        
        # Add menu items without keyboard shortcuts
        self.add_item("Free Escape", start_game)
        self.add_item("Story", None, enabled=False)  # Disabled option
        self.add_item("Settings", open_settings)
        
        # Attempt to center the menu if the base class (Menu) provides a 'rect' attribute
        if hasattr(self, 'rect') and isinstance(self.rect, pygame.Rect):
            self.rect.center = (self.screen_width // 2, self.screen_height // 2)
            print(f"MainMenu: Centered menu rect at {self.rect.center}")
        else:
            print("MainMenu: No rect attribute available for centering.")

        # Activate the menu by default
        self.activate()
        
        # Show welcome notification on first activation
        self.show_notification("Welcome to Final Escape!", 3.0)
    
    def render_title_with_border(self, surface, text, position):
        """Render the title text with a border.
        
        Args:
            surface: Pygame surface to draw on
            text: Title text
            position: (x, y) position for the title
        """
        # Create text surface with the title color
        text_surface = self.title_font.render(text, True, self.title_color)
        text_rect = text_surface.get_rect(center=position)
        
        # Create a slightly larger surface for the border
        border_surface = pygame.Surface((text_surface.get_width() + self.title_border_width*2, 
                                       text_surface.get_height() + self.title_border_width*2),
                                      pygame.SRCALPHA)
        
        # Draw the border by rendering the text in the border color at offset positions
        for x_offset in range(-self.title_border_width, self.title_border_width+1):
            for y_offset in range(-self.title_border_width, self.title_border_width+1):
                # Skip the center position (that will be the main text)
                if x_offset == 0 and y_offset == 0:
                    continue
                
                # Only draw the outermost pixels for a cleaner border
                if abs(x_offset) != self.title_border_width and abs(y_offset) != self.title_border_width:
                    continue
                
                border_text = self.title_font.render(text, True, self.title_border_color)
                border_surface.blit(border_text, 
                                  (self.title_border_width + x_offset, 
                                   self.title_border_width + y_offset))
        
        # Draw the main text in the center
        border_surface.blit(text_surface, (self.title_border_width, self.title_border_width))
        
        # Draw the combined surface to the main surface
        border_rect = border_surface.get_rect(center=position)
        surface.blit(border_surface, border_rect)
    
    def draw(self, surface):
        """Draw the menu with custom title rendering but otherwise use the parent class's button animations.
        
        Args:
            surface: Pygame surface to draw on
        """
        # First, apply the parent class's draw method to handle most menu elements
        # Store the original title_surface and title_rect
        original_title_surface = self.title_surface
        original_title_rect = self.title_rect
        
        # Override the title_glow_alpha value to prevent flickering
        original_title_glow_alpha = self.title_glow_alpha
        self.title_glow_alpha = 0  # Disable the glow animation
        
        # Instead of setting to None, create a transparent surface of the same size
        if self.title_surface:
            transparent_surface = pygame.Surface(self.title_surface.get_size(), pygame.SRCALPHA)
            transparent_surface.fill((0, 0, 0, 0))  # Completely transparent
            self.title_surface = transparent_surface
            
        # Draw only a semi-transparent overlay to allow stars to be visible
        if hasattr(self, 'background_alpha') and self.background_alpha > 0:
            bg_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            bg_overlay.fill((0, 0, 30, 20))  # Very transparent background
            surface.blit(bg_overlay, (0, 0))
        
        # Call parent class draw method to draw everything except the visible title
        # This will handle all the button animations
        super().draw(surface)
        
        # Restore original values
        self.title_surface = original_title_surface
        self.title_rect = original_title_rect
        self.title_glow_alpha = original_title_glow_alpha
        
        # Now draw our custom bordered title - always at full opacity
        if hasattr(self, 'title_rect') and self.title_rect:
            self.render_title_with_border(surface, self.title, self.title_rect.center)
        else:
            # Fallback position if title_rect isn't available
            self.render_title_with_border(surface, self.title, (self.screen_width // 2, 150))
    
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            Next state (STATE_COUNTDOWN, STATE_SETTINGS) or None
        """
        # Always refresh settings before handling events
        self.settings_manager = SettingsManager()  # Reload settings
        
        # Custom keyboard shortcuts
        if self.active and self.appear_progress >= 0.9 and event.type == pygame.KEYDOWN:
            # S key for settings
            if event.key == pygame.K_s:
                for item in self.items:
                    if "settings" in item.text.lower() and item.enabled:
                        if self.select_sound and self.settings_manager.get_sound_enabled():
                            self.select_sound.play()
                        return item.activate()
                        
        # Use the parent class's event handling
        return super().handle_event(event)
    
    def update(self, dt):
        """Update the menu.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            Next state or None
        """
        # Always refresh settings
        self.settings_manager = SettingsManager()
        
        # Use the parent class's update logic which includes button animations
        return super().update(dt) 