# wallpaper-rotator/meson.build

project('wallpaper-rotator',
  version : '0.1.0', # Set your app version
  license : 'GPL-3.0-or-later', # Match your COPYING file
  meson_version : '>= 0.60', # Recommended minimum
  default_options : [ 'warning_level=1' ])

# --- Configuration ---
app_id = 'io.github.tmeier_lang.WallpaperRotator'
py_module_name = app_id.underscorify() # io_github_tmeier_lang_WallpaperRotator
# Use a simple name for the actual executable file
simple_exec_name = 'wallpaper-rotator' 

# --- Dependencies ---
python = import('python').find_installation() 
py_dep = python.dependency()

gnome = import('gnome')
i18n = import('i18n') # For potential future translations
gtk_dep = dependency('gtk4', version : '>= 4.6') # Adjusted version
adw_dep = dependency('libadwaita-1', version : '>= 1.1') # Adjusted version

deps = [gtk_dep, adw_dep, py_dep]

# --- Python Sources ---
py_sources = files(
  'src/__init__.py',
  'src/main.py', # Assuming you are using main.py as the entry point script name
  # If you kept __main__.py, change the line above to 'src/__main__.py'
  'src/application.py',
  'src/window.py'
)

python.install_sources(
  py_sources,
  subdir: py_module_name 
)

# --- GSettings Schema ---
install_data('data/schemas/' + app_id + '.gschema.xml',
  install_dir : join_paths(get_option('datadir'), 'glib-2.0', 'schemas')
)
meson.add_install_script('glib-compile-schemas', join_paths(get_option('prefix'), get_option('datadir'), 'glib-2.0', 'schemas'))

# --- Desktop File ---
conf_desktop = configuration_data()
conf_desktop.set('APP_ID', app_id)
# Pass the simple executable name to the desktop file template
conf_desktop.set('EXEC_NAME', simple_exec_name) 

desktop_file = configure_file(
  input: join_paths('data', 'desktop', app_id + '.desktop.in'),
  output: app_id + '.desktop',
  configuration: conf_desktop # Use the configuration data
)
install_data(desktop_file, install_dir: join_paths(get_option('datadir'), 'applications'))
meson.add_install_script('update-desktop-database', join_paths(get_option('prefix'), get_option('datadir'), 'applications'))

# --- AppStream Metainfo ---
conf_metainfo = configuration_data()
conf_metainfo.set('APP_ID', app_id)
conf_metainfo.set('VERSION', meson.project_version())
date_cmd = run_command('date', '+%Y-%m-%d', check: true)
conf_metainfo.set('DATE', date_cmd.stdout().strip())

metainfo_file = configure_file(
  input: join_paths('data', 'metainfo', app_id + '.metainfo.xml.in'),
  output: app_id + '.metainfo.xml',
  configuration: conf_metainfo
)
install_data(metainfo_file, install_dir: join_paths(get_option('datadir'), 'metainfo'))
test('validate-metainfo', find_program('appstream-util', 'appstreamcli', required: false),
     args: ['validate', '--nonet', metainfo_file])

# --- Icons ---
# PNG loop commented out - assuming SVG only for now
# foreach size : ['48x48', '64x64', '128x128', '256x256', '512x512'] 
#   install_data(join_paths('data', 'icons', 'hicolor', size, 'apps', app_id + '.png'),
#     install_dir : join_paths(get_option('datadir'), 'icons', 'hicolor', size, 'apps')
#   )
# endforeach
install_data(join_paths('data', 'icons', 'hicolor', 'scalable', 'apps', app_id + '.svg'),
  install_dir : join_paths(get_option('datadir'), 'icons', 'hicolor', 'scalable', 'apps')
)
meson.add_install_script('gtk-update-icon-cache', '-qtf', join_paths(get_option('prefix'), get_option('datadir'), 'icons', 'hicolor'))

# --- Executable Script Installation ---
# Install the wrapper script (or __main__.py if you used that) 
# but rename the installed file to the simple name
install_data(
  # Make sure this path points to the script you intend to run
  # Using wrapper script:
  'data/bin/' + app_id + '.sh.in', 
  # OR Using __main__.py directly (ensure only one install_data block for the executable is active):
  # 'src/__main__.py', 
  
  # Rename the installed script to the simple name
  rename : simple_exec_name, # <--- USE SIMPLE NAME FOR INSTALLED FILE
  install_dir : join_paths(get_option('bindir')), # Install to /app/bin
  install_mode : 'rwxr-xr-x' # Make executable
)

# --- End of meson.build ---