"""
Countdown state for Final Escape game.
"""
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, 
    COUNTDOWN_DURATION, COUNTDOWN_FONT_SIZE, COUNTDOWN_COLOR,
    FADE_DURATION, STATE_PLAYING
)

class CountdownState:
    """Countdown before gameplay starts."""
    
    def __init__(self, star_field, particle_system, asset_loader=None, screen_width=None, screen_height=None):
        """Initialize the countdown state.
        
        Args:
            star_field: StarField instance for background stars
            particle_system: ParticleSystem instance for effects
            asset_loader: Optional AssetLoader instance for loading fonts
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        self.star_field = star_field
        self.particle_system = particle_system
        self.asset_loader = asset_loader
        
        # Store screen dimensions
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        # Setup fonts - try to use custom fonts if asset_loader is provided
        if asset_loader:
            assets = asset_loader.load_game_assets()
            self.countdown_font = assets["fonts"]["countdown"] if "fonts" in assets and "countdown" in assets["fonts"] else pygame.font.Font(None, COUNTDOWN_FONT_SIZE)
        else:
            # Fallback to default font
            self.countdown_font = pygame.font.Font(None, COUNTDOWN_FONT_SIZE)
        
        # Countdown timer
        self.timer = 0
        self.duration = COUNTDOWN_DURATION
        
        # Transition variables
        self.transition_out = False
        self.fade_alpha = 0
        self.transition_timer = 0
        
        # Scaling animation for numbers
        self.scale_factor = 0.1  # Start small
        self.target_scale = 1.0  # Target scale
        self.scale_speed = 2.0   # Units per second
        
        print("CountdownState initialized")
        
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            STATE_PLAYING if skip button pressed, None otherwise
        """
        # Skip button (optional)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("Skip button pressed in countdown - immediate transition to playing")
            self.timer = self.duration
            self.transition_out = True
            self.transition_timer = 0
            return STATE_PLAYING
            
        return None
        
    def update(self, dt):
        """Update the countdown state.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            STATE_PLAYING if countdown finished, None otherwise
        """
        # Update stars
        self.star_field.update(dt)
        
        # Update particles
        self.particle_system.update(dt)
        
        # Update timer
        self.timer += dt
        
        # Calculate countdown number (3, 2, 1)
        countdown_num = max(1, int(self.duration - self.timer) + 1)
        
        # Reset scale animation when number changes
        if self.timer % 1 < dt:  # Check if we just crossed a whole second
            self.scale_factor = 0.1
            
        # Update scale animation
        if self.scale_factor < self.target_scale:
            self.scale_factor += self.scale_speed * dt
            if self.scale_factor > self.target_scale:
                self.scale_factor = self.target_scale
        
        # Check if countdown is finished
        if self.timer >= self.duration and not self.transition_out:
            print("Countdown complete - starting transition")
            self.transition_out = True
            self.transition_timer = 0
            
        # Handle transition out if active
        if self.transition_out:
            self.transition_timer += dt
            self.fade_alpha = min(255, int(255 * (self.transition_timer / FADE_DURATION)))
            
            # If transition complete, change to gameplay state
            if self.transition_timer >= FADE_DURATION:
                print("Countdown transition complete - switching to gameplay")
                return STATE_PLAYING
                
        return None
            
    def draw(self, surface):
        """Draw the countdown state.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Clear screen
        surface.fill(BACKGROUND_COLOR)
        
        # Draw stars
        self.star_field.draw(surface)
        
        # Draw particles
        self.particle_system.draw(surface)
        
        # Draw countdown number
        if self.timer < self.duration:
            countdown_num = max(1, int(self.duration - self.timer) + 1)
            
            # Create text with current scale
            base_size = COUNTDOWN_FONT_SIZE
            scaled_size = int(base_size * self.scale_factor)
            
            # Use regular font if scale is too small
            if scaled_size < 20:
                scaled_size = 20
            
            # Try to use the custom font for scaling if available
            if self.asset_loader:
                try:
                    # Get the font path from our countdown font
                    font_path = self.countdown_font.get_filename()
                    scaled_font = pygame.font.Font(font_path, scaled_size)
                except:
                    # Fallback to default font if there's an error
                    scaled_font = pygame.font.Font(None, scaled_size)
            else:
                scaled_font = pygame.font.Font(None, scaled_size)
            
            countdown_text = str(countdown_num)
            countdown_surface = scaled_font.render(countdown_text, True, COUNTDOWN_COLOR)
            countdown_rect = countdown_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(countdown_surface, countdown_rect)
        
        # Draw fade overlay for transition
        if self.transition_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            surface.blit(fade_surface, (0, 0)) 