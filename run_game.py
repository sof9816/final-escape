#!/usr/bin/env python3
"""
Run script for Asteroid Navigator.
Run this script from the project root to start the game.
"""
import sys
import os

# Add the project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main function
from src.main import main

if __name__ == "__main__":
    main() 