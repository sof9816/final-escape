"""
Helper utilities for Asteroid Navigator.
"""
import pygame
import random
from pygame import mixer
from src.constants import MUSIC_FADE_DURATION

def change_music(music_file, volume=0.5):
    """
    Change background music with cross-fade.
    
    Args:
        music_file: Path to the music file
        volume: Volume level from 0.0 to 1.0
    """
    try:
        mixer.music.fadeout(MUSIC_FADE_DURATION)
        pygame.time.delay(MUSIC_FADE_DURATION // 2)  # Wait for half the fade out time
        mixer.music.load(music_file)
        mixer.music.set_volume(volume)
        mixer.music.play(loops=-1)
    except pygame.error as e:
        print(f"Error changing music: {e}")

def weighted_random_choice(weights_dict):
    """
    Select a random key from a dictionary based on the weight values.
    
    Args:
        weights_dict: Dictionary with keys as options and values as weights.
        
    Returns:
        A randomly selected key based on the weights.
    """
    options = list(weights_dict.keys())
    weights = list(weights_dict.values())
    
    # Generate a random value based on the sum of weights
    total = sum(weights)
    rand_val = random.uniform(0, total)
    
    # Find the option that corresponds to the random value
    cumulative = 0
    for i, weight in enumerate(weights):
        cumulative += weight
        if rand_val <= cumulative:
            return options[i]
    
    # Fallback (shouldn't reach here unless weights sum to 0)
    return options[0] if options else None

def create_fade_surface(width, height):
    """
    Create a surface for fade transitions.
    
    Args:
        width: Surface width
        height: Surface height
        
    Returns:
        Surface configured for fading
    """
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill((0, 0, 0))  # Black surface for fading
    return fade_surface

def fade_in(surface, fade_surface, dt, transition_timer, fade_duration):
    """
    Fade screen in from black.
    
    Args:
        surface: Target surface to draw on
        fade_surface: Pre-created fade surface
        dt: Delta time
        transition_timer: Current transition time
        fade_duration: Total fade duration
    
    Returns:
        (new_transition_timer, new_fade_alpha, is_complete)
    """
    new_transition_timer = transition_timer + dt
    fade_alpha = max(0, int(255 * (1 - new_transition_timer / fade_duration)))
    
    if fade_alpha > 0:
        fade_surface.set_alpha(fade_alpha)
        surface.blit(fade_surface, (0, 0))
        
    return new_transition_timer, fade_alpha, fade_alpha <= 0

def fade_out(surface, fade_surface, dt, transition_timer, fade_duration):
    """
    Fade screen out to black.
    
    Args:
        surface: Target surface to draw on
        fade_surface: Pre-created fade surface
        dt: Delta time
        transition_timer: Current transition time
        fade_duration: Total fade duration
    
    Returns:
        (new_transition_timer, new_fade_alpha, is_complete)
    """
    new_transition_timer = transition_timer + dt
    fade_alpha = min(255, int(255 * (new_transition_timer / fade_duration)))
    
    if fade_alpha < 255:
        fade_surface.set_alpha(fade_alpha)
        surface.blit(fade_surface, (0, 0))
        
    return new_transition_timer, fade_alpha, fade_alpha >= 255 