# src/application.py

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gio, GLib

# Import the window class from the other file in the same package
from .window import WallpaperRotatorWindow

class WallpaperRotatorApp(Adw.Application):
    """The main application class"""

    # Define App ID centrally
    APP_ID = "io.github.tmeier_lang.WallpaperRotator"

    def __init__(self, **kwargs):
        super().__init__(application_id=self.APP_ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        self.win = None
        # Connect lifecycle signals
        self.connect('activate', self.on_activate)
        # You might add a 'startup' signal handler here later for one-time setup

    def on_activate(self, app):
        """Called when the application is activated"""
        # Create the main window if it doesn't exist
        if not self.win:
            self.win = WallpaperRotatorWindow(application=self)

        # Present the window (makes it visible and brings it to front)
        self.win.present()
