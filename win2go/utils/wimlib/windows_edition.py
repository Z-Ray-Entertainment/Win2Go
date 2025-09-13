class WindowsEdition:
    index: int
    name: str
    description: str
    display_name: str
    display_description: str
    directory_count: int
    file_count: int
    total_bytes: int
    hard_link_bytes: int
    creation_time: str
    last_modification_time: str
    architecture: str
    product_name: str
    edition_id: str
    installation_type: str
    product_type: str
    product_suite: str
    languages: str
    default_language: str
    system_root: str
    major_version: int
    minor_version: int
    build: int
    service_pack_build: int
    service_pack_level: int
    flags: str
    wimboot_compatible: bool

    def __init__(self, index: int, name: str, description: str, display_name: str, display_description: str,
                 directory_count: int, file_count: int, total_bytes: int, hard_link_bytes: int, creation_time: str,
                 last_modification_time: str, architecture: str, product_name: str, edition_id: str,
                 installation_type: str, product_type: str, product_suite: str, languages: str, default_language: str,
                 system_root: str, major_version: int, minor_version: int, build: int, service_pack_build: int,
                 service_pack_level: int, flags: str, wimboot_compatible: bool):
        self.index = index
        self.name = name
        self.description = description
        self.display_name = display_name
        self.display_description = display_description
        self.directory_count = directory_count
        self.file_count = file_count
        self.total_bytes = total_bytes
        self.hard_link_bytes = hard_link_bytes
        self.creation_time = creation_time
        self.last_modification_time = last_modification_time
        self.architecture = architecture
        self.product_name = product_name
        self.edition_id = edition_id
        self.installation_type = installation_type
        self.product_type = product_type
        self.product_suite = product_suite
        self.languages = languages
        self.default_language = default_language
        self.system_root = system_root
        self.major_version = major_version
        self.minor_version = minor_version
        self.build = build
        self.service_pack_build = service_pack_build
        self.service_pack_level = service_pack_level
        self.flags = flags
        self.wimboot_compatible = wimboot_compatible