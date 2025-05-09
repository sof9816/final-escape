"""
Asteroid entity for Final Escape game.
"""
import pygame
import random
import math
import os
from pygame.math import Vector2
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ASTEROID_SIZES, ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED,
    ASTEROID_SPEED_MULTIPLIERS, ASTEROID_TYPE_WEIGHTS,
    ASTEROID_SIZE_RESTRICTIONS, ASTEROID_BASE_DAMAGE,
    ASTEROID_SIZE_DAMAGE_MULTIPLIERS, ASTEROID_PARTICLE_COLORS
)
from engine.utils import weighted_random_choice

class Asteroid(pygame.sprite.Sprite):
    """Asteroid class representing obstacles the player must avoid."""
    
    def __init__(self, particle_system, asset_loader, type_id=None, size_category=None, difficulty="Normal Space", screen_width=None, screen_height=None):
        """Initialize an asteroid with random properties.
        
        Args:
            particle_system: ParticleSystem instance for visual effects
            asset_loader: AssetLoader instance for loading images
            type_id: Optional specific asteroid type (0-6) to use
            size_category: Optional specific size category to use
            difficulty: Current game difficulty level
            screen_width: Width of the screen (defaults to SCREEN_WIDTH from constants)
            screen_height: Height of the screen (defaults to SCREEN_HEIGHT from constants)
        """
        super().__init__()
        
        # Store the difficulty
        self.difficulty = difficulty
        
        # Store screen dimensions
        self.screen_width = screen_width if screen_width is not None else SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else SCREEN_HEIGHT
        
        # Particle system for effects
        self.particle_system = particle_system
        
        # Determine the asteroid type (0-6) based on weighted probability or provided value
        if type_id is not None:
            self.asteroid_type = type_id
        else:
            self.asteroid_type = weighted_random_choice(ASTEROID_TYPE_WEIGHTS)
        
        # Determine size category based on asteroid type restrictions and provided value
        if size_category is not None:
            self.size_category = size_category
        else:
            allowed_sizes = ASTEROID_SIZE_RESTRICTIONS[self.asteroid_type]
            self.size_category = random.choice(allowed_sizes)
        
        # Calculate actual size based on category
        size_range = ASTEROID_SIZES[self.size_category]
        self.actual_size = random.randint(size_range["min"], size_range["max"])
        
        # Load and scale asteroid image from the appropriate resolution directory
        res_dir = asset_loader.image_size_dir  # Get the resolution dir (1x, 2x, 3x)
        asteroid_path = os.path.join("assets/images", res_dir, f"a{self.asteroid_type}.png")
        
        self.image_original = asset_loader.load_image(
            asteroid_path, 
            scale=(self.actual_size, self.actual_size)
        )
        
        # Add difficulty-based visual effects
        self._apply_difficulty_effects()
        
        self.image = self.image_original.copy()
        
        # Determine spawn position (outside screen edges)
        spawn_side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        
        if spawn_side == 0:  # Top
            x = random.randint(0, self.screen_width)
            y = -self.actual_size
        elif spawn_side == 1:  # Right
            x = self.screen_width + self.actual_size
            y = random.randint(0, self.screen_height)
        elif spawn_side == 2:  # Bottom
            x = random.randint(0, self.screen_width)
            y = self.screen_height + self.actual_size
        else:  # Left
            x = -self.actual_size
            y = random.randint(0, self.screen_height)
            
        # Set position and create rect
        self.position = Vector2(x, y)
        self.rect = self.image.get_rect(center=self.position)
        
        # Determine speed based on size (smaller = faster)
        base_speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        multiplier = ASTEROID_SPEED_MULTIPLIERS[self.size_category]
        self.speed = base_speed * multiplier
        
        # Calculate velocity toward center-ish of screen (with randomization)
        target_x = self.screen_width // 2 + random.randint(-200, 200)
        target_y = self.screen_height // 2 + random.randint(-150, 150)
        
        direction = Vector2(target_x - x, target_y - y).normalize()
        self.velocity = direction * self.speed
        
        # Rotation properties
        self.rotation = 0
        self.rotation_speed = random.uniform(-50, 50)  # Degrees per second
        
        # Collision properties
        self.radius = self.actual_size // 2
        
        # Damage calculation based on type and size
        base_damage = ASTEROID_BASE_DAMAGE[self.asteroid_type]
        size_multiplier = ASTEROID_SIZE_DAMAGE_MULTIPLIERS[self.size_category]
        self.damage = int(base_damage * size_multiplier)
        
        # Particle effect properties
        self.fire_intensity = max(0.3, (self.asteroid_type / 6) * 0.8)  # Controls intensity of fire effect
        self.particle_cooldown = 0
        self.particle_rate = 0.08  # Seconds between particle emissions
        
    def _apply_difficulty_effects(self):
        """Apply visual effects to asteroids based on difficulty level."""
        # Skip for lowest difficulty
        if self.difficulty == "Empty Space":
            return
            
        # Define difficulty-based color tinting
        difficulty_tints = {
            "Normal Space": None,  # No tint for normal
            "We did not agree on that": (255, 220, 150, 50),  # Slight orange tint
            "You kidding": (255, 150, 100, 80),  # Orange-red tint
            "Hell No!!!": (255, 100, 100, 100)   # Red tint
        }
        
        tint = difficulty_tints.get(self.difficulty)
        if tint:
            # Create a tint surface
            tint_surface = pygame.Surface(self.image_original.get_size(), pygame.SRCALPHA)
            tint_surface.fill(tint)
            
            # Apply the tint
            self.image_original.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
        # Add glow for higher difficulties
        if self.difficulty in ["You kidding", "Hell No!!!"]:
            # Create larger glow surface
            glow_size = int(self.actual_size * 1.2)
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Define glow color based on asteroid type
            glow_alpha = 100 if self.difficulty == "Hell No!!!" else 60
            if self.asteroid_type >= 5:  # Most dangerous asteroids
                glow_color = (255, 50, 50, glow_alpha)  # Red glow
            elif self.asteroid_type >= 3:
                glow_color = (255, 150, 50, glow_alpha)  # Orange glow
            else:
                glow_color = (255, 200, 50, glow_alpha)  # Yellow glow
                
            # Draw the glow
            pygame.draw.circle(
                glow_surface,
                glow_color,
                (glow_size // 2, glow_size // 2),
                glow_size // 2
            )
            
            # Create a larger image to accommodate the glow
            temp_img = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Center the original image on the temp surface
            orig_rect = self.image_original.get_rect(center=(glow_size // 2, glow_size // 2))
            
            # Draw glow first, then original image
            temp_img.blit(glow_surface, (0, 0))
            temp_img.blit(self.image_original, orig_rect)
            
            # Update image_original with the new glowing version
            self.image_original = temp_img
            
            # Update radius for collision to remain accurate to the asteroid, not the glow
            self.radius = self.actual_size // 2
    
    def update(self, dt, joystick=None):
        """Update the asteroid position and effects.
        
        Args:
            dt: Time delta in seconds
            joystick: Unused, included for compatibility with sprite group updates
        """
        # Update position
        self.position += self.velocity * dt
        self.rect.center = self.position
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotate(self.image_original, self.rotation)
        self.rect = self.image.get_rect(center=self.position)
        
        # Remove if off screen with buffer
        buffer = self.actual_size * 2
        if (self.position.x < -buffer or 
            self.position.x > self.screen_width + buffer or
            self.position.y < -buffer or
            self.position.y > self.screen_height + buffer):
            self.kill()
            
        # Handle particle effects
        self.particle_cooldown -= dt
        if self.particle_cooldown <= 0:
            self.emit_fire_particles()
            self.particle_cooldown = self.particle_rate
    
    def emit_fire_particles(self):
        """Emit fire particle effects behind the asteroid based on its type and difficulty."""
        if not self.particle_system:
            return
            
        # Get asteroid velocity direction
        velocity_direction = self.velocity.normalize()
        
        # Calculate the direction opposite to movement (where the trail should go)
        trail_direction = -velocity_direction
        
        # Calculate base particle count based on asteroid type and difficulty
        base_count = 1 + self.asteroid_type // 2  # 1-4 base particles depending on type
        
        # Increase particle count for higher difficulties
        difficulty_particle_multipliers = {
            "Empty Space": 0.5,
            "Normal Space": 1.0,
            "We did not agree on that": 1.5,
            "You kidding": 2.0,
            "Hell No!!!": 3.0
        }
        
        particle_multiplier = difficulty_particle_multipliers.get(self.difficulty, 1.0)
        final_count = max(1, int(base_count * particle_multiplier))
        
        # Calculate cone properties
        cone_width_factor = 0.4  # Controls width of the cone at its base
        cone_width = self.radius * cone_width_factor
        
        # Get perpendicular direction for creating the cone shape
        perp_angle = math.atan2(velocity_direction.y, velocity_direction.x) + (math.pi / 2)
        perp_vector = Vector2(math.cos(perp_angle), math.sin(perp_angle))
        
        # Emit particles to form the cone shape
        for i in range(final_count):
            # For each base particle, emit a small cluster to form the cone
            cluster_size = 2  # Number of particles in each cluster
            
            for j in range(cluster_size):
                # Calculate offset perpendicular to movement direction
                # More central for higher type asteroids to create a more focused trail
                max_offset = cone_width * (1.0 - (self.asteroid_type / 12))
                random_offset = random.uniform(-max_offset, max_offset)
                
                # Calculate perpendicular offset
                perp_offset_x = perp_vector.x * random_offset
                perp_offset_y = perp_vector.y * random_offset
                
                # Calculate how far back from center to start the particle
                # Higher type asteroids have trail starting more inside the asteroid
                center_ratio = 1.0 - (abs(random_offset) / max_offset)  # 0 to 1, 1 at center
                trail_start_factor = 0.2 + ((1.0 - center_ratio) * 0.3)
                emission_distance = self.radius * trail_start_factor
                
                # Calculate actual emission position
                emit_x = self.position.x + perp_offset_x + (trail_direction.x * emission_distance)
                emit_y = self.position.y + perp_offset_y + (trail_direction.y * emission_distance)
                
                # Calculate particle velocity
                # Particles near center move faster and straighter
                base_speed = self.speed * (0.5 + (self.asteroid_type * 0.05))
                speed_factor = 0.8 + (center_ratio * 0.4)
                
                # Add slight randomness to direction
                random_angle = random.uniform(-0.2, 0.2)
                direction_angle = math.atan2(trail_direction.y, trail_direction.x) + random_angle
                final_direction = Vector2(math.cos(direction_angle), math.sin(direction_angle))
                
                # Final velocity
                particle_speed = base_speed * speed_factor
                vel_x = final_direction.x * particle_speed
                vel_y = final_direction.y * particle_speed
                
                # Size based on asteroid type and position in cone
                min_size = 1 + (self.asteroid_type // 3)
                max_size = 2 + (self.asteroid_type // 2)
                
                # Center particles are slightly larger
                if center_ratio > 0.7:
                    min_size += 1
                    max_size += 1
                
                # Calculate lifetime - center particles live slightly longer
                min_lifetime = 0.1 + (center_ratio * 0.1) + (self.asteroid_type * 0.02)
                max_lifetime = 0.2 + (center_ratio * 0.1) + (self.asteroid_type * 0.04)
                
                # Emit the particle
                self.particle_system.emit_particles(
                    emit_x, emit_y,
                    ASTEROID_PARTICLE_COLORS,
                    count=1,
                    velocity_range=((vel_x*0.9, vel_x*1.1), (vel_y*0.9, vel_y*1.1)),
                    size_range=(min_size, max_size),
                    lifetime_range=(min_lifetime, max_lifetime),
                    fade=True
                ) 