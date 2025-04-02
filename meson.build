# wallpaper-rotator/meson.build

project('wallpaper-rotator',
  version : '0.1.0', # Set your app version
  license : 'GPL-3.0-or-later', # Match your COPYING file
  meson_version : '>= 0.60', # Recommended minimum
  default_options : [ 'warning_level=1' ])

# Application ID
app_id = 'io.github.tmeier_lang.WallpaperRotator'
# Python Module name derived from App ID
py_module_name = app_id.underscorify() # io_github_tmeier_lang_WallpaperRotator

# Find Python 3
python = import('python').find_installation() 
py_dep = python.dependency()

# Project Dependencies
gnome = import('gnome')
i18n = import('i18n') # For potential future translations
gtk_dep = dependency('gtk4', version : '>= 4.6')
adw_dep = dependency('libadwaita-1', version : '>= 1.1')

deps = [gtk_dep, adw_dep, py_dep]

# Install Python source files into a subdirectory matching the module name
py_sources = files(
  'src/__init__.py',
  'src/main.py',
  'src/application.py',
  'src/window.py'
)

python.install_sources(
  py_sources,
  # Just specify the subdirectory within the default install location
  subdir: py_module_name 
)

# Install GSettings Schema
install_data('data/schemas/' + app_id + '.gschema.xml',
  install_dir : join_paths(get_option('datadir'), 'glib-2.0', 'schemas')
)
# Compile schema post-install
meson.add_install_script('glib-compile-schemas', join_paths(get_option('prefix'), get_option('datadir'), 'glib-2.0', 'schemas'))

# Configure and Install .desktop file
# No translation needed yet, just configure
conf_desktop = configuration_data()
conf_desktop.set('APP_ID', app_id)
# EXEC_PATH removed - using python -m in Exec line directly

desktop_file = configure_file(
  input: join_paths('data', 'desktop', app_id + '.desktop.in'),
  output: app_id + '.desktop',
  configuration: conf_desktop
)
install_data(desktop_file, install_dir: join_paths(get_option('datadir'), 'applications'))
# Update .desktop file cache post-install
meson.add_install_script('update-desktop-database', join_paths(get_option('prefix'), get_option('datadir'), 'applications'))


# Configure and Install AppStream Metainfo file
conf_metainfo = configuration_data()
conf_metainfo.set('APP_ID', app_id)
conf_metainfo.set('VERSION', meson.project_version())
# Get current date using run_command for cross-platform compatibility
date_cmd = run_command('date', '+%Y-%m-%d', check: true)
conf_metainfo.set('DATE', date_cmd.stdout().strip())

metainfo_file = configure_file(
  input: join_paths('data', 'metainfo', app_id + '.metainfo.xml.in'),
  output: app_id + '.metainfo.xml',
  configuration: conf_metainfo
)
install_data(metainfo_file, install_dir: join_paths(get_option('datadir'), 'metainfo'))
# Validate AppStream file during build (optional but recommended)
test('validate-metainfo', find_program('appstream-util', 'appstreamcli', required: false),
     args: ['validate', '--nonet', metainfo_file])


# Install Icons
# foreach size : ['48x48', '64x64', '128x128', '256x256', '512x512'] # List PNG sizes you provide
#   install_data(join_paths('data', 'icons', 'hicolor', size, 'apps', app_id + '.png'),
#     install_dir : join_paths(get_option('datadir'), 'icons', 'hicolor', size, 'apps')
#   )
#endforeach
install_data(join_paths('data', 'icons', 'hicolor', 'scalable', 'apps', app_id + '.svg'),
  install_dir : join_paths(get_option('datadir'), 'icons', 'hicolor', 'scalable', 'apps')
)
# Update icon cache post-install
meson.add_install_script('gtk-update-icon-cache', '-qtf', join_paths(get_option('prefix'), get_option('datadir'), 'icons', 'hicolor'))

# --- End of meson.build ---