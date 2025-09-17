import re
import uuid

WINDOWS_RESUME_GUID = "\\$windows-resume-guid\\$"
WINDOWS_LOADER_GUID = "\\$windows-loader-guid\\$"
# '<loaderguid-here>\0\0' | hexdump -ve '/1 "%02x\0\0"'
WINDOWS_LOADER_GUID_HEX = "\\$windows-loader-guid-as-hex\\$"
WINDOWS_EDITION_DISPLAY_NAME = "\\$windows-edition-display-name\\$"

# 0C3E6943-4D18-4B94-8AAE-57727725F82A -> 43693E0C184D944B8AAE57727725F82A -> 43,69,3E,0C,18,4D,94,4B,8A,AE,57,72,77,25,F8,2A
WINDOWS_PATH_PART_BYTES = "\\$windowspath-partbytes\\$"
BOOT_PATH_PART_BYTES = "\\$bootpath-partbytes\\$"
WINDOWS_DISK_BYTES = "\\$windows-diskbytes\\$"

LOCALE = "\\$locale\\$"


def patch_boot_reg(boot_reg_path: str, windows_partition_guid: str, boot_partition_guid: str, disk_guid: str,
                   locale: str = "en-US"):
    print("Patch boot.reg...")
    win_resume_guid = uuid.uuid4()
    win_loader_guid = uuid.uuid4()

    with open(boot_reg_path, "r+") as boot_reg:
        file_data = boot_reg.read()
        file_data = re.sub(WINDOWS_RESUME_GUID, str(win_resume_guid), file_data)
        file_data = re.sub(WINDOWS_LOADER_GUID, str(win_loader_guid), file_data)
        file_data = re.sub(LOCALE, locale, file_data)

        raped_win_guid = _rape_guid(windows_partition_guid)
        raped_boot_guid = _rape_guid(boot_partition_guid)
        raped_disk_guid = _rape_guid(disk_guid)
        file_data = re.sub(WINDOWS_PATH_PART_BYTES, str(raped_win_guid), file_data)
        file_data = re.sub(BOOT_PATH_PART_BYTES, str(raped_boot_guid), file_data)
        file_data = re.sub(WINDOWS_DISK_BYTES, raped_disk_guid, file_data)

        boot_reg.seek(0)
        boot_reg.write(file_data)
        boot_reg.truncate()
    print("Patched boot.reg")


def _rape_guid(guid: str) -> str:
    raped_guid = ""
    groups = guid.split("-")
    raped_guid += _reverse_group(groups[0])
    raped_guid += _reverse_group(groups[1])
    raped_guid += _reverse_group(groups[2])
    raped_guid += groups[3]
    raped_guid += groups[4]
    return raped_guid


def _reverse_group(group: str) -> str:
    print("Reverse " + group)
    reversed_group = ""
    i = len(group)

    while i > 0:
        reversed_group += group[i:2]
        i -= 2

    print("Reversd " + reversed_group)
    return reversed_group