"""
Base Menu Component for Final Escape game.
"""
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR,
    TITLE_FONT_SIZE, INSTRUCTION_FONT_SIZE, MENU_SELECT_SOUND_PATH,
    MENU_NAVIGATE_SOUND_PATH
)

class MenuItem:
    """A single item/option in a menu."""
    
    def __init__(self, text, action=None, enabled=True, shortcut=None):
        """Initialize a menu item.
        
        Args:
            text: Display text for the menu item
            action: Callback function to execute when selected
            enabled: Whether the item is enabled and selectable
            shortcut: Optional keyboard shortcut hint to display (e.g., "ESC")
        """
        self.text = text
        self.action = action
        self.enabled = enabled
        self.shortcut = shortcut
        self.selected = False
        self.hover_alpha = 0  # For pulsing effect when selected
        self.hover_direction = 1  # 1 for increasing, -1 for decreasing
        self.hover_speed = 400  # Alpha change per second
        self.scale = 1.0  # For scaling effect when selected
        self.target_scale = 1.0  # Target scale for smooth animation
        self.scale_speed = 3.0  # Scale change per second
        self.rect = None  # Will be set when drawn
        
        # For smooth transition
        self.alpha = 0
        self.target_alpha = 255
        self.alpha_speed = 800  # Alpha change per second
    
    def update(self, dt):
        """Update the menu item's visual state.
        
        Args:
            dt: Time delta in seconds
        """
        # Smooth alpha transition
        if self.alpha != self.target_alpha:
            self.alpha += (self.target_alpha - self.alpha) * min(1.0, dt * 5)
            if abs(self.alpha - self.target_alpha) < 1:
                self.alpha = self.target_alpha
        
        if self.selected:
            # Pulse the selected item
            self.hover_alpha += self.hover_direction * self.hover_speed * dt
            if self.hover_alpha >= 255:
                self.hover_alpha = 255
                self.hover_direction = -1
            elif self.hover_alpha <= 100:
                self.hover_alpha = 100
                self.hover_direction = 1
                
            # Animate scale
            self.target_scale = 1.1  # Slightly larger when selected
        else:
            self.hover_alpha = 0
            self.hover_direction = 1
            self.target_scale = 1.0  # Normal size when not selected
        
        # Smoothly animate the scale
        if abs(self.scale - self.target_scale) > 0.01:
            self.scale += (self.target_scale - self.scale) * self.scale_speed * dt

    def select(self):
        """Mark this item as selected."""
        if self.enabled and not self.selected:
            self.selected = True
            return True
        return False
    
    def deselect(self):
        """Mark this item as not selected."""
        was_selected = self.selected
        self.selected = False
        return was_selected
    
    def activate(self):
        """Execute the menu item's action if enabled."""
        if self.enabled and self.action:
            return self.action()
        return None
        
    def contains_point(self, point):
        """Check if this menu item contains the given point.
        
        Args:
            point: (x, y) tuple to check
            
        Returns:
            bool: True if the point is inside this menu item's rect
        """
        return self.rect is not None and self.rect.collidepoint(point)


