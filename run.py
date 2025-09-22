#!/usr/bin/env python3
"""
Simple launcher script for the Dating Profile Optimizer
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
from main import DatingProfileApp

if __name__ == "__main__":
    print("Starting Dating Profile Optimizer...")
    print("Loading application...")
    
    try:
        app = DatingProfileApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)