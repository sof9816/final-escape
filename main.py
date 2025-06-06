"""
Final Escape - Main Game Entry Point

This file serves as the main entry point for the game and manages the overall game loop
and state transitions between different game states.
"""
import pygame
import sys
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, STATE_MENU, STATE_COUNTDOWN, 
    STATE_PLAYING, STATE_GAME_OVER, STATE_SETTINGS,
    FADE_DURATION, MUSIC_FADE_DURATION, FULLSCREEN
)
from engine.asset_loader import AssetLoader
from engine.text_renderer import TextRenderer
from effects.stars import StarField
from effects.particles import ParticleSystem
from states.menu_state import MenuState
from states.countdown_state import CountdownState
from states.game_state import GameState
from states.game_over_state import GameOverState

class Game:
    """Main game manager class that handles state transitions and the game loop."""
    
    def __init__(self):
        """Initialize the game window, systems, and states."""
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Create the game window
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get the actual screen dimensions
            screen_info = pygame.display.Info()
            self.screen_width = screen_info.current_w
            self.screen_height = screen_info.current_h
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen_width = SCREEN_WIDTH
            self.screen_height = SCREEN_HEIGHT
            
        pygame.display.set_caption("Final Escape")
        
        # Create the asset loader
        self.asset_loader = AssetLoader()
        
        # Load all game assets
        self.assets = self.asset_loader.load_game_assets()
        
        # Initialize text renderer
        self.text_renderer = TextRenderer(self.asset_loader)
        self.asset_loader.text_renderer = self.text_renderer
        
        # IMPROVED: Create the particle system with significantly increased particle count
        self.particle_system = ParticleSystem(max_particles=5000)  # Increased from 2000
        
        # Create the star field with the correct screen dimensions
        self.star_field = StarField(screen_width=self.screen_width, screen_height=self.screen_height)
        
        # Set up the clock
        self.clock = pygame.time.Clock()
        
        # Initialize states
        self.initializeStates()
        
        # Current game state
        self.current_state = STATE_MENU
        
        # Track the state names for debugging
        self.state_names = {
            STATE_MENU: "MENU",
            STATE_COUNTDOWN: "COUNTDOWN",
            STATE_PLAYING: "PLAYING",
            STATE_GAME_OVER: "GAME_OVER",
            STATE_SETTINGS: "SETTINGS"
        }
        
        # Start the menu music
        self.asset_loader.play_music(self.assets["music"]["menu"])
        
        print("Game initialized. Current state:", self.state_names[self.current_state])
    
    def initializeStates(self):
        """Initialize or reinitialize game states."""
        # Ensure latest settings are loaded
        from settings.settings_manager import SettingsManager
        settings = SettingsManager()
        
        # Create all game states with fresh settings
        self.menu_state = MenuState(self.asset_loader, self.star_field, self.particle_system, self.screen_width, self.screen_height)
        self.countdown_state = CountdownState(self.star_field, self.particle_system, self.asset_loader, self.screen_width, self.screen_height)
        self.game_state = GameState(self.asset_loader, self.star_field, self.particle_system, self.screen_width, self.screen_height)
        self.game_over_state = GameOverState(self.star_field, self.particle_system, self.asset_loader, self.screen_width, self.screen_height)
        
        # Apply sound settings to current music
        volume = 0.5 if settings.get_sound_enabled() else 0.0
        pygame.mixer.music.set_volume(volume)
        
        print("States initialized with current settings.")
        print(f"Current settings - Sound: {'ON' if settings.get_sound_enabled() else 'OFF'}, Difficulty: {settings.get_difficulty()}")
        
    def run(self):
        """Run the main game loop."""
        running = True
        new_state = None
        
        while running:
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0
            if dt > 0.1:  # Prevent large time steps
                dt = 0.05
                
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle key presses for debugging
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("ESC key pressed - exiting game")
                        running = False
                    elif event.key == pygame.K_F11:
                        # Toggle fullscreen mode
                        self.toggle_fullscreen()
                    
                # PART 1: EVENT HANDLING
                # Pass events to current state and get next state (if any)
                if self.current_state == STATE_MENU:
                    new_state = self.menu_state.handle_event(event)
                elif self.current_state == STATE_COUNTDOWN:
                    new_state = self.countdown_state.handle_event(event)
                elif self.current_state == STATE_PLAYING:
                    new_state = self.game_state.handle_event(event)
                elif self.current_state == STATE_GAME_OVER:
                    new_state = self.game_over_state.handle_event(event)
                elif self.current_state == STATE_SETTINGS:
                    # Settings are handled within the menu state
                    new_state = self.menu_state.handle_event(event)
                    
                # IMPROVED: Apply state change from event if needed with additional debugging
                if new_state is not None:
                    print(f"Event handler produced state change: {self.state_names[self.current_state]} -> {self.state_names[new_state]}")
                    self.change_state(new_state)
                    new_state = None
            
            # PART 2: STATE UPDATES
            # Update current state and get next state (if any)
            if self.current_state == STATE_MENU:
                new_state = self.menu_state.update(dt)
            elif self.current_state == STATE_COUNTDOWN:
                new_state = self.countdown_state.update(dt)
            elif self.current_state == STATE_PLAYING:
                new_state = self.game_state.update(dt)
                # If game over, save score
                if new_state == STATE_GAME_OVER:
                    print("Player died - transitioning to game over")
                    self.game_over_state.set_score(self.game_state.score)
            elif self.current_state == STATE_GAME_OVER:
                new_state = self.game_over_state.update(dt)
            elif self.current_state == STATE_SETTINGS:
                # Settings are handled within the menu state
                new_state = self.menu_state.update(dt)
                
            # IMPROVED: Apply state change from update if needed with additional debugging
            if new_state is not None:
                print(f"Update produced state change: {self.state_names[self.current_state]} -> {self.state_names[new_state]}")
                self.change_state(new_state)
                new_state = None
            
            # PART 3: RENDERING
            # Draw current state
            if self.current_state == STATE_MENU or self.current_state == STATE_SETTINGS:
                self.menu_state.draw(self.screen)
            elif self.current_state == STATE_COUNTDOWN:
                self.countdown_state.draw(self.screen)
            elif self.current_state == STATE_PLAYING:
                self.game_state.draw(self.screen)
            elif self.current_state == STATE_GAME_OVER:
                self.game_over_state.draw(self.screen)
            
            # Update the display
            pygame.display.flip()
            
        # Clean up
        pygame.quit()
        sys.exit()
        
    def change_state(self, new_state):
        """Change the current game state and handle transitions."""
        if new_state == self.current_state:
            return
        
        old_state = self.current_state
        print(f"Changing state from {self.state_names[old_state]} to {self.state_names[new_state]}")
        
        # Always reload settings before state transitions
        from settings.settings_manager import SettingsManager
        settings = SettingsManager()
        sound_enabled = settings.get_sound_enabled()
        volume = 0.5 if sound_enabled else 0.0
        
        # IMPROVED: Handling of state transitions, especially for game over to menu
        # Reset states when appropriate
        if new_state == STATE_MENU:
            # Reset necessary states when going back to menu
            print("Transitioning to MENU state")
            if self.current_state == STATE_GAME_OVER:
                print("Resetting game state for new game after game over")
                # Reset the game state and particles
                self.game_state.reset()
                
                # IMPROVED: Recreate particle system with even more particles
                self.particle_system = ParticleSystem(max_particles=5000)
                
                # Recreate all states to ensure clean state
                self.initializeStates()
                
            # Change to menu music with crossfade
            self.asset_loader.play_music(self.assets["music"]["menu"], volume=volume, fade_ms=MUSIC_FADE_DURATION)
            
        elif new_state == STATE_COUNTDOWN:
            print("Transitioning to COUNTDOWN state")
            # Reset countdown timer when entering countdown state
            self.countdown_state = CountdownState(self.star_field, self.particle_system, self.asset_loader, self.screen_width, self.screen_height)
            
            # Reset game state to prepare for a new game with current settings
            self.game_state.reset()
            
            # Change to game music with crossfade
            self.asset_loader.play_music(self.assets["music"]["game"], volume=volume, fade_ms=MUSIC_FADE_DURATION)
            
            # Add visual effects for game start
            self._add_game_start_effects()
            
        elif new_state == STATE_PLAYING:
            print("Transitioning to PLAYING state")
            # No need to reset game state here as it was already reset in countdown transition
            pass
            
        elif new_state == STATE_GAME_OVER:
            print("Transitioning to GAME OVER state")
            # Change to game over music with crossfade
            self.asset_loader.play_music(self.assets["music"]["game_over"], volume=volume, fade_ms=MUSIC_FADE_DURATION)
            
        # Set the new current state
        self.current_state = new_state
        print(f"State changed to: {self.state_names[self.current_state]}")
        
    def _add_game_start_effects(self):
        """Add visual effects for game start."""
        if not self.particle_system:
            return
            
        # Create a burst of particles in the center
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Create a starburst effect
        colors = [
            (0, 191, 255),    # Deep Sky Blue
            (30, 144, 255),   # Dodger Blue
            (65, 105, 225),   # Royal Blue
            (100, 149, 237),  # Cornflower Blue
            (135, 206, 250)   # Light Sky Blue
        ]
        
        # Emit particles in all directions
        for angle in range(0, 360, 5):  # Every 5 degrees
            # Calculate direction
            import math
            angle_rad = angle * (math.pi / 180)
            dir_x = math.cos(angle_rad)
            dir_y = math.sin(angle_rad)
            
            # Calculate velocity
            import random
            speed = random.uniform(200, 300)
            vel_x = dir_x * speed
            vel_y = dir_y * speed
            
            # Emit the particle
            self.particle_system.emit_particles(
                center_x, center_y,
                colors,
                count=2,
                velocity_range=((vel_x * 0.9, vel_x * 1.1), (vel_y * 0.9, vel_y * 1.1)),
                size_range=(2, 4),
                lifetime_range=(0.8, 1.2),
                fade=True
            )

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        print("Toggling fullscreen mode")
        
        # Toggle fullscreen state
        if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
            # Switch to windowed mode
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen_width = SCREEN_WIDTH
            self.screen_height = SCREEN_HEIGHT
            print("Switched to windowed mode")
        else:
            # Switch to fullscreen mode
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            screen_info = pygame.display.Info()
            self.screen_width = screen_info.current_w
            self.screen_height = screen_info.current_h
            print(f"Switched to fullscreen mode ({self.screen_width}x{self.screen_height})")
        
        # Update star field with new dimensions
        self.star_field.set_screen_size(self.screen_width, self.screen_height)
        
        # Update states with new screen dimensions
        self.initializeStates()


if __name__ == "__main__":
    game = Game()
    game.run() 