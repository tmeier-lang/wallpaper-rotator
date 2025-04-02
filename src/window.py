# src/window.py

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
    # Minimum delay between wallpaper changes (in seconds)
    MIN_CHANGE_DELAY = 5.0

    def __init__(self, application, **kwargs): # Pass application instance
        super().__init__(application=application, **kwargs)

        self.app_settings = None
        try:
            # Assumes APP_ID is defined in application object or known
            self.app_settings = Gio.Settings.new(application.APP_ID)
        except GLib.Error as e:
            print(f"Error loading GSettings for {application.APP_ID}: {e}")
            print("Using default values. Ensure schema is installed and compiled.")

        # Initialize instance variables - Read from GSettings
        # Wallpaper Directory
        saved_path = None
        if self.app_settings:
            saved_path = self.app_settings.get_string("wallpaper-folder-path")

        if saved_path and saved_path != 'DEFAULT_PICTURES':
            self.wallpaper_dir = saved_path
        else:
            pics_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
            self.wallpaper_dir = pics_dir if pics_dir else str(Path.home() / "Pictures")
            # Save resolved default back if settings are available and was placeholder
            if self.app_settings and saved_path == 'DEFAULT_PICTURES':
                 try:
                      self.app_settings.set_string("wallpaper-folder-path", self.wallpaper_dir)
                 except GLib.Error as e:
                      print(f"Error saving default wallpaper folder path: {e}")

        # Interval
        if self.app_settings:
            self.interval = self.app_settings.get_int("rotation-interval-minutes")
        else:
            self.interval = 60 # Fallback default

        self.wallpapers = []
        self.current_index = 0
        self.is_running = False
        # Settings for *setting* the wallpaper (org.gnome...)
        self.desktop_settings = Gio.Settings.new("org.gnome.desktop.background")
        self.last_change_time = 0.0

        # Set window properties
        self.set_title("Wallpaper Rotator")
        self.set_default_size(600, 400)

        # --- UI Setup ---
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        header_bar = Adw.HeaderBar()
        main_box.append(header_bar)
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.content_box.set_margin_top(24)
        self.content_box.set_margin_bottom(24)
        self.content_box.set_margin_start(24)
        self.content_box.set_margin_end(24)
        main_box.append(self.content_box)
        self.set_content(main_box)

        self.preview_label = Gtk.Label(label="<b>Current Wallpaper</b>", use_markup=True)
        self.content_box.append(self.preview_label)
        self.preview_image = Gtk.Image(width_request=300, height_request=200)
        self.content_box.append(self.preview_image)

        self.folder_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.folder_label = Gtk.Label(label="Wallpaper Folder:")
        self.folder_entry = Gtk.Entry(text=self.wallpaper_dir, hexpand=True)
        self.folder_button = Gtk.Button(label="Browse...")
        self.folder_button.connect("clicked", self.on_folder_clicked)
        self.folder_box.append(self.folder_label)
        self.folder_box.append(self.folder_entry)
        self.folder_box.append(self.folder_button)
        self.content_box.append(self.folder_box)

        self.interval_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.interval_label = Gtk.Label(label="Change interval (minutes):")
        self.interval_spin = Gtk.SpinButton()
        self.interval_spin.set_adjustment(Gtk.Adjustment(value=self.interval, lower=1, upper=1440, step_increment=1, page_increment=10))
        self.interval_spin.set_value(self.interval)
        self.interval_spin.connect("value-changed", self.on_interval_changed) # Save on change
        self.interval_box.append(self.interval_label)
        self.interval_box.append(self.interval_spin)
        self.content_box.append(self.interval_box)

        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.CENTER)
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

        self.status_label = Gtk.Label(label="Ready")
        self.content_box.append(self.status_label)
        # --- End of UI Setup ---
        self.load_wallpapers()
        # No need to call update_preview here, load_wallpapers calls it if successful

    def load_wallpapers(self):
        # ...(Same as your original code)...
        self.wallpapers = []
        self.current_index = 0
        try:
            self.wallpaper_dir = self.folder_entry.get_text()
            if not os.path.isdir(self.wallpaper_dir):
                 self.status_label.set_text(f"Error: Directory not found '{self.wallpaper_dir}'")
                 return
            supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            self.wallpapers = [
                os.path.join(self.wallpaper_dir, f)
                for f in os.listdir(self.wallpaper_dir)
                if os.path.isfile(os.path.join(self.wallpaper_dir, f)) and f.lower().endswith(supported_extensions)
            ]
            if self.wallpapers:
                try:
                    current_wallpaper_uri = self.desktop_settings.get_string("picture-uri")
                    if current_wallpaper_uri.startswith("file://"):
                       current_wallpaper_path = current_wallpaper_uri.replace("file://", "")
                       if current_wallpaper_path in self.wallpapers:
                           self.current_index = self.wallpapers.index(current_wallpaper_path)
                except GLib.Error as e:
                     print(f"Could not read current wallpaper setting: {e}")
                self.status_label.set_text(f"Loaded {len(self.wallpapers)} wallpapers")
                self.update_preview()
            else:
                self.status_label.set_text("No compatible wallpapers found")
                self.preview_image.clear()
        except PermissionError:
             self.status_label.set_text(f"Error: Permission denied for '{self.wallpaper_dir}'")
        except Exception as e:
            self.status_label.set_text(f"Error loading wallpapers: {str(e)}")
            self.preview_image.clear()

    def set_wallpaper(self, path):
        # ...(Same as your original code, using self.desktop_settings)...
        current_time = time.monotonic()
        if current_time - self.last_change_time < self.MIN_CHANGE_DELAY:
            print(f"Rate limit: Too soon. Waiting {self.MIN_CHANGE_DELAY}s.")
            self.status_label.set_text(f"Waiting... ({self.MIN_CHANGE_DELAY:.1f}s delay)")
            return False
        try:
            abs_path = os.path.abspath(path)
            if not os.path.isfile(abs_path):
                 self.status_label.set_text(f"Error: File not found '{abs_path}'")
                 return False
            uri = Path(abs_path).as_uri()
            print(f"Setting wallpaper to: {uri}")
            self.desktop_settings.set_string("picture-uri", uri)
            self.desktop_settings.set_string("picture-uri-dark", uri)
            self.last_change_time = current_time
            self.update_preview()
            return True
        except Exception as e:
            print(f"Error setting wallpaper GSettings: {e}")
            self.status_label.set_text(f"Error setting wallpaper: {str(e)}")
            return False

    def update_preview(self):
        # ...(Same as your original code)...
        if not self.wallpapers or self.current_index >= len(self.wallpapers):
            self.preview_image.clear()
            self.status_label.set_text("No wallpaper selected or list empty")
            return
        current_path = self.wallpapers[self.current_index]
        try:
            if not os.path.isfile(current_path):
                 self.status_label.set_text(f"Preview Error: File missing '{os.path.basename(current_path)}'")
                 self.preview_image.clear()
                 return
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                current_path, 300, 200, True
            )
            self.preview_image.set_from_pixbuf(pixbuf)
            filename = os.path.basename(current_path)
            self.status_label.set_text(f"Current: {filename}")
        except GLib.Error as e:
             print(f"Error loading preview pixbuf for {current_path}: {e}")
             self.status_label.set_text(f"Preview Error: Cannot load '{os.path.basename(current_path)}'")
             self.preview_image.clear()
        except Exception as e:
            print(f"Unexpected error updating preview for {current_path}: {e}")
            self.status_label.set_text(f"Error updating preview: {str(e)}")
            self.preview_image.clear()

    def wallpaper_thread(self):
        # ...(Same as your original code)...
        print("Wallpaper thread started.")
        while self.is_running:
            interval_seconds = self.interval * 60
            if interval_seconds < self.MIN_CHANGE_DELAY:
                print(f"Warning: Interval ({interval_seconds}s) < min delay ({self.MIN_CHANGE_DELAY}s). Adjusting.")
                interval_seconds = self.MIN_CHANGE_DELAY
            print(f"Thread sleeping for {interval_seconds} seconds...")
            time.sleep(interval_seconds)
            if not self.is_running:
                print("Wallpaper thread stopping during sleep.")
                break
            print("Thread scheduling wallpaper change.")
            GLib.idle_add(self.change_wallpaper_random) # Schedule on main thread
        print("Wallpaper thread finished.")

    def change_wallpaper_random(self):
        # ...(Same as your original code)...
        if not self.wallpapers or not self.is_running:
            return False
        if len(self.wallpapers) <= 1:
             print("Only one wallpaper, not changing randomly.")
             return False
        old_index = self.current_index
        while self.current_index == old_index:
            self.current_index = random.randint(0, len(self.wallpapers) - 1)
        print(f"Randomly selected index: {self.current_index}")
        return self.set_wallpaper(self.wallpapers[self.current_index])

    def on_folder_clicked(self, button):
        # ...(Same as your original code)...
        dialog = Gtk.FileChooserDialog(
            title="Select Wallpaper Folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            transient_for=self, modal=True
        )
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT)
        dialog.connect("response", self.on_folder_dialog_response)
        dialog.present()

    def on_folder_dialog_response(self, dialog, response):
        # ...(Includes saving setting)...
        new_path = None
        if response == Gtk.ResponseType.ACCEPT:
            folder_file = dialog.get_file()
            if folder_file:
                new_path = folder_file.get_path()
                self.folder_entry.set_text(new_path)
                # --- Save the new path to GSettings ---
                if self.app_settings and new_path:
                    try:
                         print(f"Saving wallpaper folder path: {new_path}")
                         self.app_settings.set_string("wallpaper-folder-path", new_path)
                    except GLib.Error as e:
                         print(f"Error saving wallpaper folder path: {e}")
                # --- End Save ---
                self.load_wallpapers() # Reload list and update preview
        dialog.destroy()

    def on_interval_changed(self, spin_button):
        """Save interval when spin button value changes"""
        new_interval = int(spin_button.get_value())
        self.interval = new_interval # Update instance variable too
        if self.app_settings:
            try:
                if self.app_settings.get_int("rotation-interval-minutes") != new_interval:
                    print(f"Saving rotation interval: {new_interval}")
                    self.app_settings.set_int("rotation-interval-minutes", new_interval)
            except GLib.Error as e:
                print(f"Error saving rotation interval: {e}")

    def on_prev_clicked(self, button):
        # ...(Same as your original code)...
        if not self.wallpapers: return
        self.current_index = (self.current_index - 1) % len(self.wallpapers)
        self.set_wallpaper(self.wallpapers[self.current_index])

    def on_next_clicked(self, button):
        # ...(Same as your original code)...
        if not self.wallpapers: return
        self.current_index = (self.current_index + 1) % len(self.wallpapers)
        self.set_wallpaper(self.wallpapers[self.current_index])

    def on_start_clicked(self, button):
        # ...(Includes saving interval just before start)...
        if self.is_running:
            print("Stopping rotation...")
            self.is_running = False
            self.start_button.set_label("Start")
            self.status_label.set_text("Automatic rotation stopped")
        else:
            if not self.wallpapers:
                self.status_label.set_text("Cannot start: No wallpapers loaded.")
                return
            # Save current interval value just before starting
            self.on_interval_changed(self.interval_spin)
            # Use the updated self.interval
            if self.interval * 60 < self.MIN_CHANGE_DELAY:
                 self.status_label.set_text(f"Interval too short (min {self.MIN_CHANGE_DELAY}s). Increase.")
                 return
            print("Starting rotation...")
            self.is_running = True
            self.start_button.set_label("Stop")
            self.status_label.set_text(f"Rotating every {self.interval} minutes")
            thread = Thread(target=self.wallpaper_thread, daemon=True)
            thread.start()