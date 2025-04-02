# Wallpaper Rotator

A simple GTK/Adwaita application for GNOME to automatically rotate desktop wallpapers from a selected folder at a set interval.

## Features

* Select wallpaper folder
* Set rotation interval (minutes)
* Manual next/previous wallpaper
* Preview current wallpaper
* (Planned: Status icon via AppIndicator)

## Building and Installing

### Prerequisites

* Meson (>= 0.60)
* Ninja
* Python 3
* GTK4 (>= 4.6) development libraries
* LibAdwaita (>= 1.1) development libraries
* (Optional but Recommended) `flatpak`, `flatpak-builder`, `org.gnome.Sdk//46`

### Using Meson (Local Install)

```bash
meson setup _build --prefix=$HOME/.local
ninja -C _build install
# Log out and log back in, or update env ($PATH, caches)
# Run via application menu or:
# python3 -m io_github_tmeier_lang_WallpaperRotator.main