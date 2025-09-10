import gi

from win2go.block_device import find_block_devices, BlockDevice

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GObject
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        block_devices_found = find_block_devices()
        if len(block_devices_found) > 0:
            self.block_device = block_devices_found[0]
        block_device_additions = build_block_device_additions(block_devices_found)
        block_device_model = Gio.ListStore(item_type=BlockDeviceItem)
        block_device_model.splice(0, 0, block_device_additions)
        list_store_expression = Gtk.PropertyExpression.new(
            BlockDeviceItem,
            None,
            "value",
        )

        self.device_drop_down.set_expression(list_store_expression)
        self.device_drop_down.set_model(block_device_model)
        self.device_drop_down.connect("notify::selected-item", self.on_selected_item)

        self.open_iso.connect("clicked", lambda *_: self.open_image())

    def open_image(self):
        Gtk.FileDialog(default_filter=self.file_filter_image).open(self, None, self.on_image_opened)

    def on_image_opened(self, file_dialog, result):
        self.image_file = file_dialog.open_finish(result)
        self.open_iso.set_label(get_file_name(self.image_file))
        self.windows_edition_drop_down.set_visible(True)
        print(f"Selected Image: {get_file_name(self.image_file)}")

    def on_selected_item(self, _drop_down, _selected_item):
            selected_item = self.device_drop_down.get_selected_item()
            self.block_device = BlockDevice(selected_item.device_name, selected_item.device_size, selected_item.device_model, selected_item.device_transport)

class WindowsEditionItem(GObject.GObject):
    key = GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE, default="")
    value = GObject.Property(
        type=int,
        nick="Value",
        blurb="Value",
        flags=GObject.ParamFlags.READWRITE,
        default=0,
    )
    edition_name = GObject.Property(
        type=str,
        nick="Name",
        blurb="Name",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )

class BlockDeviceItem(GObject.Object):
    key = GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE, default="")
    value = GObject.Property(
        type=str,
        nick="Value",
        blurb="Value",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )
    device_name = GObject.Property(
        type=str,
        nick="Name",
        blurb="Name",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )
    device_size = GObject.Property(
        type=str,
        nick="Size",
        blurb="Size",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )
    device_model = GObject.Property(
        type=str,
        nick="Model",
        blurb="Model",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )
    device_transport = GObject.Property(
        type=str,
        nick="Model",
        blurb="Model",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )

def build_block_device_additions(block_devices):
    block_device_additions = []
    for bd in block_devices:
        display_name = bd.device_model + " (" + bd.device_name + ", " + bd.device_size + ")"
        block_item = BlockDeviceItem(key=bd.device_name,
                                     value=display_name,
                                     device_name=bd.device_name,
                                     device_size=bd.device_size,
                                     device_model=bd.device_model,
                                     device_transport=bd.device_transport)
        block_device_additions.append(block_item)
    return block_device_additions

def get_file_name(file):
    info = file.query_info("standard::name", Gio.FileQueryInfoFlags.NONE, None)
    return info.get_name()