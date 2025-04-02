#!/usr/bin/env python3

import gi
import os
import random
import time
from pathlib import Path
from threading import Thread

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, GdkPixbuf

class WallpaperRotatorWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize instance variables
        self.wallpaper_dir = str(Path.home() / "Pictures")  # Default directory
        self.wallpapers = []
        self.current_index = 0
        self.interval = 60
        self.is_running = False
        self.settings = Gio.Settings.new("org.gnome.desktop.background")

        # Set window properties
        self.set_title("Wallpaper Rotator")
        self.set_default_size(600, 400)

        # Create the main layout container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Create header bar and set as titlebar
        header_bar = Adw.HeaderBar()
        main_box.append(header_bar)
        
        # Content box with margins
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.content_box.set_margin_top(24)
        self.content_box.set_margin_bottom(24)
        self.content_box.set_margin_start(24)
        self.content_box.set_margin_end(24)
        main_box.append(self.content_box)
        
        # Set the main box as the window's content
        self.set_content(main_box)
        
        # Current wallpaper preview
        self.preview_label = Gtk.Label()
        self.preview_label.set_markup("<b>Current Wallpaper</b>")
        self.content_box.append(self.preview_label)
        
        self.preview_image = Gtk.Image()
        self.preview_image.set_size_request(300, 200)
        self.content_box.append(self.preview_image)
        
        # Folder selection
        self.folder_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.folder_label = Gtk.Label(label="Wallpaper Folder:")
        self.folder_entry = Gtk.Entry()
        self.folder_entry.set_text(self.wallpaper_dir)
        self.folder_button = Gtk.Button(label="Browse...")
        self.folder_button.connect("clicked", self.on_folder_clicked)
        
        self.folder_box.append(self.folder_label)
        self.folder_box.append(self.folder_entry)
        self.folder_box.append(self.folder_button)
        self.content_box.append(self.folder_box)
        
        # Interval selection
        self.interval_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.interval_label = Gtk.Label(label="Change interval (minutes):")
        self.interval_spin = Gtk.SpinButton()
        self.interval_spin.set_adjustment(Gtk.Adjustment(value=60, lower=1, upper=1440, step_increment=1, page_increment=10))
        self.interval_spin.set_value(self.interval)
        
        self.interval_box.append(self.interval_label)
        self.interval_box.append(self.interval_spin)
        self.content_box.append(self.interval_box)
        
        # Control buttons
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.button_box.set_halign(Gtk.Align.CENTER)
        
        self.prev_button = Gtk.Button(label="Previous")
        self.prev_button.connect("clicked", self.on_prev_clicked)
        
        self.start_button = Gtk.Button(label="Start")
        self.start_button.connect("clicked", self.on_start_clicked)
        
        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.on_next_clicked)
        
        self.button_box.append(self.prev_button)
        self.button_box.append(self.start_button)
        self.button_box.append(self.next_button)
        self.content_box.append(self.button_box)
        
        # Status bar
        self.status_label = Gtk.Label(label="Ready")
        self.content_box.append(self.status_label)
        
        # Initialize
        self.load_wallpapers()
        self.update_preview()
    
    def load_wallpapers(self):
        """Load wallpapers from the selected directory"""
        try:
            self.wallpaper_dir = self.folder_entry.get_text()
            self.wallpapers = [os.path.join(self.wallpaper_dir, f) for f in os.listdir(self.wallpaper_dir) 
                              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            
            if self.wallpapers:
                current_wallpaper = self.settings.get_string("picture-uri").replace("file://", "")
                if current_wallpaper in self.wallpapers:
                    self.current_index = self.wallpapers.index(current_wallpaper)
                self.status_label.set_text(f"Loaded {len(self.wallpapers)} wallpapers")
            else:
                self.status_label.set_text("No wallpapers found in selected directory")
        except Exception as e:
            self.status_label.set_text(f"Error loading wallpapers: {str(e)}")
    
    def set_wallpaper(self, path):
        """Set the wallpaper to the given path"""
        try:
            uri = f"file://{path}"
            self.settings.set_string("picture-uri", uri)
            self.settings.set_string("picture-uri-dark", uri)  # For dark mode
            self.update_preview()
            return True
        except Exception as e:
            self.status_label.set_text(f"Error setting wallpaper: {str(e)}")
            return False
    
    def update_preview(self):
        """Update the wallpaper preview"""
        if not self.wallpapers:
            return
            
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                self.wallpapers[self.current_index], 
                300, 200, 
                True
            )
            self.preview_image.set_from_pixbuf(pixbuf)
            filename = os.path.basename(self.wallpapers[self.current_index])
            self.status_label.set_text(f"Current: {filename}")
        except Exception as e:
            self.status_label.set_text(f"Error updating preview: {str(e)}")
    
    def wallpaper_thread(self):
        """Thread to change wallpapers at intervals"""
        while self.is_running:
            # Sleep for the interval
            time.sleep(self.interval * 60)
            
            if not self.is_running:
                break
                
            # Change wallpaper on the main thread
            GLib.idle_add(self.change_wallpaper_random)
    
    def change_wallpaper_random(self):
        """Change to a random wallpaper"""
        if not self.wallpapers:
            return False
            
        old_index = self.current_index
        while len(self.wallpapers) > 1 and self.current_index == old_index:
            self.current_index = random.randint(0, len(self.wallpapers) - 1)
            
        return self.set_wallpaper(self.wallpapers[self.current_index])
    
    # Event handlers
    def on_folder_clicked(self, button):
        """Open folder chooser dialog"""
        dialog = Gtk.FileChooserDialog(
            title="Select Wallpaper Folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.ACCEPT
        )
        dialog.set_transient_for(self)
        
        dialog.connect("response", self.on_folder_dialog_response)
        dialog.show()
    
    def on_folder_dialog_response(self, dialog, response):
        """Handle folder chooser dialog response"""
        if response == Gtk.ResponseType.ACCEPT:
            self.folder_entry.set_text(dialog.get_file().get_path())
            self.load_wallpapers()
            self.update_preview()
        dialog.destroy()
    
    def on_prev_clicked(self, button):
        """Go to previous wallpaper"""
        if not self.wallpapers:
            return
            
        self.current_index = (self.current_index - 1) % len(self.wallpapers)
        self.set_wallpaper(self.wallpapers[self.current_index])
    
    def on_next_clicked(self, button):
        """Go to next wallpaper"""
        if not self.wallpapers:
            return
            
        self.current_index = (self.current_index + 1) % len(self.wallpapers)
        self.set_wallpaper(self.wallpapers[self.current_index])
    
    def on_start_clicked(self, button):
        """Start/stop automatic wallpaper rotation"""
        if self.is_running:
            self.is_running = False
            self.start_button.set_label("Start")
            self.status_label.set_text("Automatic rotation stopped")
        else:
            self.interval = int(self.interval_spin.get_value())
            self.is_running = True
            self.start_button.set_label("Stop")
            self.status_label.set_text(f"Rotating every {self.interval} minutes")
            
            # Start rotation thread
            thread = Thread(target=self.wallpaper_thread)
            thread.daemon = True
            thread.start()


class WallpaperRotatorApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        
    def on_activate(self, app):
        self.win = WallpaperRotatorWindow(application=self)
        self.win.present()


if __name__ == "__main__":
    app = WallpaperRotatorApp(application_id="org.example.wallpaperrotator")
    app.run(None)
