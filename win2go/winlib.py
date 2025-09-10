def create_windows(device_name, image_index, iso_file):
    pass

def get_windows_edition(iso_file):
    found_editions = []
    edition = WindowsEdition("Windows 11 Home", 1)
    found_editions.append(edition)
    return found_editions

class WindowsEdition:
    edition_name: str
    image_index: int

    def __init__(self, edition_name, image_index):
        self.edition_name = edition_name
        self.image_index = image_index