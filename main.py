"""
Final Escape - Main Game Entry Point

This file serves as the main entry point for the game and manages the overall game loop
and state transitions between different game states.
"""
import pygame
import sys
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, STATE_MENU, STATE_COUNTDOWN, 
    STATE_PLAYING, STATE_GAME_OVER, FADE_DURATION, MUSIC_FADE_DURATION
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
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        
        # Create the star field
        self.star_field = StarField()
        
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
            STATE_GAME_OVER: "GAME_OVER"
        }
        
        # Start the menu music
        self.asset_loader.play_music(self.assets["music"]["menu"])
        
        print("Game initialized. Current state:", self.state_names[self.current_state])
    
    def initializeStates(self):
        """Initialize or reinitialize game states."""
        self.menu_state = MenuState(self.asset_loader, self.star_field, self.particle_system)
        self.countdown_state = CountdownState(self.star_field, self.particle_system, self.asset_loader)
        self.game_state = GameState(self.asset_loader, self.star_field, self.particle_system)
        self.game_over_state = GameOverState(self.star_field, self.particle_system, self.asset_loader)
        print("States initialized.")
        
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
                
            # IMPROVED: Apply state change from update if needed with additional debugging
            if new_state is not None:
                print(f"Update produced state change: {self.state_names[self.current_state]} -> {self.state_names[new_state]}")
                self.change_state(new_state)
                new_state = None
            
            # PART 3: RENDERING
            # Draw current state
            if self.current_state == STATE_MENU:
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
            self.asset_loader.play_music(self.assets["music"]["menu"], fade_ms=MUSIC_FADE_DURATION)
            
        elif new_state == STATE_COUNTDOWN:
            print("Transitioning to COUNTDOWN state")
            # Reset countdown timer when entering countdown state
            self.countdown_state = CountdownState(self.star_field, self.particle_system, self.asset_loader)
            # Change to game music with crossfade
            self.asset_loader.play_music(self.assets["music"]["game"], fade_ms=MUSIC_FADE_DURATION)
            
        elif new_state == STATE_PLAYING:
            print("Transitioning to PLAYING state")
            # Reset game state when starting a new game
            if self.current_state == STATE_COUNTDOWN:
                self.game_state.reset()
            
        elif new_state == STATE_GAME_OVER:
            print("Transitioning to GAME_OVER state")
            # Change to game over music with crossfade
            self.asset_loader.play_music(self.assets["music"]["game_over"], fade_ms=MUSIC_FADE_DURATION)
            
        # Update the current state
        self.current_state = new_state
        print(f"State changed: {self.state_names[old_state]} -> {self.state_names[new_state]}")


if __name__ == "__main__":
    game = Game()
    game.run() 