import os
from pprint import pprint

import gi
from gi.overrides.Gio import Gio
from gi.repository import GLib
from gi.repository.GioUnix import FileDescriptorBased

gi.require_version('GioUnix', '2.0')

from pydbus import SystemBus

size_suffixes = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]

bus = SystemBus()
udisks2_bus = bus.get('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
udisks2_manager = bus.get('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2/Manager')
udisks2_object_manager = udisks2_bus['org.freedesktop.DBus.ObjectManager']

def is_ntfs_supported() -> bool:
    manager_properties = udisks2_manager['org.freedesktop.DBus.Properties']
    supported_filesystems = manager_properties.Get('org.freedesktop.UDisks2.Manager', 'SupportedFilesystems')
    return 'ntfs' in supported_filesystems

def mount_iso_image(file):
    manager_interface = udisks2_manager['org.freedesktop.UDisks2.Manager']
    fd = os.open(file.get_path(), os.O_RDONLY)
    print(fd)
    manager_interface.LoopSetup(fd, {
            'offset': None,
            'size': None,
            'read-only': True,
            'no-part-scan': None,
        }) # TODO: Options as GLib.Variant.

def find_removable_media():
    devices_found = []

    ud2_managed_objects = udisks2_object_manager.GetManagedObjects()
    for managed_object in ud2_managed_objects:
        drive_interfaces = bus.get('org.freedesktop.UDisks2', managed_object)
        device_properties = drive_interfaces['org.freedesktop.DBus.Properties']
        try:
            if device_properties.Get('org.freedesktop.UDisks2.Drive', 'Removable'):
                device_model = device_properties.Get('org.freedesktop.UDisks2.Drive', 'Model')
                device_size = device_properties.Get('org.freedesktop.UDisks2.Drive', 'Size')
                if device_size > 0:
                    devices_found.append(BlockDevice(device_size, device_model, managed_object))
        except GLib.GError: # Not all Devices have the .Drive Interface (e.g. loop devices)
            pass

    return devices_found

class BlockDevice:
    device_object: str
    device_size: int
    device_model: str
    device_transport: str

    def __init__(self, device_size, device_model, device_object):
        self.device_size = device_size
        self.device_model = device_model
        self.device_object = device_object

    def get_size_readable(self):
        size_readable = self.device_size
        suffix = 0
        while not (size_readable / 1024.) < 1 and suffix < len(size_suffixes):
            suffix += 1
            size_readable = size_readable / 1024.

        size_readable = '%.2f' % size_readable
        return str(size_readable) + size_suffixes[suffix]

    def print_device(self):
        print("{" +
              str(self.device_size) + ", " +
              self.device_model + ", " +
              self.device_object + ", " +
              "}")