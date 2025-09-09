pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'win2go')

conf = configuration_data()
conf.set('VERSION', meson.project_version())

python = import('python')
conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('APPID', 'de.z_ray.Win2Go')
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

win2go_bin = configure_file(
  input: '__init__.py',
  output: 'win2go',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x',
)

configure_file(
  input: 'const.py',
  output: 'const.py',
  configuration: conf,
  install: true,
  install_dir: moduledir,
  install_mode: 'r-xr--r--',
)

win2go_sources = files([
    'winlib.py',
    'win2go_app.py',
    'usb.py',
    'sysutils.py'
])

subdir('ui')

install_data(win2go_sources, install_dir: moduledir)