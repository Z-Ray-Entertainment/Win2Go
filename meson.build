project('win2go',
  version: '1.0',
  meson_version: '>= 0.62.0',
  default_options: ['warning_level=2', 'werror=false'],
)

gnome = import('gnome')
i18n = import('i18n')
i18n.gettext('win2go', preset: 'glib')

appstream_file = 'de.z_ray.Win2Go.metainfo.xml'
install_data(appstream_file, install_dir: join_paths(get_option('datadir'), 'metainfo'))

desktop_file='de.z_ray.Win2Go.desktop'
install_data(desktop_file, install_dir: join_paths(get_option('datadir'), 'applications'))

subdir('win2go')
subdir('data')

gnome.post_install(
    gtk_update_icon_cache: false,
    update_desktop_database: true,
)