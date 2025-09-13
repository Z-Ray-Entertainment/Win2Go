from typing import List

import gi

from win2go.utils.wimlib.wim_info import WIMInfo
from win2go.utils.wimlib.windows_edition import WindowsEdition

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


def build_windows_edition_model(wim_info: WIMInfo):
    block_device_additions = _build_windows_edition_additions(wim_info.images)
    block_device_model = Gio.ListStore(item_type=WindowsEditionItem)
    block_device_model.splice(0, 0, block_device_additions)
    return block_device_model

def get_edition_list_store_expression():
    return Gtk.PropertyExpression.new(
        WindowsEditionItem,
        None,
        "value",
    )

def _build_windows_edition_additions(found_editions: List[WindowsEdition]):
    block_device_additions = []
    for edition in found_editions:
        block_item = WindowsEditionItem(key=edition.display_name,
                                        value=edition.display_name,
                                        edition_name=edition.display_name,
                                        edition_index=edition.index
                                    )
        block_device_additions.append(block_item)
    return block_device_additions