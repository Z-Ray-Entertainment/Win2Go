import re
import uuid

WINDOWS_RESUME_GUID = "\\$windows-resume-guid\\$"
WINDOWS_LOADER_GUID = "\\$windows-loader-guid\\$"
# '<loaderguid-here>\0\0' | hexdump -ve '/1 "%02x\0\0"'
WINDOWS_LOADER_GUID_HEX = "\\$windows-loader-guid-as-hex\\$"
WINDOWS_EDITION_DISPLAY_NAME = "\\$windows-edition-display-name\\$"
SOURCE_PATH_PART_BYTES = "\\$sourcepath-partbytes\\$"
SOURCE_PATH_DISK_BYTES = "\\$sourcepath-diskbytes\\$"
DESTINATION_PATH_PART_BYTES = "\\$destinationpath-partbytes\\$"
DESTINATION_PATH_DISK_BYTES = "\\$destinationpath-diskbytes\\$"
SYSTEM_PATH_PART_BYTES = "\\$sysempath-partbytes\\$"
SYSTEM_PATH_DISK_BYTES = "\\$sysempath-diskbytes\\$"
LOCALE = "\\$locale\\$"


def patch_boot_reg(boot_reg_path: str, windows_mount: str, boot_mount: str, locale: str = "en-US"):
    print("Patch boot.reg...")
    win_resume_guid = uuid.uuid4()
    win_loader_guid = uuid.uuid4()

    with open(boot_reg_path, "r+") as boot_reg:
        file_data = boot_reg.read()
        file_data = re.sub(WINDOWS_RESUME_GUID, str(win_resume_guid), file_data)
        file_data = re.sub(WINDOWS_LOADER_GUID, str(win_loader_guid), file_data)
        file_data = re.sub(LOCALE, locale, file_data)

        boot_reg.seek(0)
        boot_reg.write(file_data)
        boot_reg.truncate()
    print("Patched boot.reg")