import os
import re
from collections.abc import Callable
from typing import List

from dasbus.connection import SystemMessageBus
from dasbus.error import DBusError
from dasbus.unix import GLibClientUnix
from gi.overrides import GLib
from gi.repository.GLib import VariantType
from gi.repository.Gio import File, FileQueryInfoFlags

from win2go.utils.udisks2.drive import Drive

BOOT_SIZE = 512 * 1024 * 1024

sys_bus = SystemMessageBus()

drive_to_block_devices = {}
supported_file_systems = []

sandbox_regex = re.compile('/run/user/[1-9][0-9]*/doc/[a-z0-9]*/.*')

selected_drive: Drive | None = None
windows_boot: str = ""
windows_main: str = ""
windows_drive_created = False
setup_done_callback: Callable


def is_udisks2_supported() -> bool:
    try:
        proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                                  "/org/freedesktop/UDisks2",
                                  "org.freedesktop.DBus.Peer")
        proxy.Ping()
        return True
    except DBusError:
        return False


def get_missing_filesystems(fs_to_look_up: List[str]) -> List[str]:
    missing_fs = []
    for fs in fs_to_look_up:
        if fs not in supported_file_systems:
            missing_fs.append(fs)
    return missing_fs


def get_managed_objects() -> List[str]:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              "/org/freedesktop/UDisks2",
                              "org.freedesktop.DBus.ObjectManager")
    return proxy.GetManagedObjects()


def find_removable_media() -> List[Drive]:
    devices_found = []
    for managed in get_managed_objects():
        managed_properties = sys_bus.get_proxy("org.freedesktop.UDisks2",
                                               managed,
                                               "org.freedesktop.DBus.Properties")
        try:
            if managed_properties.Get("org.freedesktop.UDisks2.Drive", "Removable"):
                model = managed_properties.Get("org.freedesktop.UDisks2.Drive", "Model")
                size = managed_properties.Get("org.freedesktop.UDisks2.Drive", "Size")
                if size.unpack() > 0:
                    devices_found.append(Drive(size.unpack(), model.unpack(), managed, drive_to_block_devices[managed]))

        except DBusError:  # Not all Devices have the .Drive Interface (e.g. loop devices)
            pass
    return devices_found


def loop_setup(file: File) -> str | None:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              "/org/freedesktop/UDisks2/Manager",
                              "org.freedesktop.UDisks2.Manager",
                              client=GLibClientUnix)

    file_path = file.get_path()  # Sandbox path, as fallback
    try:
        file_info = file.query_info("xattr::document-portal.host-path", FileQueryInfoFlags.NONE, None)
        real_path = file_info.get_attribute_string("xattr::document-portal.host-path")
        if real_path is not None:  # Is None if attribute does not exist
            file_path = real_path
        else:
            if sandbox_regex.match(file_path):  # File path is sandbox path, does not work!
                return None
    except GLib.Error:
        print("Can not get real path. Stuck with sandbox")
    fd = os.open(file_path, os.O_RDONLY)
    readonly = GLib.Variant.new_byte(True)
    loop_path = proxy.LoopSetup(fd, {"read-only": readonly, }, )
    # TODO: Mount loop_path into sandbox to get rid of --filesystem=/run/media/
    return loop_path


def filesystem_mount(object_path: str) -> str:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              object_path,
                              "org.freedesktop.UDisks2.Filesystem")
    return proxy.Mount({})


def find_block_devices_for_drive(drive_path: str) -> List[str]:
    return drive_to_block_devices[drive_path]


def setup_windows_drive(drive: Drive, callback: Callable = None):
    print("Setting up drive {} for Windows...".format(drive.get_readable_drive_identification()))
    global selected_drive, setup_done_callback
    setup_done_callback = callback
    if selected_drive is None:
        selected_drive = drive
        _delete_partitions()
    else:
        print("Operation in progress")


def _get_block_devices():
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              "/org/freedesktop/UDisks2/Manager")
    for block in proxy.GetBlockDevices({}):
        block_proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                                        block,
                                        "org.freedesktop.UDisks2.Block")
        drive = block_proxy.Drive
        drive_entry = drive_to_block_devices.get(drive)
        if not drive_entry:
            drive_to_block_devices[drive] = [block]
        else:
            drive_entry.append(block)


def _get_supported_filesystems():
    global supported_file_systems
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              "/org/freedesktop/UDisks2/Manager")
    supported_file_systems = proxy.SupportedFilesystems


def _delete_partitions(call=None) -> None:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              selected_drive.get_top_level_block_device(),
                              "org.freedesktop.UDisks2.PartitionTable")

    if len(proxy.Partitions) > 0:
        print("Deleting partition " + proxy.Partitions[0] + "...")
        partition_proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                                            proxy.Partitions[0],
                                            "org.freedesktop.UDisks2.Partition")
        try:
            partition_proxy.Delete({}, callback=_delete_partitions)
        except DBusError as e:
            print(e)
    else:
        _create_boot_partition()


def _create_boot_partition():
    print("Creating BOOT partition...")
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              selected_drive.get_top_level_block_device(),
                              "org.freedesktop.UDisks2.PartitionTable")

    variant_type = VariantType.new("s")
    mkfs_args = GLib.Variant.new_array(variant_type, [
        GLib.Variant.new_string("-F"),
        GLib.Variant.new_string("32")
    ])

    format_options = {
        "label": GLib.Variant.new_string("BOOT"),
        "mkfs-args": mkfs_args,
    }

    proxy.CreatePartitionAndFormat(
        0, BOOT_SIZE, "", "BOOT", {}, "vfat", format_options, callback=_callback_create_boot_partition
    )


def _callback_create_boot_partition(call):
    global windows_boot
    windows_boot = call()
    print("BOOT created at " + windows_boot)
    _create_windows_main_partition()


def _create_windows_main_partition():
    print("Creating WINDOWS partition...")
    boot_proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                                   windows_boot,
                                   "org.freedesktop.UDisks2.Partition")
    boot_offset = boot_proxy.Offset
    boot_size = boot_proxy.Size

    variant_type = VariantType.new("s")
    mkfs_args = GLib.Variant.new_array(variant_type, [
        GLib.Variant.new_string("-f"),
    ])

    offset = boot_offset + boot_size  # After BOOT
    options = {
        "partition-type": GLib.Variant.new_string(string="primary")
    }
    format_options = {
        "label": GLib.Variant.new_string("WINDOWS"),
        "mkfs-args": mkfs_args
    }

    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              selected_drive.get_top_level_block_device(),
                              "org.freedesktop.UDisks2.PartitionTable")

    proxy.CreatePartitionAndFormat(
        offset, 0, "", "WINDOWS", options, "ntfs", format_options, callback=_callback_create_windows_main_partition
    )


def _callback_create_windows_main_partition(call):
    global windows_main, selected_drive, windows_drive_created
    windows_main = call()
    print("WINDOWS created at " + windows_main)
    selected_drive = None
    windows_drive_created = True
    if setup_done_callback is not None:
        setup_done_callback()

_get_block_devices()
_get_supported_filesystems()
