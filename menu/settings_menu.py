"""
Settings Menu for Final Escape game.
"""
import pygame
from constants import STATE_MENU, DIFFICULTY_LEVELS, SCREEN_WIDTH, SCREEN_HEIGHT
from menu.menu_component import Menu

class SettingItem:
    """Extended menu item specifically for settings that need left/right adjustment."""
    
    def __init__(self, title, value, description=""):
        """Initialize a setting item.
        
        Args:
            title: The setting title
            value: The current value
            description: Optional description of the setting
        """
        self.title = title
        self.value = value
        self.description = description
        
        # For rendering
        self.title_surface = None
        self.value_surface = None
        self.description_surface = None
        self.arrows_visible = False
        self.rect = None
        
    def get_display_text(self):
        """Get the text to display for this setting."""
        return f"{self.title}: {self.value}"

class SettingsMenu(Menu):
    """Settings menu for Final Escape."""
    
    def __init__(self, asset_loader, settings_manager, star_field, screen_width=None, screen_height=None):
        """Initialize the settings menu.
        
        Args:
            asset_loader: AssetLoader instance for loading fonts
            settings_manager: SettingsManager for accessing/modifying settings
            star_field: StarField instance for adjusting star opacity
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        # Store screen dimensions
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        # Get assets
        assets = asset_loader.load_game_assets()
        
        # Get fonts from the asset loader
        title_font = assets["fonts"]["title"] if "fonts" in assets and "title" in assets["fonts"] else None
        item_font = assets["fonts"]["instruction"] if "fonts" in assets and "instruction" in assets["fonts"] else None
        
        # Initialize the base menu with title
        super().__init__("SETTINGS", title_font, item_font, asset_loader, self.screen_width, self.screen_height)
        
        # Store references to manager and star field
        self.asset_loader = asset_loader
        self.settings_manager = settings_manager
        self.star_field = star_field
        
        # Additional font for descriptions (smaller)
        self.description_font = pygame.font.Font(None, 20)
        
        # Setting items - used to store additional data beyond menu items
        self.setting_items = {}
        
        # Define menu items
        self._create_menu_items()
        
        # Activate the menu by default
        self.activate()
    
    def _create_menu_items(self):
        """Create the menu items for settings."""
        # Sound toggle
        sound_enabled = self.settings_manager.get_sound_enabled()
        sound_value = 'ON' if sound_enabled else 'OFF'
        sound_description = "Toggle game sound effects and music"
        self.setting_items["sound"] = SettingItem("Sound", sound_value, sound_description)
        self.sound_item = self.add_item(self.setting_items["sound"].get_display_text(), self._toggle_sound)
        
        # Star opacity control
        opacity = self.settings_manager.get_star_opacity()
        opacity_description = "Adjust the visibility of background stars (0-100%)"
        self.setting_items["opacity"] = SettingItem("Star Opacity", f"{opacity}%", opacity_description)
        self.opacity_item = self.add_item(self.setting_items["opacity"].get_display_text(), None)
        
        # Difficulty selection
        difficulty = self.settings_manager.get_difficulty()
        difficulty_description = "Choose how challenging the asteroid field will be"
        self.setting_items["difficulty"] = SettingItem("Difficulty", difficulty, difficulty_description)
        self.difficulty_item = self.add_item(self.setting_items["difficulty"].get_display_text(), None)
        
        # Back to main menu
        self.add_item("Back to Main Menu", self._return_to_main_menu)
    
    def _toggle_sound(self):
        """Toggle sound on/off."""
        new_state = not self.settings_manager.get_sound_enabled()
        self.settings_manager.set_sound_enabled(new_state)
        
        # Update setting item and menu item text
        self.setting_items["sound"].value = 'ON' if new_state else 'OFF'
        self.sound_item.text = self.setting_items["sound"].get_display_text()
        
        # Apply setting immediately
        if new_state:
            # Unmute - get the current game music and restart it
            pygame.mixer.music.set_volume(1.0)
        else:
            # Mute
            pygame.mixer.music.set_volume(0.0)
            
        # Play sound effect if enabling sound (and if sounds loaded)
        if new_state and self.select_sound:
            self.select_sound.play()
            
        # Show confirmation notification
        self.show_notification(f"Sound: {'ON' if new_state else 'OFF'}")
            
        return None  # Don't change state
    
    def _adjust_star_opacity(self, increase=True):
        """Adjust star opacity up or down."""
        current = self.settings_manager.get_star_opacity()
        
        # Change by 10%
        step = 10
        new_value = current + step if increase else current - step
        
        # Ensure in valid range
        new_value = max(0, min(100, new_value))
        
        # Update if changed
        if new_value != current:
            self.settings_manager.set_star_opacity(new_value)
            
            # Update setting item and menu item text
            self.setting_items["opacity"].value = f"{new_value}%"
            self.opacity_item.text = self.setting_items["opacity"].get_display_text()
            
            # Apply setting immediately to star field
            # Convert percentage to opacity value (0-255)
            opacity_value = int(new_value * 255 / 100)
            for star in self.star_field.stars:
                star.opacity = opacity_value
            
            # Play navigation sound effect if available
            if self.navigate_sound:
                self.navigate_sound.play()
                
            # Show confirmation notification for significant changes (multiples of 20%)
            if new_value % 20 == 0:
                self.show_notification(f"Star Opacity: {new_value}%")
    
    def _cycle_difficulty(self, forward=True):
        """Cycle through difficulty levels."""
        current_idx = self.settings_manager.get_difficulty_index()
        
        # Move to next/previous difficulty
        if forward:
            new_idx = (current_idx + 1) % len(DIFFICULTY_LEVELS)
        else:
            new_idx = (current_idx - 1) % len(DIFFICULTY_LEVELS)
        
        # Get new difficulty
        new_difficulty = DIFFICULTY_LEVELS[new_idx]
        
        # Update setting
        self.settings_manager.set_difficulty(new_difficulty)
        
        # Update setting item and menu item text
        self.setting_items["difficulty"].value = new_difficulty
        self.difficulty_item.text = self.setting_items["difficulty"].get_display_text()
        
        # Play navigation sound effect if available
        if self.navigate_sound:
            self.navigate_sound.play()
            
        # Show confirmation notification
        self.show_notification(f"Difficulty: {new_difficulty}")
    
    def _return_to_main_menu(self):
        """Return to the main menu."""
        # Save settings before returning
        self.settings_manager.save_settings()
        
        # Show confirmation notification
        self.show_notification("Settings saved!")
        
        # Delay return to menu to show the notification
        pygame.time.delay(300)
        
        # Play selection sound if available
        if self.select_sound:
            self.select_sound.play()
            
        return STATE_MENU
    
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            Next state (STATE_MENU) or None
        """
        # First check if parent class handles this event
        result = super().handle_event(event)
        if result is not None:
            return result
        
        # Handle our custom controls for settings
        if self.active and self.appear_progress >= 0.9:
            # Keyboard controls
            if event.type == pygame.KEYDOWN:
                # Opacity adjustment with left/right arrows when opacity item selected
                if self.opacity_item.selected:
                    if event.key == pygame.K_LEFT:
                        self._adjust_star_opacity(increase=False)
                        return None
                    elif event.key == pygame.K_RIGHT:
                        self._adjust_star_opacity(increase=True)
                        return None
                
                # Difficulty cycling with left/right arrows when difficulty item selected
                if self.difficulty_item.selected:
                    if event.key == pygame.K_LEFT:
                        self._cycle_difficulty(forward=False)
                        return None
                    elif event.key == pygame.K_RIGHT:
                        self._cycle_difficulty(forward=True)
                        return None
            
            # Mouse controls for left/right arrows
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                # Check if clicking on opacity arrows
                if self.opacity_item.selected and hasattr(self, 'opacity_left_rect') and hasattr(self, 'opacity_right_rect'):
                    if self.opacity_left_rect.collidepoint(event.pos):
                        self._adjust_star_opacity(increase=False)
                        return None
                    elif self.opacity_right_rect.collidepoint(event.pos):
                        self._adjust_star_opacity(increase=True)
                        return None
                        
                # Check if clicking on difficulty arrows
                if self.difficulty_item.selected and hasattr(self, 'difficulty_left_rect') and hasattr(self, 'difficulty_right_rect'):
                    if self.difficulty_left_rect.collidepoint(event.pos):
                        self._cycle_difficulty(forward=False)
                        return None
                    elif self.difficulty_right_rect.collidepoint(event.pos):
                        self._cycle_difficulty(forward=True)
                        return None
        
        return None
    
    def update(self, dt):
        """Update the settings menu.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            Next state or None
        """
        # Update basic menu stuff (animations, etc)
        result = super().update(dt)
        
        # Update which item shows adjustment arrows
        for item_key, setting_item in self.setting_items.items():
            if item_key == "opacity" and self.opacity_item.selected:
                setting_item.arrows_visible = True
            elif item_key == "difficulty" and self.difficulty_item.selected:
                setting_item.arrows_visible = True
            else:
                setting_item.arrows_visible = False
                
        return result
    
    def draw(self, surface):
        """Draw the settings menu with increased spacing between items.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Apply appearance progress to all elements
        alpha = int(255 * self.appear_progress)
        
        # Draw a subtle background overlay
        if self.background_alpha > 0:
            bg_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            bg_overlay.fill((0, 0, 30, self.background_alpha))
            bg_overlay.set_alpha(alpha)
            surface.blit(bg_overlay, (0, 0))
        
        # Draw the title with glow effect
        if self.title_glow_alpha > 0:
            # Create glow surface
            glow_size = 5  # Pixels of glow around text
            glow_surface = pygame.Surface((
                self.title_rect.width + glow_size * 2,
                self.title_rect.height + glow_size * 2
            ), pygame.SRCALPHA)
            
            # Render the glow
            glow_color = (100, 150, 255, int(self.title_glow_alpha))
            pygame.draw.rect(
                glow_surface,
                glow_color,
                pygame.Rect(0, 0, glow_surface.get_width(), glow_surface.get_height()),
                0,
                10  # Rounded corners
            )
            
            # Apply a slight blur effect
            blurred_surface = pygame.transform.smoothscale(
                glow_surface,
                (glow_surface.get_width() - 2, glow_surface.get_height() - 2)
            )
            glow_surface = blurred_surface
            
            # Position the glow
            glow_rect = glow_surface.get_rect(center=self.title_rect.center)
            glow_surface.set_alpha(alpha)
            surface.blit(glow_surface, glow_rect)
        
        # Draw the title
        title_surface_with_alpha = self.title_surface.copy()
        title_surface_with_alpha.set_alpha(alpha)
        surface.blit(title_surface_with_alpha, self.title_rect)
        
        # Draw menu items with increased spacing
        if self.items:
            # Calculate positions with increased height for settings menu
            item_height = 70  # Increased from 40 to 70 for more spacing
            total_height = item_height * len(self.items)
            
            # Position first item lower to avoid title overlap (adjusted from 220 to 250)
            start_y = 250
            
            # Draw each menu item
            for i, item in enumerate(self.items):
                # Calculate item position with increased spacing
                item_y = start_y + i * item_height
                
                # Render the item text
                color = (200, 200, 200) if item.enabled else (100, 100, 100)
                if item.selected and item.enabled:
                    color = (255, 255, 255)
                
                # Apply the item's current alpha
                actual_alpha = min(alpha, item.alpha)
                text_surface = self.item_font.render(item.text, True, color)
                text_surface.set_alpha(actual_alpha)
                text_rect = text_surface.get_rect(center=(self.screen_width // 2, item_y))
                
                # Store the rect for mouse detection
                item.rect = text_rect.inflate(20, 10)
                
                # Draw selection indicator for selected items
                if item.selected and item.enabled:
                    # Draw a pulse effect behind the text
                    pulse_rect = item.rect.inflate(10, 5)
                    pulse_surface = pygame.Surface(pulse_rect.size, pygame.SRCALPHA)
                    pulse_color = (100, 150, 255, item.hover_alpha // 3)
                    pygame.draw.rect(pulse_surface, pulse_color, pygame.Rect(0, 0, pulse_rect.width, pulse_rect.height), 0, 5)
                    pulse_surface.set_alpha(actual_alpha)
                    surface.blit(pulse_surface, pulse_rect)
                    
                    # Draw indicator
                    indicator_color = (100, 150, 255, 200)
                    indicator_width = 5
                    indicator_height = 5
                    
                    # Left indicator
                    left_indicator = pygame.Surface((indicator_width, indicator_height), pygame.SRCALPHA)
                    left_indicator.fill(indicator_color)
                    left_rect = left_indicator.get_rect(midright=(item.rect.left - 10, item_y))
                    left_indicator.set_alpha(actual_alpha)
                    surface.blit(left_indicator, left_rect)
                    
                    # Right indicator
                    right_indicator = pygame.Surface((indicator_width, indicator_height), pygame.SRCALPHA)
                    right_indicator.fill(indicator_color)
                    right_rect = right_indicator.get_rect(midleft=(item.rect.right + 10, item_y))
                    right_indicator.set_alpha(actual_alpha)
                    surface.blit(right_indicator, right_rect)
                
                # Apply any scale animation
                if item.scale != 1.0:
                    # Scale the text (centered)
                    old_center = text_rect.center
                    scaled_width = int(text_rect.width * item.scale)
                    scaled_height = int(text_rect.height * item.scale)
                    text_surface = pygame.transform.smoothscale(text_surface, (scaled_width, scaled_height))
                    text_rect = text_surface.get_rect(center=old_center)
                
                # Draw the actual text
                surface.blit(text_surface, text_rect)
                
                # Check which special setting item this corresponds to
                setting_item = None
                for key, si in self.setting_items.items():
                    if si.get_display_text() in item.text:
                        setting_item = si
                        break
                        
                # Skip if not a setting item
                if not setting_item:
                    continue
                    
                # Draw description text with better positioning
                if setting_item.description:
                    desc_surface = self.description_font.render(setting_item.description, True, (180, 180, 180))
                    desc_rect = desc_surface.get_rect(center=(self.screen_width // 2, item_y + 25))
                    
                    # Apply opacity
                    desc_with_alpha = desc_surface.copy()
                    desc_with_alpha.set_alpha(alpha)
                    surface.blit(desc_with_alpha, desc_rect)
                
                # Draw adjustment arrows if needed
                if setting_item.arrows_visible:
                    # Calculate arrow positions
                    arrow_size = 20
                    arrow_color = (200, 200, 200)
                    arrow_gap = 140  # Distance between arrows
                    
                    # Left arrow
                    left_arrow_points = [
                        (item.rect.centerx - arrow_gap, item_y),
                        (item.rect.centerx - arrow_gap + arrow_size, item_y - arrow_size // 2),
                        (item.rect.centerx - arrow_gap + arrow_size, item_y + arrow_size // 2)
                    ]
                    
                    # Right arrow
                    right_arrow_points = [
                        (item.rect.centerx + arrow_gap, item_y),
                        (item.rect.centerx + arrow_gap - arrow_size, item_y - arrow_size // 2),
                        (item.rect.centerx + arrow_gap - arrow_size, item_y + arrow_size // 2)
                    ]
                    
                    # Create surface for arrows with opacity
                    arrow_surface = pygame.Surface((self.screen_width, 50), pygame.SRCALPHA)
                    
                    # Draw arrows on the surface
                    pygame.draw.polygon(arrow_surface, (*arrow_color, alpha), left_arrow_points)
                    pygame.draw.polygon(arrow_surface, (*arrow_color, alpha), right_arrow_points)
                    
                    # Determine which setting this is to store the arrow rects for interaction
                    if "opacity" in item.text:
                        self.opacity_left_rect = pygame.Rect(left_arrow_points[0][0] - 10, left_arrow_points[0][1] - 10, 20, 20)
                        self.opacity_right_rect = pygame.Rect(right_arrow_points[0][0] - 10, right_arrow_points[0][1] - 10, 20, 20)
                    elif "difficulty" in item.text:
                        self.difficulty_left_rect = pygame.Rect(left_arrow_points[0][0] - 10, left_arrow_points[0][1] - 10, 20, 20)
                        self.difficulty_right_rect = pygame.Rect(right_arrow_points[0][0] - 10, right_arrow_points[0][1] - 10, 20, 20)
                    
                    # Draw arrows
                    arrow_rect = arrow_surface.get_rect(center=(self.screen_width // 2, item_y))
                    surface.blit(arrow_surface, arrow_rect)
        
        # Draw help text if enabled
        if self.show_help and self.help_surfaces and self.appear_progress >= 0.8:
            help_alpha = int(min(255, alpha * (self.appear_progress - 0.8) * 5))
            help_y = self.screen_height - 20 * len(self.help_surfaces) - 10
            
            for i, help_surface in enumerate(self.help_surfaces):
                help_surface_copy = help_surface.copy()
                help_surface_copy.set_alpha(help_alpha)
                help_rect = help_surface_copy.get_rect(bottomright=(self.screen_width - 20, help_y + i * 20))
                surface.blit(help_surface_copy, help_rect)
                
        # Draw notification if exists
        if self.notification and self.notification_timer > 0:
            # Calculate fade in/out
            fade = 1.0
            if self.notification_timer < 0.5:
                fade = self.notification_timer * 2  # Fade out in last 0.5 seconds
            elif self.notification_timer > self.notification_duration - 0.5:
                fade = (self.notification_duration - self.notification_timer) * 2  # Fade in in first 0.5 seconds
                
            # Create notification text
            notif_alpha = int(200 * fade)
            notif_surface = self.item_font.render(self.notification, True, (100, 255, 100))
            notif_surface.set_alpha(notif_alpha)
            
            # Create background
            notif_rect = notif_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
            notif_bg = pygame.Surface((notif_rect.width + 20, notif_rect.height + 10), pygame.SRCALPHA)
            notif_bg.fill((0, 0, 0, int(150 * fade)))
            notif_bg_rect = notif_bg.get_rect(center=notif_rect.center)
            
            # Draw notification
            surface.blit(notif_bg, notif_bg_rect)
            surface.blit(notif_surface, notif_rect) 