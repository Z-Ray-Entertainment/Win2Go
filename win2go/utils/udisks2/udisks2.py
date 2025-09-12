import os

import gi
from gi.repository import GLib

from win2go.utils.udisks2.block_device import BlockDevice

gi.require_version('GioUnix', '2.0')

from pydbus import SystemBus

bus = SystemBus()
udisks2_bus = bus.get('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
udisks2_manager = bus.get('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2/Manager')
udisks2_object_manager = udisks2_bus['org.freedesktop.DBus.ObjectManager']

def mount_iso_image(file):
    manager_interface = udisks2_manager['org.freedesktop.UDisks2.Manager']
    fd = os.open(file.get_path(), os.O_RDONLY)

    auth = GLib.Variant('b', 0)
    readonly = GLib.Variant('b', True)
    fd_variant = GLib.Variant('h', fd)

    manager_interface.LoopSetup(0, {'fd': fd_variant,
                                    'auth.no_user_interaction': auth,
                                    'read-only': readonly,
                                }) # TODO: Options as GLib.Variant.