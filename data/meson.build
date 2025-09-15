application_id = 'de.z_ray.Win2Go'

scalable_dir = join_paths('icons', 'hicolor', 'scalable', 'apps')
install_data(
  join_paths(scalable_dir, ('@0@.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), scalable_dir)
)

symbolic_dir = join_paths('icons', 'hicolor', 'symbolic', 'apps')
install_data(
  join_paths(symbolic_dir, ('@0@-symbolic.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), symbolic_dir)
)

custom_icons = join_paths('icons')
install_data(
  join_paths(custom_icons, 'windows-logo.svg'),
  join_paths(custom_icons, 'usb-device.svg'),
  install_dir: join_paths(get_option('datadir'), custom_icons)
)

blueprints = custom_target('blueprints',
  input: files(
    'blp/main_window.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('win2go',
  'win2go.gresource.xml',
  gresource_bundle: true,
  dependencies: blueprints,
  install: true,
  install_dir: pkgdatadir,
)

bcd_dir = join_paths(pkgdatadir, 'win2go', 'bcd')
bcd_files = files([
    'bcd/BCD',
    'bcd/boot.reg'
])
install_data(bcd_files, install_dir: bcd_dir)