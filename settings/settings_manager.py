"""
Settings Manager for Final Escape.
Handles saving and loading game settings from a file.
"""
import os
import json
import logging
from constants import DIFFICULTY_LEVELS

class SettingsManager:
    """
    Manages game settings and persistence.
    
    The SettingsManager provides an API for other game components to access and modify
    game settings. It also handles persisting settings between game sessions using a JSON file.
    
    Settings include:
    - sound_enabled: Controls whether game audio is enabled
    - star_opacity: Controls the opacity of background stars (0-100%)
    - difficulty: Sets the game difficulty level from the available options
    
    Usage example:
        settings = SettingsManager()
        is_sound_on = settings.get_sound_enabled()
        settings.set_star_opacity(75)
        current_difficulty = settings.get_difficulty()
    """
    
    def __init__(self, settings_dir="data"):
        """
        Initialize settings manager with default values.
        
        Args:
            settings_dir: Directory to store settings file (will be created if it doesn't exist)
        """
        # Ensure settings directory exists
        self.settings_dir = settings_dir
        os.makedirs(self.settings_dir, exist_ok=True)
        
        self.settings_path = os.path.join(self.settings_dir, "settings.json")
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("SettingsManager")
        
        # Default settings
        self.default_settings = {
            "sound_enabled": True,
            "star_opacity": 60,  # Percentage (0-100)
            "difficulty": "Normal Space"  # Default to middle difficulty
        }
        
        # Current settings (will be loaded from file if it exists)
        self.settings = self.default_settings.copy()
        
        # Load settings from file if it exists
        self.load_settings()
    
    def load_settings(self):
        """
        Load settings from file.
        
        If the settings file doesn't exist or is invalid, defaults will be used.
        """
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    loaded_settings = json.load(f)
                    
                    # Update settings with loaded values
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
                            
                    # Validate settings
                    self._validate_settings()
                    self.logger.info(f"Settings loaded from {self.settings_path}")
            else:
                self.logger.info("No settings file found, using defaults")
                # Save defaults to create the file
                self.save_settings()
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in settings file {self.settings_path}, using defaults")
            self.settings = self.default_settings.copy()
            # Backup the corrupted file and save defaults
            if os.path.exists(self.settings_path):
                backup_path = f"{self.settings_path}.backup"
                try:
                    os.rename(self.settings_path, backup_path)
                    self.logger.info(f"Corrupted settings file backed up to {backup_path}")
                except Exception as e:
                    self.logger.error(f"Failed to backup corrupted settings file: {e}")
            self.save_settings()
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}, using defaults")
            self.settings = self.default_settings.copy()
    
    def save_settings(self):
        """
        Save settings to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(self.settings_dir, exist_ok=True)
            
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.logger.info(f"Settings saved to {self.settings_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False
    
    def reset_to_defaults(self):
        """
        Reset all settings to their default values.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def _validate_settings(self):
        """Validate and fix any invalid settings."""
        # Check sound_enabled is boolean
        if not isinstance(self.settings["sound_enabled"], bool):
            self.logger.warning(f"Invalid sound_enabled value: {self.settings['sound_enabled']}, using default")
            self.settings["sound_enabled"] = self.default_settings["sound_enabled"]
            
        # Check star_opacity is in valid range
        if not isinstance(self.settings["star_opacity"], (int, float)) or \
           self.settings["star_opacity"] < 0 or self.settings["star_opacity"] > 100:
            self.logger.warning(f"Invalid star_opacity value: {self.settings['star_opacity']}, using default")
            self.settings["star_opacity"] = self.default_settings["star_opacity"]
            
        # Check difficulty is valid
        if self.settings["difficulty"] not in DIFFICULTY_LEVELS:
            self.logger.warning(f"Invalid difficulty value: {self.settings['difficulty']}, using default")
            self.settings["difficulty"] = self.default_settings["difficulty"]
    
    def get_sound_enabled(self):
        """
        Get sound enabled setting.
        
        Returns:
            bool: True if sound is enabled, False otherwise
        """
        return self.settings["sound_enabled"]
    
    def set_sound_enabled(self, enabled):
        """
        Set sound enabled setting.
        
        Args:
            enabled: Boolean indicating if sound should be enabled
            
        Returns:
            bool: True if setting was changed, False otherwise
        """
        enabled = bool(enabled)
        if self.settings["sound_enabled"] != enabled:
            self.settings["sound_enabled"] = enabled
            return self.save_settings()
        return True  # No change needed
    
    def get_star_opacity(self):
        """
        Get star opacity setting (0-100).
        
        Returns:
            float: Star opacity percentage
        """
        return self.settings["star_opacity"]
    
    def set_star_opacity(self, opacity):
        """
        Set star opacity setting.
        
        Args:
            opacity: Star opacity percentage (0-100)
            
        Returns:
            bool: True if setting was changed, False otherwise
        """
        # Ensure value is in valid range
        opacity = max(0, min(100, opacity))
        
        if self.settings["star_opacity"] != opacity:
            self.settings["star_opacity"] = opacity
            return self.save_settings()
        return True  # No change needed
    
    def get_difficulty(self):
        """
        Get difficulty setting.
        
        Returns:
            str: Difficulty level name
        """
        return self.settings["difficulty"]
    
    def set_difficulty(self, difficulty):
        """
        Set difficulty setting.
        
        Args:
            difficulty: Difficulty level name
            
        Returns:
            bool: True if setting was changed, False otherwise
        """
        if difficulty in DIFFICULTY_LEVELS and self.settings["difficulty"] != difficulty:
            self.settings["difficulty"] = difficulty
            return self.save_settings()
        return True  # Either no change needed or invalid difficulty
    
    def get_difficulty_index(self):
        """
        Get the index of the current difficulty level.
        
        Returns:
            int: Index of current difficulty in DIFFICULTY_LEVELS
        """
        try:
            return DIFFICULTY_LEVELS.index(self.settings["difficulty"])
        except ValueError:
            # Default to middle difficulty if invalid
            self.logger.warning(f"Invalid difficulty '{self.settings['difficulty']}', resetting to default")
            self.settings["difficulty"] = self.default_settings["difficulty"]
            return DIFFICULTY_LEVELS.index(self.settings["difficulty"]) 