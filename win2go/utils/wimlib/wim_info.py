from typing import List

from win2go.utils.wimlib.windows_edition import WindowsEdition


class WIMInfo:
    images: List[WindowsEdition]
    boot_index: int
    path: str
    guid: str # 0x....
    version: int
    image_count: int
    compression: str
    chunk_size: int
    part_number: List[int] # x/y
    size: int # bytes
    attributes: str

    def __init__(self, path: str, guid: str, version: int, image_count: int, compression: str, chunk_size: int,
                 part_number: List[int], size: int, boot_index: int, attributes: str, images: List[WindowsEdition]):
        self.boot_index = boot_index
        self.path = path
        self.guid = guid
        self.version = version
        self.image_count = image_count
        self.compression = compression
        self.chunk_size = chunk_size
        self.part_number = part_number
        self.size = size
        self.attributes = attributes
        self.images = images