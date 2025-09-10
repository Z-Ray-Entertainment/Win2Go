import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject, Gio

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


def build_block_device_model(found_block_devices):
    block_device_additions = _build_block_device_additions(found_block_devices)
    block_device_model = Gio.ListStore(item_type=BlockDeviceItem)
    block_device_model.splice(0, 0, block_device_additions)
    return block_device_model

def get_list_store_expression():
    return Gtk.PropertyExpression.new(
        BlockDeviceItem,
        None,
        "value",
    )

def _build_block_device_additions(block_devices):
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