import os
import re
from typing import List

from dasbus.connection import SystemMessageBus
from dasbus.error import DBusError
from dasbus.unix import GLibClientUnix
from gi.overrides import GLib
from gi.repository.GLib import Variant, VariantType
from gi.repository.Gio import File, FileQueryInfoFlags

from win2go.utils.udisks2.drive import Drive

sys_bus = SystemMessageBus()

drive_to_block_devices = {}
supported_file_systems = []

sandbox_regex = re.compile('/run/user/[1-9][0-9]*/doc/[a-z0-9]*/.*')

selected_drive: Drive | None = None


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


def setup_windows_drive(drive: Drive):
    global selected_drive
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


def _delete_partitions() -> None:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              selected_drive.get_top_level_block_device(),
                              "org.freedesktop.UDisks2.PartitionTable")

    for partition in proxy.Partitions:
        print("Deleting partition " + partition)
        partition_proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                                            partition,
                                            "org.freedesktop.UDisks2.Partition")
        partition_proxy.Delete({}, callback=_callback_delete_partition)


def _callback_delete_partition(call) -> None:
    print(call)
    _create_boot_partition()


def _create_boot_partition() -> str:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              selected_drive.get_top_level_block_device(),
                              "org.freedesktop.UDisks2.PartitionTable")

    variant_type = VariantType.new("s")
    mkfs_args = GLib.Variant.new_array(variant_type, [Variant.new_string("-F"), Variant.new_string("32")])

    offset = 0  # At start of device
    size = 512 * 1024 * 1024  # 512 MiB
    type_gpt = ""
    name = "BOOT"
    options = {}
    format_type = "vfat"
    format_options = {
        "label": GLib.Variant.new_string("BOOT"),
        "mkfs-args": mkfs_args,
    }

    return proxy.CreatePartitionAndFormat(
        offset, size, type_gpt, name, options, format_type, format_options, callback=_callback_create_boot_partition
    )


def _callback_create_boot_partition(call) -> None:
    print(call)


_get_block_devices()
_get_supported_filesystems()
