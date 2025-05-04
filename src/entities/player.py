"""
Player entity for Asteroid Navigator.
"""
import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_a, K_d, K_w, K_s
from pygame.math import Vector2
from src.constants import PLAYER_SIZE, PLAYER_SPEED, PLAYER_MAX_HEALTH, SCREEN_WIDTH, SCREEN_HEIGHT

class Player(pygame.sprite.Sprite):
    """Player ship controlled by the user."""
    
    def __init__(self, pos, image):
        """
        Initialize the player.
        
        Args:
            pos: Initial position as (x, y) tuple
            image: Player ship image
        """
        super().__init__()
        
        # Load and scale the player graphic
        self.image = pygame.transform.scale(image, (PLAYER_SIZE, PLAYER_SIZE))
        
        # Make the background transparent
        self.image.set_colorkey((0, 0, 0))
        
        # Create circular collision mask
        self.radius = PLAYER_SIZE // 2
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        
        # Store original image for animations
        self.original_image = self.image.copy()
        self.pos = Vector2(pos)
        self.speed = PLAYER_SPEED
        
        # Initialize player health
        self.health = PLAYER_MAX_HEALTH
        # Add invulnerability timer for when player takes damage
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.0  # 1 second of invulnerability after hit
        self.flash_timer = 0
        self.is_flashing = False

    def update(self, dt, joystick=None):
        """
        Update player position and status.
        
        Args:
            dt: Delta time
            joystick: Optional joystick for control
        """
        keys = pygame.key.get_pressed()
        direction = Vector2(0, 0)

        # Keyboard input
        if keys[K_LEFT] or keys[K_a]:
            direction.x = -1
        if keys[K_RIGHT] or keys[K_d]:
            direction.x = 1
        if keys[K_UP] or keys[K_w]:
            direction.y = -1
        if keys[K_DOWN] or keys[K_s]:
            direction.y = 1

        # Joystick input (basic axis 0/1)
        if joystick:
            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)
            # Add a small deadzone
            if abs(axis_x) > 0.2:
                direction.x = axis_x
            if abs(axis_y) > 0.2:
                direction.y = axis_y

        # Normalize diagonal movement and apply speed * dt
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt

        # Keep player on screen
        self.pos.x = max(PLAYER_SIZE // 2, min(SCREEN_WIDTH - PLAYER_SIZE // 2, self.pos.x))
        self.pos.y = max(PLAYER_SIZE // 2, min(SCREEN_HEIGHT - PLAYER_SIZE // 2, self.pos.y))

        self.rect.center = self.pos
        
        # Update invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer += dt
            if self.invulnerable_timer >= self.invulnerable_duration:
                self.invulnerable = False
                self.invulnerable_timer = 0
                # Restore original image when invulnerability ends
                self.image = self.original_image.copy()
            else:
                # Flash effect during invulnerability
                self.flash_timer += dt
                if self.flash_timer >= 0.1:  # Toggle flash every 0.1 seconds
                    self.flash_timer = 0
                    self.is_flashing = not self.is_flashing
                    
                    if self.is_flashing:
                        # Make player semi-transparent when flashing
                        self.image = self.original_image.copy()
                        self.image.set_alpha(128)
                    else:
                        # Restore normal visibility
                        self.image = self.original_image.copy()
    
    def take_damage(self, amount):
        """
        Reduce player health and trigger invulnerability.
        
        Args:
            amount: Amount of damage to apply
            
        Returns:
            bool: True if damage was applied, False if player was invulnerable
        """
        if not self.invulnerable:
            self.health -= amount
            self.health = max(0, self.health)  # Don't go below 0
            self.invulnerable = True
            self.invulnerable_timer = 0
            self.flash_timer = 0
            self.is_flashing = True
            
            # Start flashing immediately
            self.image = self.original_image.copy()
            self.image.set_alpha(128)
            
            return True  # Damage was applied
        return False  # Player was invulnerable, no damage 