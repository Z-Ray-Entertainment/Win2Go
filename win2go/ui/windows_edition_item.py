import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GObject, Gio

class WindowsEditionItem(GObject.GObject):
    key = GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE, default="")
    value = GObject.Property(
        type=str,
        nick="Value",
        blurb="Value",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )
    edition_name = GObject.Property(
        type=str,
        nick="Name",
        blurb="Name",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )
    edition_index = GObject.Property(
        type=int,
        nick="Name",
        blurb="Name",
        flags=GObject.ParamFlags.READWRITE,
        default=0,
    )


def build_windows_edition_model(found_editions):
    block_device_additions = _build_windows_edition_additions(found_editions)
    block_device_model = Gio.ListStore(item_type=WindowsEditionItem)
    block_device_model.splice(0, 0, block_device_additions)
    return block_device_model

def get_edition_list_store_expression():
    return Gtk.PropertyExpression.new(
        WindowsEditionItem,
        None,
        "value",
    )

def _build_windows_edition_additions(found_editions):
    block_device_additions = []
    for edition in found_editions:
        block_item = WindowsEditionItem(key=edition.edition_name,
                                        value=edition.edition_name,
                                        edition_name=edition.edition_name,
                                        edition_index=edition.edition_index
                                    )
        block_device_additions.append(block_item)
    return block_device_additions