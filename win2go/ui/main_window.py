import gi

from win2go.ui.block_device_item import get_list_store_expression, build_block_device_model
from win2go.ui.windows_edition_item import get_edition_list_store_expression, build_windows_edition_model
from win2go.utils.udisks2 import find_removable_media, BlockDevice, mount_iso_image
from win2go.winlib import get_windows_edition, WindowsEdition

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk
from gi.repository.Gtk import DropDown, Button, FileFilter

@Gtk.Template(resource_path="/de/z_ray/win2go/blp/main_window.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "Win2GoMainWindow"
    device_drop_down: DropDown = Gtk.Template.Child()
    open_iso: Button = Gtk.Template.Child()
    file_filter_image: FileFilter = Gtk.Template.Child()
    windows_edition_drop_down: DropDown = Gtk.Template.Child()

    file_dialog: Gtk.FileDialog

    image_file = None
    block_device: BlockDevice
    windows_edition: WindowsEdition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        block_devices_found = find_removable_media()
        if len(block_devices_found) > 0:
            self.block_device = block_devices_found[0]

        self.device_drop_down.set_expression(get_list_store_expression())
        self.device_drop_down.set_model(build_block_device_model(block_devices_found))
        self.device_drop_down.connect("notify::selected-item", self.on_block_device_selected_item)

        self.open_iso.connect("clicked", lambda *_: self.open_image())

    def open_image(self):
        Gtk.FileDialog(default_filter=self.file_filter_image).open(self, None, self.on_image_opened)

    def on_image_opened(self, file_dialog, result):
        self.image_file = file_dialog.open_finish(result)
        self.open_iso.set_label(self.image_file.get_basename())
        mount_iso_image(self.image_file)

        windows_editions_found = get_windows_edition(self.image_file)
        self.windows_edition_drop_down.set_visible(True)
        self.windows_edition_drop_down.set_expression(get_edition_list_store_expression())
        self.windows_edition_drop_down.set_model(build_windows_edition_model(windows_editions_found))
        self.windows_edition_drop_down.connect("notify::selected-item", self.on_edition_selected)

    def on_block_device_selected_item(self, _drop_down, _selected_item):
        selected_item = _drop_down.get_selected_item()
        self.block_device = BlockDevice(selected_item.device_size, selected_item.device_model, selected_item.device_object)

    def on_edition_selected(self, _drop_down, _selected_item):
        selected_item = _drop_down.get_selected_item()
        self.windows_edition = WindowsEdition(selected_item.edition_name, selected_item.edition_index)