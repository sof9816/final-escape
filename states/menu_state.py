"""
Menu state for Asteroid Navigator game.
"""
import pygame
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR,
    TITLE_FONT_SIZE, INSTRUCTION_FONT_SIZE,
    FADE_DURATION, MUSIC_FADE_DURATION, STATE_COUNTDOWN
)

class MenuState:
    """The main menu state for the game."""
    
    def __init__(self, asset_loader, star_field, particle_system):
        """Initialize the menu state.
        
        Args:
            asset_loader: AssetLoader instance for loading assets
            star_field: StarField instance for background stars
            particle_system: ParticleSystem instance for effects
        """
        self.asset_loader = asset_loader
        self.star_field = star_field
        self.particle_system = particle_system
        
        # Load logo
        self.logo_img = asset_loader.load_image("assets/images/logo.png")
        self.logo_rect = self.logo_img.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Setup fonts
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        
        # Setup text
        self.instruction_text = "Press any key to start"
        self.instruction_surface = self.instruction_font.render(
            self.instruction_text, True, (255, 255, 255)
        )
        self.instruction_rect = self.instruction_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        )
        
        # Animation for instruction text
        self.instruction_alpha = 255
        self.fade_direction = -1  # -1 for fade out, 1 for fade in
        self.fade_speed = 200  # Alpha change per second
        
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
        
        print("MenuState initialized")
        
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            STATE_COUNTDOWN if transitioning, None otherwise
        """
        if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
            if not self.transition_out:
                print("Key press detected in menu - starting transition")
                self.transition_out = True
                self.transition_timer = 0
        return None
        
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
        
        # Pulse the instruction text
        self.instruction_alpha += self.fade_direction * self.fade_speed * dt
        if self.instruction_alpha <= 100:
            self.instruction_alpha = 100
            self.fade_direction = 1
        elif self.instruction_alpha >= 255:
            self.instruction_alpha = 255
            self.fade_direction = -1
            
        # Update the instruction surface with new alpha
        self.instruction_surface = self.instruction_font.render(
            self.instruction_text, True, (255, 255, 255)
        )
        
        # Handle transition out if active
        if self.transition_out:
            self.transition_timer += dt
            self.fade_alpha = min(255, int(255 * (self.transition_timer / FADE_DURATION)))
            
            # If transition complete, change to countdown state
            if self.transition_timer >= FADE_DURATION:
                # Change the music
                print("Menu transition complete - switching to countdown")
                self.asset_loader.play_music(
                    self.asset_loader.load_game_assets()["music"]["game"],
                    volume=0.5,
                    fade_ms=MUSIC_FADE_DURATION
                )
                return STATE_COUNTDOWN
                
        return None
            
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
        
        # Draw logo
        surface.blit(self.logo_img, self.logo_rect)
        
        # Draw instruction text with current alpha
        temp_surface = pygame.Surface(self.instruction_surface.get_size(), pygame.SRCALPHA)
        temp_surface.fill((255, 255, 255, 0))  # Transparent background
        temp_surface.blit(self.instruction_surface, (0, 0))
        temp_surface.set_alpha(int(self.instruction_alpha))
        surface.blit(temp_surface, self.instruction_rect)
        
        # Draw fade overlay for transition
        if self.transition_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            surface.blit(fade_surface, (0, 0)) 