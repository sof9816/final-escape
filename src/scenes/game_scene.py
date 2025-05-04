"""
Main gameplay scene for Asteroid Navigator.
"""
import random
import pygame
from src.constants import (
    BACKGROUND_COLOR, SCORE_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, 
    PLAYER_SIZE, ASTEROID_SPAWN_RATE, PLAYER_MAX_HEALTH
)
from src.scenes.scene import Scene
from src.entities.star import StarField
from src.entities.player import Player
from src.entities.asteroid import Asteroid
from src.ui.health_bar import HealthBar

class GameScene(Scene):
    """Main gameplay scene with player control and asteroid dodging."""
    
    def __init__(self, screen, assets):
        """
        Initialize the game scene.
        
        Args:
            screen: Pygame display surface
            assets: AssetLoader instance
        """
        super().__init__(screen, assets)
        self.next_scene = "GAME_OVER"
        
        # Create starfield
        self.star_field = StarField(100, SCREEN_WIDTH)
        
        # Setup sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        
        # Create player
        player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_SIZE * 1.5)
        self.player = Player(player_pos, assets.get_image("player"))
        self.all_sprites.add(self.player)
        
        # Create health bar
        self.health_bar = HealthBar(SCREEN_HEIGHT, assets.get_font("score"))
        
        # Game state
        self.score = 0
        self.asteroid_spawn_timer = 0.0
        self.next_spawn_interval = random.uniform(ASTEROID_SPAWN_RATE * 0.5, ASTEROID_SPAWN_RATE * 1.5)
        
        # Score font
        self.score_font = assets.get_font("score")
        
    def process_events(self, events):
        """
        Process input events.
        
        Args:
            events: List of pygame events to process
            
        Returns:
            bool: True if the game should quit
        """
        for event in events:
            if event.type == pygame.QUIT:
                return True
        return False
                
    def update(self, dt, joystick=None):
        """
        Update game elements.
        
        Args:
            dt: Delta time
            joystick: Optional joystick for control
        """
        # Update stars
        self.star_field.update(dt)
        
        # Update all sprites
        self.all_sprites.update(dt, joystick)

        # Asteroid Spawning
        self.asteroid_spawn_timer += dt
        if self.asteroid_spawn_timer >= self.next_spawn_interval:
            self.asteroid_spawn_timer = 0
            self.next_spawn_interval = random.uniform(ASTEROID_SPAWN_RATE * 0.5, ASTEROID_SPAWN_RATE * 1.5)
            self._spawn_asteroid()

        # Collision Detection
        hits = pygame.sprite.spritecollide(
            self.player, self.asteroids, False, pygame.sprite.collide_circle
        )
        if hits and not self.player.invulnerable:
            for asteroid in hits:
                # Apply damage from asteroid
                damage_applied = self.player.take_damage(asteroid.damage)
                if damage_applied:
                    print(f"Hit by asteroid type {asteroid.asteroid_type} "
                          f"(size: {asteroid.size_category}), dealing {asteroid.damage} damage!")
                    
                    # Check if player died
                    if self.player.health <= 0:
                        self.done = True
                    
                    # Only apply damage from one asteroid if multiple hits in the same frame
                    break

        # Scoring
        self.score += dt * 10
        
    def _spawn_asteroid(self):
        """Spawn a new asteroid and add it to the groups."""
        new_asteroid = Asteroid(self.assets.asteroid_images)
        self.all_sprites.add(new_asteroid)
        self.asteroids.add(new_asteroid)
        
    def draw(self):
        """Draw game elements on the screen."""
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw stars
        self.star_field.draw(self.screen)
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw score
        score_text = f"Score: {int(self.score)}"
        score_surface = self.score_font.render(score_text, True, SCORE_COLOR)
        self.screen.blit(score_surface, (10, 10))
        
        # Draw health bar
        self.health_bar.draw(self.screen, self.player.health, PLAYER_MAX_HEALTH)
        
    def get_score(self):
        """
        Get the current score.
        
        Returns:
            int: Current score
        """
        return int(self.score) 