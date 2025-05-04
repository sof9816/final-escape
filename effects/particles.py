"""
Particle system for Asteroid Navigator game.
"""
import pygame
import random
from pygame.math import Vector2
from constants import MAX_PARTICLES, PARTICLE_LIFETIME

class Particle:
    """Individual particle for visual effects."""
    
    def __init__(self, x, y, color, velocity=(0, 0), size=2, lifetime=PARTICLE_LIFETIME, gravity=False, fade=True):
        """Initialize a particle with position, color, and optional parameters.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: RGB color tuple
            velocity: Initial velocity (x, y)
            size: Particle size in pixels
            lifetime: How long the particle lasts in seconds
            gravity: Whether gravity affects the particle
            fade: Whether the particle fades out over time
        """
        self.x = x
        self.y = y
        self.color = color
        self.original_color = color  # Store original color for alpha calculations
        self.velocity = Vector2(velocity)
        self.size = size
        self.lifetime = lifetime
        self.age = 0.0
        self.gravity = gravity
        self.fade = fade
        
    def update(self, dt):
        """Update the particle position and age.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            Boolean indicating if the particle is still alive
        """
        # Update position
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt
        
        # Apply gravity if enabled
        if self.gravity:
            self.velocity.y += 50 * dt  # Gravity acceleration
            
        # Update age
        self.age += dt
        
        # Check if the particle is still alive
        return self.age < self.lifetime
        
    def draw(self, surface):
        """Draw the particle on the given surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Calculate alpha for fading
        if self.fade:
            # Linear fade from 255 to 0 over lifetime
            alpha = 255 * (1 - (self.age / self.lifetime))
            # Create color with alpha
            r, g, b = self.original_color
            self.color = (r, g, b, int(alpha))
            
        # Draw the particle
        if self.fade:
            # For fading particles, we need to use a temporary surface with per-pixel alpha
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                self.color, 
                (self.size, self.size), 
                self.size
            )
            surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))
        else:
            # For non-fading particles, we can draw directly
            pygame.draw.circle(
                surface, 
                self.color, 
                (int(self.x), int(self.y)), 
                self.size
            )

class ParticleSystem:
    """Manages multiple particles for visual effects."""
    
    def __init__(self, max_particles=MAX_PARTICLES):
        """Initialize the particle system.
        
        Args:
            max_particles: Maximum number of particles allowed at once
        """
        self.max_particles = max_particles
        self.particles = []
        
    def add_particle(self, particle):
        """Add a particle to the system.
        
        Args:
            particle: Particle object to add
        """
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
        
    def emit_particles(self, x, y, color_range, count, velocity_range=None, 
                      size_range=None, lifetime_range=None, gravity=False, fade=True):
        """Emit multiple particles at once.
        
        Args:
            x: X coordinate to emit from
            y: Y coordinate to emit from
            color_range: List of possible colors to choose from
            count: Number of particles to emit
            velocity_range: ((min_x, max_x), (min_y, max_y)) for random velocities
            size_range: (min_size, max_size) for random sizes
            lifetime_range: (min_lifetime, max_lifetime) for random lifetimes
            gravity: Whether particles are affected by gravity
            fade: Whether particles fade out over time
        """
        # Use default ranges if not specified
        if velocity_range is None:
            velocity_range = ((-20, 20), (-20, 20))
            
        if size_range is None:
            size_range = (1, 3)
            
        if lifetime_range is None:
            lifetime_range = (0.5, 1.5)
            
        # Create the specified number of particles
        for _ in range(count):
            # Random color from the range
            color = random.choice(color_range)
            
            # Random velocity
            velocity = (
                random.uniform(velocity_range[0][0], velocity_range[0][1]),
                random.uniform(velocity_range[1][0], velocity_range[1][1])
            )
            
            # Random size
            size = random.uniform(size_range[0], size_range[1])
            
            # Random lifetime
            lifetime = random.uniform(lifetime_range[0], lifetime_range[1])
            
            # Create and add the particle
            self.add_particle(Particle(
                x, y, color, velocity, size, lifetime, gravity, fade
            ))
    
    def update(self, dt):
        """Update all particles in the system.
        
        Args:
            dt: Time delta in seconds
        """
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.update(dt)]
        
    def draw(self, surface):
        """Draw all particles in the system.
        
        Args:
            surface: Pygame surface to draw on
        """
        for particle in self.particles:
            particle.draw(surface) 