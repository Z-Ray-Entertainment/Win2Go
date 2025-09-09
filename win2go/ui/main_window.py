import gi

from win2go.usb import find_usb_devices

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

@Gtk.Template(resource_path="/de/z_ray/win2go/blp/main_window.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "Win2GoMainWindow"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        find_usb_devices()
