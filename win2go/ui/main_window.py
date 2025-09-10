import gi

from win2go.block_device import find_block_devices

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GObject
from gi.repository.Gtk import DropDown

@Gtk.Template(resource_path="/de/z_ray/win2go/blp/main_window.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "Win2GoMainWindow"
    device_drop_down: DropDown = Gtk.Template.Child()
    block_devices: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_devices = find_block_devices()

        block_device_additions = []
        for bd in self.block_devices:
            display_name = bd.device_model + " (" + bd.device_name + ", " + bd.device_size + ")"
            block_item = BlockDeviceItem(key=bd.device_name,
                                         value=display_name,
                                         device_name=bd.device_name,
                                         device_size=bd.device_size,
                                         device_model=bd.device_model)
            block_device_additions.append(block_item)

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

    def on_selected_item(self, _drop_down, _selected_item):
            selected_item = self.device_drop_down.get_selected_item()
            if selected_item:
                print(selected_item.key,
                      selected_item.value,
                      selected_item.device_name,
                      selected_item.device_size,
                      selected_item.device_model)

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