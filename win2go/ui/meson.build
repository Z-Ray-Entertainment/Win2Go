blueprints = custom_target('blueprints',
  input: files(
    'main_window.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '--minify', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

user_interface_sources = files([
    'main_window.py',
    '__init__.py'
])

install_data(user_interface_sources, install_dir: moduledir)