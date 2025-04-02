# src/main.py

import sys

# Import the application class from the other file in the same package
from .application import WallpaperRotatorApp

def main():
    """Application entry point"""
    app = WallpaperRotatorApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())