class Menu:
    """Base class for all menu screens in the game."""
    
    def __init__(self, title, font=None, item_font=None, asset_loader=None):
        """Initialize a menu.
        
        Args:
            title: Menu title string
            font: Optional font for the title
            item_font: Optional font for menu items
            asset_loader: Optional AssetLoader instance for loading assets
        """
        self.title = title
        self.title_font = font or pygame.font.Font(None, TITLE_FONT_SIZE)
        self.item_font = item_font or pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        self.asset_loader = asset_loader
        
        # Render the title
        self.title_surface = self.title_font.render(self.title, True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # For title glow effect
        self.title_glow_alpha = 0
        self.title_glow_dir = 1
        self.title_glow_speed = 100  # Alpha change per second
        
        # Menu items
        self.items = []
        self.selected_index = 0
        
        # State
        self.active = False
        
        # Animation
        self.appear_progress = 0.0  # 0.0 to 1.0
        self.appear_speed = 3.0  # Full appearance in 1/3 second
        
        # Sound effects
        self.navigate_sound = None
        self.select_sound = None
        self._load_sounds()
        
        # Help text
        self.show_help = True
        self.help_font = pygame.font.Font(None, 16)
        self.help_text = [
            "↑/↓: Navigate",
            "Enter: Select",
            "Esc: Back"
        ]
        self.help_surfaces = [self.help_font.render(text, True, (200, 200, 200)) for text in self.help_text]
        
        # Notification system (for confirmations)
        self.notification = None
        self.notification_timer = 0
        self.notification_duration = 2.0  # Duration to show a notification
        
        # Menu background effect
        self.background_alpha = 30  # Very subtle background overlay
        
    def _load_sounds(self):
        """Load menu sound effects if asset_loader is available."""
        if self.asset_loader:
            try:
                assets = self.asset_loader.load_game_assets()
                if "sounds" in assets:
                    self.navigate_sound = assets["sounds"].get("menu_navigate")
                    self.select_sound = assets["sounds"].get("menu_select")
                    
                    # Print status message for debugging
                    if self.navigate_sound:
                        print("Menu navigation sound loaded successfully")
                    else:
                        print("Menu navigation sound not available, continuing without it")
                        
                    if self.select_sound:
                        print("Menu selection sound loaded successfully")
                    else:
                        print("Menu selection sound not available, continuing without it")
            except Exception as e:
                print(f"Error loading menu sounds: {e}")
                self.navigate_sound = None
                self.select_sound = None
        
    def add_item(self, text, action=None, enabled=True, shortcut=None):
        """Add an item to the menu.
        
        Args:
            text: Display text for the menu item
            action: Callback function to execute when selected
            enabled: Whether the item is enabled and selectable
            shortcut: Optional keyboard shortcut hint (e.g., "ESC")
            
        Returns:
            The created MenuItem object
        """
        item = MenuItem(text, action, enabled, shortcut)
        self.items.append(item)
        
        # If this is the first item, select it if it's enabled
        if len(self.items) == 1 and item.enabled:
            item.select()
            
        return item
    
    def handle_event(self, event):
        """Handle pygame events for menu navigation.
        
        Args:
            event: Pygame event to process
            
        Returns:
            Result of the selected action if an item is activated, None otherwise
        """
        if not self.active or self.appear_progress < 0.9:
            return None
            
        if event.type == pygame.KEYDOWN:
            # Up/Down navigation
            if event.key == pygame.K_UP:
                if self._select_previous() and self.navigate_sound:
                    self.navigate_sound.play()
            elif event.key == pygame.K_DOWN:
                if self._select_next() and self.navigate_sound:
                    self.navigate_sound.play()
            # Activation with Enter or Space
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if 0 <= self.selected_index < len(self.items):
                    if self.select_sound:
                        self.select_sound.play()
                    return self.items[self.selected_index].activate()
            # ESC key typically goes back in menus
            elif event.key == pygame.K_ESCAPE:
                for item in self.items:
                    if "back" in item.text.lower() and item.enabled:
                        self._select_item_at_index(self.items.index(item))
                        if self.select_sound:
                            self.select_sound.play()
                        return item.activate()
            # Toggle help text with F1
            elif event.key == pygame.K_F1:
                self.show_help = not self.show_help
        
        # Mouse movement to hover over items
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_move(event.pos)
            
        # Mouse click to select
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            for i, item in enumerate(self.items):
                if item.contains_point(event.pos) and item.enabled:
                    # Already selected, so activate it
                    if item.selected:
                        if self.select_sound:
                            self.select_sound.play()
                        return item.activate()
                    # Not selected yet, select it first
                    else:
                        self._select_item_at_index(i)
                        if self.navigate_sound:
                            self.navigate_sound.play()
                        break
        
        return None
    
    def _handle_mouse_move(self, pos):
        """Handle mouse movement for highlighting menu items.
        
        Args:
            pos: (x, y) mouse position
        """
        for i, item in enumerate(self.items):
            if item.contains_point(pos) and item.enabled:
                if i != self.selected_index:
                    self._select_item_at_index(i)
                    if self.navigate_sound:
                        self.navigate_sound.play()
                break
    
    def _select_item_at_index(self, index):
        """Select the menu item at the given index.
        
        Args:
            index: Index of the item to select
            
        Returns:
            bool: True if selection changed, False otherwise
        """
        if not self.items or not (0 <= index < len(self.items)) or not self.items[index].enabled:
            return False
            
        # Deselect current item
        if 0 <= self.selected_index < len(self.items):
            self.items[self.selected_index].deselect()
            
        # Select new item
        self.selected_index = index
        self.items[self.selected_index].select()
        return True
    
    def _select_next(self):
        """Select the next enabled menu item.
        
        Returns:
            bool: True if selection changed, False otherwise
        """
        if not self.items:
            return False
            
        # Find the next enabled item
        start_index = (self.selected_index + 1) % len(self.items)
        index = start_index
        
        while True:
            if self.items[index].enabled:
                return self._select_item_at_index(index)
                
            index = (index + 1) % len(self.items)
            if index == start_index:
                break  # Wrapped around, no enabled items
                
        return False
    
    def _select_previous(self):
        """Select the previous enabled menu item.
        
        Returns:
            bool: True if selection changed, False otherwise
        """
        if not self.items:
            return False
            
        # Find the previous enabled item
        start_index = (self.selected_index - 1) % len(self.items)
        index = start_index
        
        while True:
            if self.items[index].enabled:
                return self._select_item_at_index(index)
                
            index = (index - 1) % len(self.items)
            if index == start_index:
                break  # Wrapped around, no enabled items
                
        return False
    
    def update(self, dt):
        """Update the menu state.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            None (handled by the menu item activate method)
        """
        # Update appearance animation
        if self.active and self.appear_progress < 1.0:
            self.appear_progress += self.appear_speed * dt
            if self.appear_progress > 1.0:
                self.appear_progress = 1.0
                
        # Update all menu items
        for item in self.items:
            item.update(dt)
            
        # Update title glow effect
        self.title_glow_alpha += self.title_glow_dir * self.title_glow_speed * dt
        if self.title_glow_alpha >= 100:
            self.title_glow_alpha = 100
            self.title_glow_dir = -1
        elif self.title_glow_alpha <= 0:
            self.title_glow_alpha = 0
            self.title_glow_dir = 1
            
        # Update notification if present
        if self.notification:
            self.notification_timer -= dt
            if self.notification_timer <= 0:
                self.notification = None
                
        return None
    
    def draw(self, surface):
        """Draw the menu on the screen.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Apply appearance progress to all elements
        alpha = int(255 * self.appear_progress)
        
        # Draw a subtle background overlay
        if self.background_alpha > 0:
            bg_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
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
            
            # Apply a slight blur effect (simple approximation)
            blurred_surface = pygame.transform.smoothscale(
                glow_surface,
                (glow_surface.get_width() - 2, glow_surface.get_height() - 2)
            )
            # Use the blurred surface
            glow_surface = blurred_surface
            
            # Position the glow
            glow_rect = glow_surface.get_rect(center=self.title_rect.center)
            glow_surface.set_alpha(alpha)
            surface.blit(glow_surface, glow_rect)
        
        # Draw the title
        title_surface_with_alpha = self.title_surface.copy()
        title_surface_with_alpha.set_alpha(alpha)
        surface.blit(title_surface_with_alpha, self.title_rect)
        
        # Draw menu items
        if self.items:
            # Calculate positions
            item_height = 40
            total_height = item_height * len(self.items)
            
            # Position first item (vertically centered, accounting for title)
            start_y = 250
            
            # Draw each menu item
            for i, item in enumerate(self.items):
                # Calculate item position
                item_y = start_y + i * item_height
                
                # Render the item text
                color = (200, 200, 200) if item.enabled else (100, 100, 100)
                if item.selected and item.enabled:
                    color = (255, 255, 255)
                
                # Apply the item's current alpha
                actual_alpha = min(alpha, item.alpha)
                text_surface = self.item_font.render(item.text, True, color)
                text_surface.set_alpha(actual_alpha)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, item_y))
                
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
                
                # If there's a shortcut hint, draw it
                if item.shortcut:
                    shortcut_surface = self.help_font.render(f"[{item.shortcut}]", True, color)
                    shortcut_rect = shortcut_surface.get_rect(midleft=(item.rect.right + 20, item_y))
                    shortcut_surface.set_alpha(actual_alpha)
                    surface.blit(shortcut_surface, shortcut_rect)
        
        # Draw help text if enabled
        if self.show_help and self.help_surfaces and self.appear_progress >= 0.8:
            help_alpha = int(min(255, alpha * (self.appear_progress - 0.8) * 5))
            help_y = SCREEN_HEIGHT - 20 * len(self.help_surfaces) - 10
            
            for i, help_surface in enumerate(self.help_surfaces):
                help_surface_copy = help_surface.copy()
                help_surface_copy.set_alpha(help_alpha)
                help_rect = help_surface_copy.get_rect(bottomright=(SCREEN_WIDTH - 20, help_y + i * 20))
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
            notif_rect = notif_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            notif_bg = pygame.Surface((notif_rect.width + 20, notif_rect.height + 10), pygame.SRCALPHA)
            notif_bg.fill((0, 0, 0, int(150 * fade)))
            notif_bg_rect = notif_bg.get_rect(center=notif_rect.center)
            
            # Draw notification
            surface.blit(notif_bg, notif_bg_rect)
            surface.blit(notif_surface, notif_rect)
    
    def activate(self):
        """Activate the menu."""
        self.active = True
        
        # Reset appearance progress to create the animation
        self.appear_progress = 0.0
        
        # Reset alpha for all items
        for item in self.items:
            item.alpha = 0
            item.target_alpha = 255
    
    def deactivate(self):
        """Deactivate the menu."""
        self.active = False
        
    def show_notification(self, text, duration=2.0):
        """Show a notification message.
        
        Args:
            text: The notification text
            duration: How long to show the notification (seconds)
        """
        self.notification = text
        self.notification_timer = duration
        self.notification_duration = duration 