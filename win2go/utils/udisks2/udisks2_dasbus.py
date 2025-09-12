from typing import List

from dasbus.connection import SystemMessageBus
from dasbus.error import DBusError

from win2go.utils.udisks2.block_device import BlockDevice

sys_bus = SystemMessageBus()

def get_supported_filesystems() -> List[str]:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2", "/org/freedesktop/UDisks2/Manager")
    print(proxy.SupportedFilesystems)
    return proxy.SupportedFilesystems

def is_ntfs_supported() -> bool:
    return "ntfs" in get_supported_filesystems()

def get_managed_objects() -> List[str]:
    proxy = sys_bus.get_proxy("org.freedesktop.UDisks2", "/org/freedesktop/UDisks2", "org.freedesktop.DBus.ObjectManager")
    return proxy.GetManagedObjects()

def find_removable_media() -> List[BlockDevice]:
    devices_found = []
    for managed in get_managed_objects():
        managed_properties = sys_bus.get_proxy("org.freedesktop.UDisks2", managed, "org.freedesktop.DBus.Properties")
        try:
            if managed_properties.Get("org.freedesktop.UDisks2.Drive", "Removable"):
                model = managed_properties.Get("org.freedesktop.UDisks2.Drive", "Model")
                size = managed_properties.Get("org.freedesktop.UDisks2.Drive", "Size")
                if size.unpack() > 0:
                    devices_found.append(BlockDevice(size.unpack(), model.unpack(), managed))
        except DBusError:  # Not all Devices have the .Drive Interface (e.g. loop devices)
            pass
    return devices_found