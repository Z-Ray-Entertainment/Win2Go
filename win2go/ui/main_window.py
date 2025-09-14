import sys
from typing import List

import gi

from win2go import const
from win2go.ui.block_device_item import get_list_store_expression, build_block_device_model
from win2go.ui.windows_edition_item import get_edition_list_store_expression, build_windows_edition_model
from win2go.utils.udisks2.drive import Drive
from win2go.utils.udisks2.loop_device import LoopDevice
from win2go.utils.udisks2.udisks2_dasbus import find_removable_media, loop_setup, get_missing_filesystems, \
    is_udisks2_supported, setup_windows_drive
from win2go.utils.wimlib.wim_info import WIMInfo
from win2go.utils.wimlib.wimlib import get_wim_info
from win2go.utils.wimlib.windows_edition import WindowsEdition

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from gi.repository.Gtk import DropDown, Button, FileFilter, TextView


def _on_close_error_and_exit(_dialog, result):
    sys.exit(1)


@Gtk.Template(resource_path="/de/z_ray/win2go/blp/main_window.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "Win2GoMainWindow"
    device_drop_down: DropDown = Gtk.Template.Child()
    open_iso: Button = Gtk.Template.Child()
    bt_about: Button = Gtk.Template.Child()
    file_filter_image: FileFilter = Gtk.Template.Child()
    windows_edition_drop_down: DropDown = Gtk.Template.Child()
    text_view_changes: TextView = Gtk.Template.Child()
    bt_flash: Button = Gtk.Template.Child()

    file_dialog: Gtk.FileDialog

    image_file: LoopDevice
    all_removable_drives: List[Drive]
    wim_info: WIMInfo
    selected_windows_edition: WindowsEdition
    selected_drive: Drive | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_udisks2_supported():
            self._create_error_udisks2_not_supported()
        else:
            missing_fs = get_missing_filesystems(["ntfs", "udf", "vfat"])
            if len(missing_fs) > 0:
                self._create_error_unsupported_filesystem_dialog(missing_fs)
            else:
                self.all_removable_drives = find_removable_media()
                if len(self.all_removable_drives) > 0:
                    self.selected_drive = self.all_removable_drives[0]
                else:
                    self.selected_drive = None

                self.device_drop_down.set_expression(get_list_store_expression())
                self.device_drop_down.set_model(build_block_device_model(self.all_removable_drives))
                self.device_drop_down.connect("notify::selected-item", self.on_block_device_selected_item)

                self.open_iso.connect("clicked", lambda *_: self.open_image())
                self.bt_about.connect("clicked", self._open_about)
                self.bt_flash.connect("clicked", self._do_flash)
                self._update_changes()

    def open_image(self):
        Gtk.FileDialog(default_filter=self.file_filter_image).open(self, None, self.on_image_opened)

    def on_image_opened(self, file_dialog, result):
        iso_file = file_dialog.open_finish(result)
        loop_path = loop_setup(iso_file)
        if loop_path is None:
            self._create_error_sandbox_path_dialog()
        else:
            self.open_iso.set_label(iso_file.get_basename())
            self.image_file = LoopDevice(loop_path)
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

    def _create_error_udisks2_not_supported(self):
        dialog = Adw.AlertDialog(
            heading=_("UDisks2 Error"),
            body=_("This system does not support UDisks2."),
            close_response="okay",
        )

        dialog.add_response("close", _("Close"))
        dialog.choose(self, None, _on_close_error_and_exit)
        dialog.set_response_appearance("close", Adw.ResponseAppearance.DESTRUCTIVE)

    def _create_error_sandbox_path_dialog(self, *_args):
        dialog = Adw.AlertDialog(
            heading=_("Sandbox Error"),
            body=_(
                "Win2Go can not retrieve the real image file path. Please allow user home directory access manually." +
                "Or update to xdg-desktop-portal 1.20."),
            close_response="okay",
        )

        dialog.add_response("close", _("Close"))
        dialog.choose(self, None, _on_close_error_and_exit)
        dialog.set_response_appearance("close", Adw.ResponseAppearance.DESTRUCTIVE)

    def _create_error_unsupported_filesystem_dialog(self, missing_fs):
        dialog = Adw.AlertDialog(
            heading=_("Unsupported Filesystem"),
            body=_("This system lacks support for {filesystem}. Win2Go can not proceed".format(filesystem=missing_fs)),
            close_response="okay",
        )

        dialog.add_response("close", _("Close"))
        dialog.choose(self, None, _on_close_error_and_exit)
        dialog.set_response_appearance("close", Adw.ResponseAppearance.DESTRUCTIVE)

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
            changes += _(
                "Drive {device} will be erased"
                .format(device=self.selected_drive.get_readable_drive_identification())
            )

        text_buffer: Gtk.TextBuffer = self.text_view_changes.get_buffer()
        text_buffer.set_text(changes)
        print("Changes:", changes)

    def _do_flash(self, _widget):
        self._create_flash_confirmation(self.selected_drive.get_readable_drive_identification())

    def _create_flash_confirmation(self, device):
        dialog = Adw.AlertDialog(
            heading="Flash?",
            body=_(
                "Flashing the device is an irreversible operation and all data on {device} will be lost. Continue?"
                .format(device=device)
            ),
            close_response="cancel",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("flash", "Flash")
        dialog.set_response_appearance("flash", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.choose(self, None, self._on_flash_confirm_selected)

    def _on_flash_confirm_selected(self, _dialog, task):
        response = _dialog.choose_finish(task)
        if response == "flash":
            self._do_flash_for_real()

    def _do_flash_for_real(self):
        print("Flashing...")
        setup_windows_drive(self.selected_drive, callback=self._drive_prepared_callback)

    def _drive_prepared_callback(self):
        print("Drive was setup")
