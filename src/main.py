#!/usr/bin/env python3 
# src/main.py

import sys

try:
    # Make sure this is the absolute import:
    from io_github_tmeier_lang_WallpaperRotator.application import WallpaperRotatorApp
except ImportError as e:
    sys.exit(1) # Exit if import fails

def main():
    app = WallpaperRotatorApp()
    result = app.run(sys.argv)
    return result

if __name__ == "__main__":
    sys.exit(main())