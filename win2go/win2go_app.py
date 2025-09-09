import gi

from win2go.ui.main_window import MainWindow

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk

class Win2Go(Adw.Application):
    win: MainWindow

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()
