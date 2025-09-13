import os
from typing import List

from dasbus.connection import SystemMessageBus
from dasbus.error import DBusError
from dasbus.unix import GLibClientUnix
from gi.overrides import GLib
from gi.repository.Gio import File

from win2go.utils.udisks2.drive import Drive

sys_bus = SystemMessageBus()
drive_to_block_devices = {}

def get_supported_filesystems() -> List[str]:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              "/org/freedesktop/UDisks2/Manager")
    print(proxy.SupportedFilesystems)
    return proxy.SupportedFilesystems

def is_ntfs_supported() -> bool:
    return "ntfs" in get_supported_filesystems()

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

def loop_setup(file: File) -> str:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              "/org/freedesktop/UDisks2/Manager",
                              "org.freedesktop.UDisks2.Manager",
                              client=GLibClientUnix)

    fd = os.open(file.get_path(), os.O_RDONLY)
    readonly = GLib.Variant.new_byte(True)
    loop_path = proxy.LoopSetup(fd, {"read-only": readonly, },)

    return loop_path

def filesystem_mount(object_path: str) -> str:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2",
                              object_path,
                              "org.freedesktop.UDisks2.Filesystem")
    return proxy.Mount({})

def find_block_devices_for_drive(drive_path: str) -> List[str]:
    return drive_to_block_devices[drive_path]

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

_get_block_devices()