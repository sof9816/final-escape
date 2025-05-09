"""
Menu state for Final Escape game.
"""
import pygame
import random
import math
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR,
    TITLE_FONT_SIZE, INSTRUCTION_FONT_SIZE,
    FADE_DURATION, MUSIC_FADE_DURATION, 
    STATE_COUNTDOWN, STATE_SETTINGS, STATE_MENU
)
from menu.main_menu import MainMenu
from menu.settings_menu import SettingsMenu
from settings.settings_manager import SettingsManager

class MenuState:
    """The main menu state for the game."""
    
    def __init__(self, asset_loader, star_field, particle_system, screen_width=None, screen_height=None):
        """Initialize the menu state.
        
        Args:
            asset_loader: AssetLoader instance for loading assets
            star_field: StarField instance for background stars
            particle_system: ParticleSystem instance for effects
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        self.asset_loader = asset_loader
        self.star_field = star_field
        self.particle_system = particle_system
        
        # Store screen dimensions
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Apply settings to star field
        self._apply_star_opacity()
        
        # Set up menus
        self.main_menu = MainMenu(asset_loader, self.screen_width, self.screen_height)
        self.settings_menu = SettingsMenu(asset_loader, self.settings_manager, star_field, self.screen_width, self.screen_height)
        
        # Track active menu
        self.active_menu = self.main_menu
        self.previous_menu = None
        
        # Create menu entities
        from entities.menu_entities import MenuAsteroid, MenuPlayer
        
        # Create background asteroids
        self.menu_asteroids = []
        for _ in range(10):  # 10 asteroids in menu
            self.menu_asteroids.append(MenuAsteroid(particle_system, asset_loader))
            
        # Create player ship that moves in a circle
        self.menu_player = MenuPlayer(particle_system, asset_loader)
        
        # Transition state
        self.transition_out = False
        self.fade_alpha = 0
        self.transition_timer = 0
        self.transition_target = None  # Which state to transition to
        
        # Menu transition effects
        self.menu_transition = False
        self.menu_transition_timer = 0
        self.menu_transition_duration = 0.5
        
        # Apply sound settings
        self._apply_sound_settings()
        
        # Ambient particle effects
        self.ambient_timer = 0
        self.ambient_interval = 0.8  # Seconds between ambient particle bursts
        
        print("MenuState initialized")
        
    def _apply_star_opacity(self):
        """Apply star opacity setting to the star field."""
        opacity_percent = self.settings_manager.get_star_opacity()
        opacity_value = int(opacity_percent * 255 / 100)
        
        # Apply to all stars
        for star in self.star_field.stars:
            star.opacity = opacity_value
    
    def _apply_sound_settings(self):
        """Apply sound settings to the game."""
        sound_enabled = self.settings_manager.get_sound_enabled()
        
        # Apply volume
        if sound_enabled:
            pygame.mixer.music.set_volume(1.0)
        else:
            pygame.mixer.music.set_volume(0.0)
            
    def _add_ambient_particles(self):
        """Add ambient particle effects."""
        # Random position near edge of screen
        edge = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        
        if edge == 0:  # Top
            x = random.randint(0, self.screen_width)
            y = -20
            direction_y = random.uniform(100, 200)
        elif edge == 1:  # Right
            x = self.screen_width + 20
            y = random.randint(0, self.screen_height)
            direction_y = random.uniform(-50, 50)
        elif edge == 2:  # Bottom
            x = random.randint(0, self.screen_width)
            y = self.screen_height + 20
            direction_y = random.uniform(-200, -100)
        else:  # Left
            x = -20
            y = random.randint(0, self.screen_height)
            direction_y = random.uniform(-50, 50)
            
        # Calculate direction toward center with randomness
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        direction_x = (center_x - x) * random.uniform(0.1, 0.3)
        
        # Colors for ambient particles
        colors = [
            (100, 100, 255),  # Blue
            (100, 200, 255),  # Light blue
            (255, 255, 255),  # White
            (200, 100, 255),  # Purple
        ]
        
        # Emit particles
        self.particle_system.emit_particles(
            x, y,
            [random.choice(colors)],
            count=random.randint(5, 15),
            velocity_range=((direction_x * 0.8, direction_x * 1.2), (direction_y * 0.8, direction_y * 1.2)),
            size_range=(1, 3),
            lifetime_range=(3, 6),
            fade=True
        )
        
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            STATE_COUNTDOWN if transitioning, None otherwise
        """
        # Skip events during transition
        if self.transition_out or self.menu_transition:
            return None
            
        # Let the active menu handle the event
        result = self.active_menu.handle_event(event)
        
        # Handle menu navigation results
        if result == STATE_COUNTDOWN:
            # Start game
            print("Starting game from menu")
            self.transition_out = True
            self.transition_timer = 0
            self.transition_target = STATE_COUNTDOWN
            
            # Add visual effect for game start
            self._add_game_start_effect()
            
        elif result == STATE_SETTINGS:
            # Switch to settings menu with transition
            print("Switching to settings menu")
            self.previous_menu = self.active_menu
            self.menu_transition = True
            self.menu_transition_timer = 0
            
            # Deactivate current menu during transition
            self.active_menu.deactivate()
            
            # Set new menu but don't activate until transition completes
            self.active_menu = self.settings_menu
            
        elif result == STATE_MENU:
            # Return to main menu with transition
            print("Returning to main menu")
            self.previous_menu = self.active_menu
            self.menu_transition = True
            self.menu_transition_timer = 0
            
            # Deactivate current menu during transition
            self.active_menu.deactivate()
            
            # Set new menu but don't activate until transition completes
            self.active_menu = self.main_menu
            
        return None
        
    def _add_game_start_effect(self):
        """Add visual effects when starting the game."""
        # Create a dramatic particle burst from the center
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Blue/white color scheme
        colors = [
            (100, 150, 255),  # Blue
            (150, 200, 255),  # Light blue
            (255, 255, 255),  # White
        ]
        
        # Emit particles in a starburst pattern
        for i in range(40):  # 40 emission points in a circle
            angle = i * (360 / 40)
            angle_rad = math.radians(angle)
            
            # Direction from center
            dir_x = math.cos(angle_rad)
            dir_y = math.sin(angle_rad)
            
            # Speed with some randomness
            speed = random.uniform(250, 350)
            vel_x = dir_x * speed
            vel_y = dir_y * speed
            
            # Emit several particles per angle
            self.particle_system.emit_particles(
                center_x, center_y,
                colors,
                count=4,
                velocity_range=((vel_x * 0.9, vel_x * 1.1), (vel_y * 0.9, vel_y * 1.1)),
                size_range=(2, 4),
                lifetime_range=(0.8, 1.5),
                fade=True
            )
        
    def update(self, dt):
        """Update the menu state.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            STATE_COUNTDOWN if transition complete, None otherwise
        """
        # Update stars
        self.star_field.update(dt)
        
        # Update particles
        self.particle_system.update(dt)
        
        # Update menu asteroids
        for asteroid in self.menu_asteroids:
            asteroid.update(dt)
            
            # Emit particles occasionally
            if random.random() < 0.2 * dt * 60:  # 20% chance per frame
                asteroid.emit_fire_particles()
                
        # Update menu player
        self.menu_player.update(dt)
        
        # Handle menu transitions
        if self.menu_transition:
            self.menu_transition_timer += dt
            
            # When transition completes, activate the new menu
            if self.menu_transition_timer >= self.menu_transition_duration:
                self.menu_transition = False
                self.active_menu.activate()
                
                # Add a transition effect with particles
                self._add_menu_transition_effect()
                
            return None
        
        # Update the active menu
        menu_result = self.active_menu.update(dt)
        
        # Handle menu update results
        if menu_result == STATE_COUNTDOWN:
            self.transition_out = True
            self.transition_timer = 0
            self.transition_target = STATE_COUNTDOWN
            
            # Add visual effect for game start
            self._add_game_start_effect()
            
        elif menu_result == STATE_SETTINGS:
            # Switch to settings menu
            self.previous_menu = self.active_menu
            self.menu_transition = True
            self.menu_transition_timer = 0
            
            # Deactivate current menu during transition
            self.active_menu.deactivate()
            
            # Set new menu but don't activate until transition completes
            self.active_menu = self.settings_menu
            
        elif menu_result == STATE_MENU:
            # Return to main menu
            self.previous_menu = self.active_menu
            self.menu_transition = True
            self.menu_transition_timer = 0
            
            # Deactivate current menu during transition
            self.active_menu.deactivate()
            
            # Set new menu but don't activate until transition completes
            self.active_menu = self.main_menu
            
        # Handle transition out if active
        if self.transition_out:
            self.transition_timer += dt
            self.fade_alpha = min(255, int(255 * (self.transition_timer / FADE_DURATION)))
            
            # If transition complete, change to target state
            if self.transition_timer >= FADE_DURATION:
                # Change the music if going to game
                if self.transition_target == STATE_COUNTDOWN:
                    print("Menu transition complete - switching to countdown")
                    self.asset_loader.play_music(
                        self.asset_loader.load_game_assets()["music"]["game"],
                        volume=self.settings_manager.get_sound_enabled() and 0.5 or 0.0,
                        fade_ms=MUSIC_FADE_DURATION
                    )
                return self.transition_target
        
        # Add ambient particles occasionally
        self.ambient_timer += dt
        if self.ambient_timer >= self.ambient_interval:
            self.ambient_timer = 0
            self._add_ambient_particles()
                
        return None
        
    def _add_menu_transition_effect(self):
        """Add a particle effect when transitioning between menus."""
        # Create a subtle wave of particles
        width = self.screen_width
        height = self.screen_height
        
        # Create particles along a horizontal line in the middle
        y = height // 2
        for x in range(0, width + 1, 20):  # Every 20 pixels
            # Emit particles
            colors = [(150, 200, 255), (200, 220, 255)]
            
            # Random upward/downward velocities
            vel_y = random.uniform(-80, 80)
            
            self.particle_system.emit_particles(
                x, y,
                colors,
                count=3,
                velocity_range=((-20, 20), (vel_y * 0.8, vel_y * 1.2)),
                size_range=(1, 3),
                lifetime_range=(0.6, 1.2),
                fade=True
            )
            
    def draw(self, surface):
        """Draw the menu state.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Clear screen
        surface.fill(BACKGROUND_COLOR)
        
        # Draw stars
        self.star_field.draw(surface)
        
        # Draw particles
        self.particle_system.draw(surface)
        
        # Draw menu asteroids
        for asteroid in self.menu_asteroids:
            asteroid.draw(surface)
            
        # Draw menu player
        self.menu_player.draw(surface)
        
        if self.menu_transition:
            # During menu transition, fade between menus
            progress = self.menu_transition_timer / self.menu_transition_duration
            
            # If we have a previous menu, draw it fading out
            if self.previous_menu:
                # Draw with fading alpha
                fade_alpha = int(255 * (1 - progress))
                prev_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                self.previous_menu.draw(prev_surface)
                prev_surface.set_alpha(fade_alpha)
                surface.blit(prev_surface, (0, 0))
            
            # Draw the new menu fading in
            new_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            self.active_menu.draw(new_surface)
            new_surface.set_alpha(int(255 * progress))
            surface.blit(new_surface, (0, 0))
        else:
            # Normal menu drawing
            self.active_menu.draw(surface)
        
        # Draw fade effect during transition out
        if self.transition_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, self.fade_alpha))
            surface.blit(fade_surface, (0, 0)) 