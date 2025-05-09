"""
Player entity for Final Escape game.
"""
import pygame
import random
import math
from pygame.math import Vector2
from constants import (
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_ACCELERATION, PLAYER_DECELERATION,
    PLAYER_MAX_HEALTH, PLAYER_THRUSTER_COLORS
)

class Player(pygame.sprite.Sprite):
    """Player class representing the spaceship controlled by the user."""
    
    def __init__(self, pos, player_image_surface, particle_system):
        """Initialize the player sprite.
        
        Args:
            pos: Initial position (x, y)
            player_image_surface: Pre-loaded pygame.Surface for the player's image
            particle_system: ParticleSystem instance for visual effects
        """
        super().__init__()
        
        # Use the pre-loaded player image
        self.image_original = player_image_surface
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=pos)
        
        # Movement properties
        self.position = Vector2(pos)
        self.velocity = Vector2(0, 0)
        self.target_velocity = Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.acceleration = PLAYER_ACCELERATION
        self.deceleration = PLAYER_DECELERATION
        self.rotation = 0
        
        # Collision properties
        self.radius = self.rect.width // 2
        
        # Health system
        self.health = PLAYER_MAX_HEALTH
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.0  # Seconds of invulnerability after hit
        
        # Visual feedback for damage
        self.flash_rate = 0.1  # How quickly to flash (seconds)
        self.flash_timer = 0
        self.flash_visible = True
        
        # Store particle system but don't use it
        self.particle_system = particle_system
        
        # Thruster control variables
        self.thrusting = False
        self.thruster_cooldown = 0
        self.thruster_rate = 0.03  # Emit particles every 0.03 seconds when thrusting
        
    def update(self, dt, joystick=None):
        """Update the player based on input and game state."""
        # Reset thrusting flag
        self.thrusting = False
        
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Reset target velocity
        self.target_velocity = Vector2(0, 0)
        
        # Keyboard input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.target_velocity.x = -self.speed
            self.thrusting = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.target_velocity.x = self.speed
            self.thrusting = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.target_velocity.y = -self.speed
            self.thrusting = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.target_velocity.y = self.speed
            self.thrusting = True
            
        # Joystick input if available
        if joystick:
            # Get joystick axis values (ranges from -1 to 1)
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            
            # Apply deadzone to prevent drift
            deadzone = 0.2
            if abs(x_axis) > deadzone:
                self.target_velocity.x = x_axis * self.speed
                self.thrusting = True
            if abs(y_axis) > deadzone:
                self.target_velocity.y = y_axis * self.speed
                self.thrusting = True
        
        # Calculate acceleration/deceleration
        if self.thrusting:
            # Accelerate toward target velocity
            if self.target_velocity.length() > 0:
                # Normalize and scale by acceleration and dt
                acceleration_vector = self.target_velocity.normalize() * self.acceleration * dt
                self.velocity += acceleration_vector
                
                # Cap at maximum speed
                if self.velocity.length() > self.speed:
                    self.velocity.scale_to_length(self.speed)
        else:
            # Decelerate when not thrusting
            if self.velocity.length() > 0:
                deceleration_amount = self.deceleration * dt
                
                # If we would decelerate past zero, just stop
                if self.velocity.length() <= deceleration_amount:
                    self.velocity = Vector2(0, 0)
                else:
                    # Apply deceleration in the opposite direction of movement
                    deceleration_vector = -self.velocity.normalize() * deceleration_amount
                    self.velocity += deceleration_vector
        
        # Update position based on velocity
        self.position += self.velocity * dt
        
        # Keep player on screen
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        # Left/right boundaries
        if self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x = 0
        elif self.position.x > screen_width - self.radius:
            self.position.x = screen_width - self.radius
            self.velocity.x = 0
            
        # Top/bottom boundaries
        if self.position.y < self.radius:
            self.position.y = self.radius
            self.velocity.y = 0
        elif self.position.y > screen_height - self.radius:
            self.position.y = screen_height - self.radius
            self.velocity.y = 0
            
        # Update rect position
        self.rect.center = self.position
        
        # Update invulnerability and flashing effect
        if self.invulnerable:
            self.invulnerable_timer -= dt
            
            # Update flashing effect
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_visible = not self.flash_visible
                self.flash_timer = self.flash_rate
                
                # Apply visual effect based on flash state
                if not self.flash_visible:
                    # Set transparency to half during invulnerability "off" phase
                    temp_image = self.image_original.copy()
                    temp_image.set_alpha(128)  # 0-255, where 0 is fully transparent
                    self.image = temp_image
                else:
                    # Reset to full visibility
                    self.image = self.image_original.copy()
                    
                # Keep the image rotated correctly
                if self.rotation != 0:
                    self.image = pygame.transform.rotate(self.image, -self.rotation)
                
            # End invulnerability if timer expired
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.flash_visible = True
                # Ensure full visibility when invulnerability ends
                self.image = self.image_original.copy()
                if self.rotation != 0:
                    self.image = pygame.transform.rotate(self.image, -self.rotation)
        
        # Emit thruster particles if thrusting
        if self.thrusting:
            self.thruster_cooldown -= dt
            if self.thruster_cooldown <= 0:
                self.emit_thruster_particles()
                self.thruster_cooldown = self.thruster_rate
                
        # Update rotation based on movement direction
        if self.velocity.length() > 0.5:  # Only rotate if moving significantly
            # Calculate the angle of movement (in degrees)
            target_angle = math.degrees(math.atan2(self.velocity.y, self.velocity.x))
            
            # Rotate 90 degrees clockwise (so ship points in direction of travel)
            self.rotation = target_angle + 90
            
            # Rotate the image (negative because pygame rotates counterclockwise)
            # Only update the rotation if not in the middle of a flash to prevent flickering
            if not self.invulnerable or self.flash_visible:
                self.image = pygame.transform.rotate(self.image_original, -self.rotation)
                self.rect = self.image.get_rect(center=self.rect.center)
    
    def take_damage(self, amount):
        """Apply damage to the player if not invulnerable.
        
        Args:
            amount: Amount of damage to apply
            
        Returns:
            Boolean indicating if damage was applied
        """
        if self.invulnerable:
            return False
            
        self.health -= amount
        
        # Clamp health to minimum 0
        if self.health < 0:
            self.health = 0
            
        # Activate invulnerability and flashing effect
        self.invulnerable = True
        self.invulnerable_timer = self.invulnerable_duration
        self.flash_timer = self.flash_rate
        self.flash_visible = True
        
        return True
        
    def emit_thruster_particles(self):
        """Emit thruster particle effects from three points behind the player."""
        if not self.particle_system:
            return

        # Ship rotation determines the orientation
        angle_rad = math.radians(self.rotation)

        # --- Calculate Emission Points Relative to Ship Orientation --- 

        # 1. Bottom/Center Point:
        #    Calculate the position directly behind the player's center based on rotation.
        back_offset_distance = self.radius * 0.9  # How far back from the center
        bottom_x = self.position.x - math.sin(angle_rad) * back_offset_distance
        bottom_y = self.position.y + math.cos(angle_rad) * back_offset_distance

        # 2. Left and Right Points:
        #    Calculate points perpendicular to the ship's orientation from the bottom point.
        perp_angle = angle_rad + (math.pi / 2)  # Perpendicular angle
        thruster_spacing = self.radius * 0.45  # Distance from center to side thrusters
        
        # Left thruster
        left_x = bottom_x + math.sin(perp_angle) * thruster_spacing
        left_y = bottom_y + math.cos(perp_angle) * thruster_spacing
        
        # Right thruster
        right_x = bottom_x - math.sin(perp_angle) * thruster_spacing
        right_y = bottom_y - math.cos(perp_angle) * thruster_spacing
        
        # --- Define Flame Direction --- 
        # The flame should oppose the actual velocity of the player
        if self.velocity.length() > 0.1: # Avoid division by zero if not moving
            flame_direction = -self.velocity.normalize()
        else:
            # If not moving, default to pointing opposite the ship's orientation
            flame_direction = Vector2(-math.cos(angle_rad), -math.sin(angle_rad))

        # --- Calculate Ship's Perpendicular Vector --- 
        # This is needed to spread the cone relative to the ship's body, not velocity
        ship_perp_angle = angle_rad + (math.pi / 2)
        ship_perp_vector = Vector2(math.cos(ship_perp_angle), math.sin(ship_perp_angle))

        # --- Emit Flames --- 
        
        # Center Flame (more intense)
        self._create_jet_flame(
            bottom_x, bottom_y,       # Position
            flame_direction,            # Direction
            ship_perp_vector,           # Ship's perpendicular vector for cone spread
            count=3,                    # Particle count
            cone_width=self.radius * 0.15,  # Width of cone base
            speed_factor=1.8,           # Base speed multiplier
            size_range=(3, 6),          # Particle size
            lifetime_range=(0.15, 0.3)  # Particle lifetime
        )
        
        # Left Flame
        self._create_jet_flame(
            left_x, left_y,             # Position
            flame_direction,            # Direction
            ship_perp_vector,           # Ship's perpendicular vector for cone spread
            count=2,                    # Particle count
            cone_width=self.radius * 0.1,   # Width of cone base
            speed_factor=1.5,           # Base speed multiplier
            size_range=(2, 4),          # Particle size
            lifetime_range=(0.1, 0.25)  # Particle lifetime
        )
        
        # Right Flame
        self._create_jet_flame(
            right_x, right_y,            # Position
            flame_direction,            # Direction
            ship_perp_vector,           # Ship's perpendicular vector for cone spread
            count=2,                    # Particle count
            cone_width=self.radius * 0.1,   # Width of cone base
            speed_factor=1.5,           # Base speed multiplier
            size_range=(2, 4),          # Particle size
            lifetime_range=(0.1, 0.25)  # Particle lifetime
        )
    
    def _create_jet_flame(self, x, y, direction, ship_perp_vector, count, cone_width, speed_factor, size_range, lifetime_range):
        """Helper method to create a single jet flame cone effect."""
        # Base speed depends slightly on player's current speed
        base_particle_speed = max(150, self.velocity.length() * 0.5) * speed_factor

        for i in range(count):
            # Position within the cone base, using the SHIP's perpendicular vector
            random_width_offset = random.uniform(-cone_width, cone_width)
            emit_x = x + ship_perp_vector.x * random_width_offset
            emit_y = y + ship_perp_vector.y * random_width_offset

            # How close to the center of the cone (0 = edge, 1 = center)
            center_ratio = 1.0 - (abs(random_width_offset) / cone_width)
            
            # Velocity calculation (uses flame direction)
            # Particles in the center move faster and straighter
            particle_speed = base_particle_speed * (0.8 + center_ratio * 0.4)
            # Add minor angle variation for a less rigid look
            angle_variation = random.uniform(-0.15, 0.15) * (1.0 - center_ratio) # More variation at edges
            current_angle = math.atan2(direction.y, direction.x) + angle_variation
            vel_x = math.cos(current_angle) * particle_speed
            vel_y = math.sin(current_angle) * particle_speed

            velocity_range = (
                (vel_x * 0.9, vel_x * 1.1),
                (vel_y * 0.9, vel_y * 1.1)
            )

            # Size calculation (center particles slightly larger)
            current_min_size = size_range[0] + (center_ratio * 1)
            current_max_size = size_range[1] + (center_ratio * 1)

            # Lifetime calculation (center particles live slightly longer)
            current_min_lifetime = lifetime_range[0] * (0.9 + center_ratio * 0.2)
            current_max_lifetime = lifetime_range[1] * (0.9 + center_ratio * 0.2)
            
            # Emit particle
            self.particle_system.emit_particles(
                emit_x, emit_y,
                PLAYER_THRUSTER_COLORS,
                count=1,
                velocity_range=velocity_range,
                size_range=(current_min_size, current_max_size),
                lifetime_range=(current_min_lifetime, current_max_lifetime),
                fade=True
            ) 