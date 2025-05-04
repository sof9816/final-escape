# Asteroid Navigator

A space-themed arcade game where you navigate a ship through dangerous asteroid fields.

## Game Overview

In Asteroid Navigator, you control a spaceship trying to survive as long as possible while navigating through increasingly dangerous asteroid fields. Different types of asteroids cause different amounts of damage on collision.

## Controls

- Arrow keys or WASD: Move the ship
- Joystick: Move the ship (if available)

## Features

- Different types of asteroids with varying damage levels
- Health system with visual health bar
- Scoring system based on survival time
- Parallax star field background
- Menu animations
- Soundtrack for different game states
- Gamepad/joystick support

## Directory Structure

```
asteroid_navigator/
├── assets/             # Game assets
│   ├── images/         # Images and sprites
│   ├── sound/          # Music and sound effects
│   └── fonts/          # Font files
├── src/                # Source code
│   ├── core/           # Core game functionality
│   ├── entities/       # Game entities
│   ├── scenes/         # Game scenes
│   ├── ui/             # UI components
│   ├── utils/          # Utility functions
│   ├── constants.py    # Game constants
│   └── main.py         # Main entry point
└── run_game.py         # Wrapper script to run the game
```

## Requirements

- Python 3.6+
- Pygame 2.0+

## Installation

1. Ensure you have Python and Pygame installed.
2. Clone the repository.
3. Run the game:

```
python run_game.py
```

## Credits

- Game developed as a learning project
- Music and sound assets are included in the repository
