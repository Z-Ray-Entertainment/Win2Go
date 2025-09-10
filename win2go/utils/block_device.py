from win2go.utils.sysutils import lsblk


def find_block_devices():
    block_devices = lsblk()
    found_devices = []
    for device in block_devices["blockdevices"]:
        device_name: str = device["name"]
        device_size: str = device["size"]
        device_model: str = device["model"]
        device_transport = device["tran"]

        if device_transport == "usb":
            usb_device: BlockDevice = BlockDevice(device_name.strip(), device_size.strip(), device_model.strip(), device_transport.strip())
            found_devices.append(usb_device)
    return found_devices

class BlockDevice:
    device_name: str
    device_size: str
    device_model: str
    device_transport: str

    def __init__(self, device_name, device_size, device_model, device_transport):
        self.device_name = device_name
        self.device_size = device_size
        self.device_model = device_model
        self.device_transport = device_transport

    def print_device(self):
        print("{" +
              self.device_name + ", " +
              self.device_size + ", " +
              self.device_model + ", " +
              self.device_transport +
              "}")