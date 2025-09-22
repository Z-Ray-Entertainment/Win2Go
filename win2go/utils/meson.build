utils_dir = join_paths(moduledir, 'utils')
utils_sources = files([
    '__init__.py',
    'sysutils.py'
])

subdir('udisks2')
subdir('wimlib')
subdir('bcd')

install_data(utils_sources, install_dir: utils_dir)