# Wallpaper Rotator

A simple GTK4/LibAdwaita application for the GNOME desktop that automatically rotates your wallpaper at a set interval using images from a selected folder.

## Screenshots

![Screenshot 1](https://raw.githubusercontent.com/tmeier-lang/wallpaper-rotator/main/data/screenshots/screenshot1.png)

![Screenshot 2](https://raw.githubusercontent.com/tmeier-lang/wallpaper-rotator/main/data/screenshots/screenshot2.png)


## Features

* Select a folder containing your wallpaper images.
* Set a custom rotation interval (in minutes).
* Automatically change wallpaper at the specified interval when active.
* Manually change to the next or previous wallpaper.
* Displays a preview of the current wallpaper.
* Remembers your selected folder and interval settings between sessions (using GSettings).

## Known Issues / Limitations

* **Wallpaper Not Changing in Flatpak:** Due to Flatpak's security sandbox, the host system's background service currently does not apply the wallpaper change when requested by this application running as a Flatpak. Although the application attempts to set the wallpaper (and internal checks report success), the visual change does not occur. This is likely a restriction preventing sandboxed apps from setting backgrounds using `file://` URIs via the standard GSettings D-Bus interface. Running the application *outside* Flatpak (e.g., via the Local Meson Build) *does* work correctly. A potential fix would involve implementing direct D-Bus calls to the XDG Wallpaper Portal, which is significantly more complex and not yet implemented.

## Installation

The recommended way to install and run Wallpaper Rotator is via Flatpak, **bearing in mind the limitation described above.**

**(Note: This application is not yet published on a remote like Flathub. The following instructions are for building and installing locally from source.)**

### Flatpak (Recommended, with Limitations)

1.  **Prerequisites:**
    * Ensure you have `flatpak` and `flatpak-builder` installed.
    * Install the GNOME 46 SDK (or the version matching the `.yaml` file):
        ```bash
        flatpak install flathub org.gnome.Sdk//46
        ```
2.  **Clone the repository:**
    ```bash
    git clone [https://github.com/tmeier-lang/wallpaper-rotator.git](https://github.com/tmeier-lang/wallpaper-rotator.git)
    cd wallpaper-rotator
    ```
3.  **Build and Install:**
    ```bash
    flatpak-builder --user --install --force-clean _flatpak_build io.github.tmeier_lang.WallpaperRotator.yaml
    ```

### Local Meson Build (Works Fully, Development Focus)

1.  **Prerequisites:**
    * Meson (>= 0.60)
    * Ninja
    * Python 3
    * GTK4 development libraries (>= 4.6)
    * LibAdwaita development libraries (>= 1.1)
2.  **Clone the repository:**
    ```bash
    git clone [https://github.com/tmeier-lang/wallpaper-rotator.git](https://github.com/tmeier-lang/wallpaper-rotator.git)
    cd wallpaper-rotator
    ```
3.  **Ensure File Name Correct:** Please double-check that the desktop entry template file in `data/desktop/` is correctly named `io.github.tmeier_lang.WallpaperRotator.desktop.in`.
4.  **Configure and Install:**
    ```bash
    meson setup _build --prefix=$HOME/.local
    ninja -C _build install
    ```
5.  **Post-Install (Local):**
    * You will likely need to log out and log back in for the desktop environment to see the application icon, `.desktop` file, and GSettings schema.
    * Ensure `$HOME/.local/bin` is in your system `$PATH`.
    * Ensure Python can find modules installed in `$HOME/.local/lib/pythonX.Y/dist-packages` (you may need to configure `PYTHONPATH` manually if your system doesn't include this by default).

## Usage

* **Via Application Menu:** After installation (Flatpak or local install + logout/login), search for "Wallpaper Rotator" in your GNOME application menu/overview.
* **Via Terminal:**
    * **Flatpak:** (Note: Wallpaper changing won't work visually)
        ```bash
        flatpak run io.github.tmeier_lang.WallpaperRotator
        ```
    * **Local Meson Install:** (Requires `$HOME/.local/bin` in PATH and potentially PYTHONPATH setup)
        ```bash
        wallpaper-rotator 
        ```

## Bug Reports & Contributing

Please report any issues or suggest features on the [GitHub Issues](https://github.com/tmeier-lang/wallpaper-rotator/issues) page. Note the known issue regarding Flatpak wallpaper setting. Contributions are welcome!
