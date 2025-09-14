from typing import List

SIZE_SUFFIXES = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]

class Drive:
    device_object: str
    device_size: int
    device_model: str
    device_block_devices: List[str]

    def __init__(self, device_size: int, device_model: str, device_object: str, block_devices: List[str]):
        self.device_size = device_size
        self.device_model = device_model
        self.device_object = device_object
        self.device_block_devices = block_devices

    def get_size_readable(self):
        size_readable = self.device_size
        suffix = 0
        while not (size_readable / 1024.) < 1 and suffix < len(SIZE_SUFFIXES):
            suffix += 1
            size_readable = size_readable / 1024.

        size_readable = '%.2f' % size_readable
        return str(size_readable) + SIZE_SUFFIXES[suffix]

    def get_top_level_block_device(self) -> str:
        self.device_block_devices.sort()
        return self.device_block_devices[0]

    def get_readable_drive_identification(self) -> str:
        top_level_split = self.get_top_level_block_device().split("/")
        top_level_last = top_level_split[len(top_level_split) - 1]
        return self.device_model + " (" + self.get_size_readable() + ", "  + top_level_last + ")"

    def print_device(self):
        block_dev = "["
        for block in self.device_block_devices:
            block_dev += block + ","
        block_dev += "]"
        print("{" +
              str(self.device_size) + ", " +
              self.device_model + ", " +
              self.device_object + ", " +
              block_dev + ", " +
              "}")