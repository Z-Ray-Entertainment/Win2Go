import re

from win2go.sysutils import lsblk

blacklist = re.compile('(zram|sr)\d')


def find_usb_devices():
    block_devices = lsblk()
    found_devices = []
    for device in block_devices["blockdevices"]:
        device_name: str = device["name"]
        device_size: str = device["size"]
        device_model: str = device["model"]

        if blacklist.search(device_name) is None:
            usb_device: USBDevice = USBDevice(device_name.strip(), device_size.strip(), device_model.strip())
            found_devices.append(usb_device)


class USBDevice:
    device_name: str
    device_size: str
    device_model: str

    def __init__(self, device_name, device_size, device_model):
        self.device_name = device_name
        self.device_size = device_size
        self.device_model = device_model