"""
Utility functions for the Asteroid Navigator game.
"""
import random

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