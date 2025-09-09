import gi

from win2go.block_device import find_block_devices

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

@Gtk.Template(resource_path="/de/z_ray/win2go/blp/main_window.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "Win2GoMainWindow"
    block_devices: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_devices = find_block_devices()

