from typing import List

import gi

from win2go import const
from win2go.ui.block_device_item import get_list_store_expression, build_block_device_model
from win2go.ui.windows_edition_item import get_edition_list_store_expression, build_windows_edition_model
from win2go.utils.udisks2.drive import Drive
from win2go.utils.udisks2.loop_device import LoopDevice
from win2go.utils.udisks2.udisks2_dasbus import find_removable_media, loop_setup
from win2go.utils.wimlib.wim_info import WIMInfo
from win2go.utils.wimlib.wimlib import get_wim_info
from win2go.utils.wimlib.windows_edition import WindowsEdition

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from gi.repository.Gtk import DropDown, Button, FileFilter, TextView


@Gtk.Template(resource_path="/de/z_ray/win2go/blp/main_window.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "Win2GoMainWindow"
    device_drop_down: DropDown = Gtk.Template.Child()
    open_iso: Button = Gtk.Template.Child()
    bt_about: Button = Gtk.Template.Child()
    file_filter_image: FileFilter = Gtk.Template.Child()
    windows_edition_drop_down: DropDown = Gtk.Template.Child()
    text_view_changes: TextView = Gtk.Template.Child()

    file_dialog: Gtk.FileDialog

    image_file: LoopDevice
    all_removable_drives: List[Drive]
    wim_info: WIMInfo
    selected_windows_edition: WindowsEdition
    selected_drive: Drive

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.all_removable_drives = find_removable_media()
        if len(self.all_removable_drives) > 0:
            self.selected_drive = self.all_removable_drives[0]

        self.device_drop_down.set_expression(get_list_store_expression())
        self.device_drop_down.set_model(build_block_device_model(self.all_removable_drives))
        self.device_drop_down.connect("notify::selected-item", self.on_block_device_selected_item)

        self.open_iso.connect("clicked", lambda *_: self.open_image())
        self.bt_about.connect("clicked", self._open_about)
        self._update_changes()

    def open_image(self):
        Gtk.FileDialog(default_filter=self.file_filter_image).open(self, None, self.on_image_opened)

    def on_image_opened(self, file_dialog, result):
        iso_file = file_dialog.open_finish(result)
        self.open_iso.set_label(iso_file.get_basename())
        loop_path = loop_setup(iso_file)
        if loop_path is None:
            pass # TODO: Show sandbox path error dialog
        else:
            self.image_file = LoopDevice(loop_setup(iso_file))
            self.image_file.mount()
            self.wim_info = get_wim_info(self.image_file.mount_path)
            self.windows_edition_drop_down.set_visible(True)
            self.windows_edition_drop_down.set_expression(get_edition_list_store_expression())
            self.windows_edition_drop_down.set_model(build_windows_edition_model(self.wim_info))
            self.windows_edition_drop_down.connect("notify::selected-item", self.on_edition_selected)

    def on_block_device_selected_item(self, _drop_down, _selected_item):
        selected_item = _drop_down.get_selected()
        self.selected_drive = self.all_removable_drives[selected_item]
        self._update_changes()

    def on_edition_selected(self, _drop_down, _selected_item):
        selected_item_index = _drop_down.get_selected()
        self.selected_windows_edition = self.wim_info.images[selected_item_index]

    def _open_about(self, _widget):
        dialog = Adw.AboutDialog(
            application_icon=const.APP_ID,
            application_name=const.APP_NAME,
            developer_name="Vortex Acherontic",
            version=const.VERSION,
            comments=_(
                "Win2Go creates persistent and portable installations of Microsoft Windows on USB devices",
            ),
            website="https://z-ray.de",
            issue_url="https://codeberg.org/ZRayEntertainment/win2go/issues",
            support_url="https://codeberg.org/ZRayEntertainment/win2go/issues",
            copyright="© 2025 Vortex Acherontic",
            license_type=Gtk.License.MIT_X11,
            developers=["Imo 'Vortex Acherontic' Hester <vortex@z-ray.de>"],
            artists=["Imo 'Vortex Acherontic' Hester"],
            translator_credits=_("translator-credits"),
        )

        dialog.add_link(
            _("Documentation"),
            "https://docs.z-ray.de/zray-soft/",
        )

        dialog.add_legal_section(
            _("Wimlib"),
            None,
            Gtk.License.GPL_3_0_ONLY
        )
        dialog.add_legal_section(
            _("dasbus"),
            None,
            Gtk.License.LGPL_2_1_ONLY
        )

        dialog.add_acknowledgement_section(_("Special thanks to"), ["jxctn0"])
        dialog.present(self)

    def _update_changes(self):
        print("Update changes...")
        changes: str = ""
        if self.selected_drive is not None:
            device_text = self.selected_drive.device_model + " (" + str(self.selected_drive.device_size) + ")"
            changes += _("Drive {device} will be erased".format(device=device_text))

        text_buffer: Gtk.TextBuffer = self.text_view_changes.get_buffer()
        text_buffer.set_text(changes)
        print("Changes:", changes)