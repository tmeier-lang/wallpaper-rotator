#!/usr/bin/env python3

import gi
import os
import random
import time
import sys # <-- Added import sys
from pathlib import Path
from threading import Thread

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, GdkPixbuf

class WallpaperRotatorWindow(Adw.ApplicationWindow):
    # Minimum delay between wallpaper changes (in seconds) to prevent system overload
    MIN_CHANGE_DELAY = 5.0 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize instance variables
        self.wallpaper_dir = str(Path.home() / "Pictures")  # Default directory
        self.wallpapers = []
        self.current_index = 0
        self.interval = 60 # Default interval in minutes
        self.is_running = False
        self.settings = Gio.Settings.new("org.gnome.desktop.background")
        self.last_change_time = 0.0 # Timestamp of the last successful wallpaper change

        # Set window properties
        self.set_title("Wallpaper Rotator")
        self.set_default_size(600, 400)

        # --- UI Setup (Identical to your original code) --- 
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
        self.preview_image.set_size_request(300, 200) # Consider if fixed size is best
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
        # Ensure minimum interval is respected visually (already was 1 min)
        self.interval_spin.set_adjustment(Gtk.Adjustment(value=self.interval, lower=1, upper=1440, step_increment=1, page_increment=10))
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
        # --- End of UI Setup ---
        
        # Initialize
        self.load_wallpapers()
        self.update_preview() # Update preview based on initial index

    def load_wallpapers(self):
        """Load wallpapers from the selected directory"""
        self.wallpapers = [] # Clear previous list
        self.current_index = 0 # Reset index
        try:
            self.wallpaper_dir = self.folder_entry.get_text()
            # Basic check if directory exists
            if not os.path.isdir(self.wallpaper_dir):
                 self.status_label.set_text(f"Error: Directory not found '{self.wallpaper_dir}'")
                 return

            supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp') # Added webp
            self.wallpapers = [
                os.path.join(self.wallpaper_dir, f) 
                for f in os.listdir(self.wallpaper_dir) 
                if os.path.isfile(os.path.join(self.wallpaper_dir, f)) and f.lower().endswith(supported_extensions)
            ]
            
            if self.wallpapers:
                # Try to find the current system wallpaper in the list
                try:
                    current_wallpaper_uri = self.settings.get_string("picture-uri")
                    if current_wallpaper_uri.startswith("file://"):
                       current_wallpaper_path = current_wallpaper_uri.replace("file://", "")
                       if current_wallpaper_path in self.wallpapers:
                           self.current_index = self.wallpapers.index(current_wallpaper_path)
                except GLib.Error as e:
                     print(f"Could not read current wallpaper setting: {e}") # Non-fatal

                self.status_label.set_text(f"Loaded {len(self.wallpapers)} wallpapers")
                self.update_preview() # Update preview after loading
            else:
                self.status_label.set_text("No compatible wallpapers found in selected directory")
                self.preview_image.clear() # Clear preview if no images
        except PermissionError:
             self.status_label.set_text(f"Error: Permission denied for '{self.wallpaper_dir}'")
        except Exception as e:
            self.status_label.set_text(f"Error loading wallpapers: {str(e)}")
            self.preview_image.clear() # Clear preview on error

    def set_wallpaper(self, path):
        """Set the wallpaper to the given path, respecting rate limit"""
        # --- Rate Limiting Check ---
        current_time = time.monotonic() 
        if current_time - self.last_change_time < self.MIN_CHANGE_DELAY:
            print(f"Rate limit: Too soon to change wallpaper. Waiting {self.MIN_CHANGE_DELAY}s.")
            self.status_label.set_text(f"Waiting... ({self.MIN_CHANGE_DELAY:.1f}s delay)")
            return False
        # --- End Rate Limiting Check ---

        try:
            # Ensure path is absolute and exists (basic sanity check)
            abs_path = os.path.abspath(path)
            if not os.path.isfile(abs_path):
                 self.status_label.set_text(f"Error: File not found '{abs_path}'")
                 return False

            uri = Path(abs_path).as_uri() # Use pathlib for correct URI generation
            
            print(f"Setting wallpaper to: {uri}") # Debug output
            self.settings.set_string("picture-uri", uri)
            self.settings.set_string("picture-uri-dark", uri)
            # Gio.Settings.sync() # Usually not needed for desktop schemas, uncomment if changes lag

            self.last_change_time = current_time # Update timestamp *after* successful attempt
            self.update_preview() # Update preview *after* attempting set
            return True
        except Exception as e:
            print(f"Error setting wallpaper GSettings: {e}")
            self.status_label.set_text(f"Error setting wallpaper: {str(e)}")
            return False

    def update_preview(self):
        """Update the wallpaper preview"""
        if not self.wallpapers or self.current_index >= len(self.wallpapers):
            self.preview_image.clear()
            self.status_label.set_text("No wallpaper selected or list empty")
            return
            
        current_path = self.wallpapers[self.current_index]
        try:
            # Check if file exists before trying to load
            if not os.path.isfile(current_path):
                 self.status_label.set_text(f"Preview Error: File missing '{os.path.basename(current_path)}'")
                 self.preview_image.clear()
                 return

            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                current_path, 
                300, 200, # Dimensions for preview
                True # Preserve aspect ratio
            )
            self.preview_image.set_from_pixbuf(pixbuf)
            filename = os.path.basename(current_path)
            # Status update happens here, potentially overwriting rate limit message quickly
            # Consider deferring this status update slightly if needed
            self.status_label.set_text(f"Current: {filename}") 
        except GLib.Error as e: # Catch specific GdkPixbuf errors
             print(f"Error loading preview pixbuf for {current_path}: {e}")
             self.status_label.set_text(f"Preview Error: Cannot load '{os.path.basename(current_path)}'")
             self.preview_image.clear() # Clear preview on error
        except Exception as e:
            print(f"Unexpected error updating preview for {current_path}: {e}")
            self.status_label.set_text(f"Error updating preview: {str(e)}")
            self.preview_image.clear() # Clear preview on error

    def wallpaper_thread(self):
        """Thread to change wallpapers at intervals"""
        print("Wallpaper thread started.")
        while self.is_running:
            interval_seconds = self.interval * 60
            # Check interval sanity (should be caught by SpinButton, but belt-and-suspenders)
            if interval_seconds < self.MIN_CHANGE_DELAY:
                print(f"Warning: Interval ({interval_seconds}s) is less than minimum delay ({self.MIN_CHANGE_DELAY}s). Adjusting sleep.")
                interval_seconds = self.MIN_CHANGE_DELAY

            # Sleep for the interval
            print(f"Thread sleeping for {interval_seconds} seconds...")
            # Use time.monotonic() for sleeping relative to last wake time if precise interval is critical
            # For simplicity, time.sleep is usually sufficient here.
            time.sleep(interval_seconds) 
            
            if not self.is_running:
                print("Wallpaper thread stopping during sleep.")
                break # Exit loop if stopped during sleep
                
            # Schedule wallpaper change on the main GTK thread
            print("Thread scheduling wallpaper change.")
            GLib.idle_add(self.change_wallpaper_random)
        
        print("Wallpaper thread finished.")

    def change_wallpaper_random(self):
        """Change to a random wallpaper (called via GLib.idle_add)"""
        if not self.wallpapers or not self.is_running: # Double check state
            return False # Indicate no action taken
            
        if len(self.wallpapers) <= 1:
             print("Only one wallpaper, not changing randomly.")
             # Optionally set the single wallpaper if it wasn't set?
             # self.set_wallpaper(self.wallpapers[self.current_index]) 
             return False

        old_index = self.current_index
        # Ensure the new index is different from the old one
        while self.current_index == old_index:
            self.current_index = random.randint(0, len(self.wallpapers) - 1)
        
        print(f"Randomly selected index: {self.current_index}")
        # set_wallpaper handles rate limiting and preview update
        return self.set_wallpaper(self.wallpapers[self.current_index])

    # --- Event Handlers (Mostly unchanged, rely on set_wallpaper for rate limit) ---
    def on_folder_clicked(self, button):
        """Open folder chooser dialog"""
        dialog = Gtk.FileChooserDialog(
            title="Select Wallpaper Folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            transient_for=self, # Set transient parent
            modal=True # Make dialog modal
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.ACCEPT
        )
        # Removed unnecessary connection here, using response signal only
        dialog.connect("response", self.on_folder_dialog_response)
        dialog.present() # Use present for dialogs too in GTK4

    def on_folder_dialog_response(self, dialog, response):
        """Handle folder chooser dialog response"""
        if response == Gtk.ResponseType.ACCEPT:
            folder_file = dialog.get_file()
            if folder_file:
                self.folder_entry.set_text(folder_file.get_path())
                self.load_wallpapers() # Reloads list and updates preview
        dialog.destroy()

    def on_prev_clicked(self, button):
        """Go to previous wallpaper"""
        if not self.wallpapers:
            return
            
        self.current_index = (self.current_index - 1) % len(self.wallpapers)
        # set_wallpaper handles rate limiting and preview update
        self.set_wallpaper(self.wallpapers[self.current_index])

    def on_next_clicked(self, button):
        """Go to next wallpaper"""
        if not self.wallpapers:
            return
            
        self.current_index = (self.current_index + 1) % len(self.wallpapers)
        # set_wallpaper handles rate limiting and preview update
        self.set_wallpaper(self.wallpapers[self.current_index])

    def on_start_clicked(self, button):
        """Start/stop automatic wallpaper rotation"""
        if self.is_running:
            print("Stopping rotation...")
            self.is_running = False # Set flag *before* potentially waiting thread finishes
            self.start_button.set_label("Start")
            self.status_label.set_text("Automatic rotation stopped")
            # Thread will exit on its next check of self.is_running
        else:
            # Ensure we have wallpapers to rotate
            if not self.wallpapers:
                self.status_label.set_text("Cannot start: No wallpapers loaded.")
                return

            # Get interval value *before* starting thread
            self.interval = int(self.interval_spin.get_value()) 
            # Double-check interval against minimum practical delay
            if self.interval * 60 < self.MIN_CHANGE_DELAY:
                 self.status_label.set_text(f"Interval too short (min {self.MIN_CHANGE_DELAY}s). Please increase.")
                 # Optionally, force interval_spin value up?
                 # self.interval_spin.set_value(math.ceil(self.MIN_CHANGE_DELAY / 60))
                 # self.interval = int(self.interval_spin.get_value()) 
                 return # Don't start if interval is too low

            print("Starting rotation...")
            self.is_running = True
            self.start_button.set_label("Stop")
            self.status_label.set_text(f"Rotating every {self.interval} minutes")
            
            # Start rotation thread
            thread = Thread(target=self.wallpaper_thread, daemon=True) # Ensure daemon=True
            thread.start()


class WallpaperRotatorApp(Adw.Application):
    """The main application class"""
    def __init__(self, **kwargs):
        # Use the correct, unique application ID
        super().__init__(application_id="io.github.tmeier_lang.WallpaperRotator",
                         flags=Gio.ApplicationFlags.FLAGS_NONE, # Use FLAGS_NONE unless specific flags needed
                         **kwargs)
        self.win = None
        self.connect('activate', self.on_activate)
        
    def on_activate(self, app):
        """Called when the application is activated (main entry point)"""
        if not self.win:
            # Create the main window, passing the application instance
            self.win = WallpaperRotatorWindow(application=self) 
        
        # Present the window (makes it visible and brings to front)
        self.win.present()


if __name__ == "__main__":
    # Create and run the application
    app = WallpaperRotatorApp() 
    exit_status = app.run(sys.argv) # Pass command line arguments
    sys.exit(exit_status)