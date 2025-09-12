SIZE_SUFFIXES = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]

class BlockDevice:
    device_object: str
    device_size: int
    device_model: str

    def __init__(self, device_size: int, device_model: str, device_object: str):
        self.device_size = device_size
        self.device_model = device_model
        self.device_object = device_object

    def get_size_readable(self):
        size_readable = self.device_size
        suffix = 0
        while not (size_readable / 1024.) < 1 and suffix < len(SIZE_SUFFIXES):
            suffix += 1
            size_readable = size_readable / 1024.

        size_readable = '%.2f' % size_readable
        return str(size_readable) + SIZE_SUFFIXES[suffix]

    def print_device(self):
        print("{" +
              str(self.device_size) + ", " +
              self.device_model + ", " +
              self.device_object + ", " +
              "}")