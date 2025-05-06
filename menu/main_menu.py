"""
Main Menu for Final Escape game.
"""
import pygame
from constants import STATE_COUNTDOWN, STATE_SETTINGS
from menu.menu_component import Menu
from settings.settings_manager import SettingsManager

class MainMenu(Menu):
    """Main menu for Final Escape."""
    
    def __init__(self, asset_loader):
        """Initialize the main menu.
        
        Args:
            asset_loader: AssetLoader instance for loading fonts
        """
        # Get assets
        assets = asset_loader.load_game_assets()
        
        # Get fonts from the asset loader
        title_font = assets["fonts"]["title"] if "fonts" in assets and "title" in assets["fonts"] else None
        item_font = assets["fonts"]["instruction"] if "fonts" in assets and "instruction" in assets["fonts"] else None
        
        # Initialize the base menu with title
        super().__init__("FINAL ESCAPE", title_font, item_font, asset_loader)
        
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
        
        # Add menu items with keyboard shortcuts
        self.add_item("Free Escape", start_game, shortcut="Enter")
        self.add_item("Story", None, enabled=False, shortcut="Locked")  # Disabled option
        self.add_item("Settings", open_settings, shortcut="S")
        
        # Activate the menu by default
        self.activate()
        
        # Show welcome notification on first activation
        self.show_notification("Welcome to Final Escape!", 3.0)
        
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
        
        # Use the parent class's update logic
        return super().update(dt) 