# Final Escape

A space-themed arcade game where you navigate a ship through dangerous asteroid fields while trying to survive as long as possible.

## Game Overview

In Final Escape, you control a spaceship trying to survive as long as possible while navigating through increasingly dangerous asteroid fields. The game features different types of asteroids with varying damage levels, and the difficulty increases over time.

## Controls

- Arrow keys: Move the ship
- ESC: Pause/Return to menu
- Enter/Space: Select menu items

## Features

- Enhanced menu system with smooth transitions and visual feedback
- Multiple difficulty levels that affect asteroid spawn rates and types
- Settings menu with customizable options:
  - Sound toggle (on/off)
  - Star opacity adjustment
  - Difficulty selection
- Different types of asteroids with varying damage levels
- Health system with visual health bar
- Scoring system based on survival time
- Particle system for visual effects
- Parallax star field background
- Game state system (menu, countdown, playing, game over)
- Custom soundtrack for different game states

## Directory Structure

```
final-escape/
├── assets/             # Game assets
│   ├── images/         # Images and sprites
│   │   └── asteroids/  # Asteroid sprites
│   ├── sound/          # Music and sound effects
│   └── fonts/          # Font files (optional)
├── data/               # User data and settings
├── effects/            # Visual effects
├── entities/           # Game entities
├── menu/               # Menu components
├── settings/           # Settings management
├── states/             # Game states
├── constants.py        # Game constants
└── main.py             # Main entry point
```

## Requirements

- Python 3.6+
- Pygame 2.0+

## Installation

1. Ensure you have Python and Pygame installed:

   ```
   pip install pygame
   ```

2. Clone the repository:

   ```
   git clone https://github.com/yourusername/final-escape.git
   ```

3. Run the game:
   ```
   python main.py
   ```

## Recent Updates

- Enhanced menu system with better spacing and visual feedback
- Fixed transition issues between game states
- Improved settings menu with adjustable star opacity
- Added smooth animations and transitions between menus
- Fixed various rendering issues for better performance
- Improved game over screen to properly wait for user input

## Credits

- Game developed as a learning project
- Music and sound assets included in the repository
