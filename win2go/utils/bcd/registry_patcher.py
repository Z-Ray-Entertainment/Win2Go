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

COMMENTS = re.compile("#[a-zA-Z ]*#")

def patch_boot_reg(boot_reg_path: str, windows_partition_guid: str, boot_partition_guid: str, disk_guid: str,
                   locale: str = "en-US", windows_edition: str = "Windows"):
    win_resume_guid = uuid.uuid4()
    win_loader_guid = uuid.uuid4()

    with open(boot_reg_path, "r+") as boot_reg:
        file_data = boot_reg.read()
        file_data = re.sub(WINDOWS_RESUME_GUID, str(win_resume_guid), file_data)
        file_data = re.sub(WINDOWS_LOADER_GUID, str(win_loader_guid), file_data)
        file_data = re.sub(LOCALE, locale, file_data)

        windows_partiton_uuid: uuid.UUID = uuid.UUID(windows_partition_guid)
        boot_partiton_uuid: uuid.UUID = uuid.UUID(boot_partition_guid)

        # b = guid.encode("utf-8") + b"\x00\x00"

        dotnet_win_guid = _dotnet_guid(windows_partition_guid)
        print("Raped WIN GUID: {}".format(dotnet_win_guid))
        print("UUID WIN GUID: {}".format(windows_partiton_uuid.bytes))

        dotnet_boot_guid = _dotnet_guid(boot_partition_guid)
        dotnet_disk_guid = _dotnet_guid(disk_guid)
        file_data = re.sub(WINDOWS_PATH_PART_BYTES, str(dotnet_win_guid), file_data)
        file_data = re.sub(BOOT_PATH_PART_BYTES, str(dotnet_boot_guid), file_data)
        file_data = re.sub(WINDOWS_DISK_BYTES, dotnet_disk_guid, file_data)

        file_data = re.sub(WINDOWS_EDITION_DISPLAY_NAME, windows_edition, file_data)

        file_data = re.sub(WINDOWS_LOADER_GUID_HEX, _hexdump(str(win_loader_guid)), file_data)

        file_data = re.sub(COMMENTS, "", file_data)

        boot_reg.seek(0)
        boot_reg.write(file_data)
        boot_reg.truncate()

def patch_recovery_registry(recovery_reg_path: str, disk_guid: str, boot_partition_guid: str, locale: str = "en-US"):
    with open(recovery_reg_path, "r+") as recovery_reg:
        file_data = recovery_reg.read()
        file_data = re.sub(LOCALE, locale, file_data)

        dotnet_boot_guid = _dotnet_guid(boot_partition_guid)
        dotnet_disk_guid = _dotnet_guid(disk_guid)

        file_data = re.sub(BOOT_PATH_PART_BYTES, str(dotnet_boot_guid), file_data)
        file_data = re.sub(WINDOWS_DISK_BYTES, dotnet_disk_guid, file_data)

        recovery_reg.seek(0)
        recovery_reg.write(file_data)
        recovery_reg.truncate()

# Int32, Int16, Int16, Bytes[] see: https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-9.0&redirectedfrom=MSDN#system-guid-ctor(system-int32-system-int16-system-int16-system-byte())
def _dotnet_guid(guid: str) -> str:
    dotnet_guid = ""
    groups = guid.split("-")
    dotnet_guid += _reverse_group(groups[0])
    dotnet_guid += _reverse_group(groups[1])
    dotnet_guid += _reverse_group(groups[2])
    dotnet_guid += groups[3]
    dotnet_guid += groups[4]

    dotnet_guid = _separate_pairs_by_delimiter(dotnet_guid)

    return dotnet_guid


def _reverse_group(group: str) -> str:
    reversed_group = ""
    i = len(group)

    while i > 0:
        i = i - 2
        reversed_group += group[i:i+2]

    return reversed_group

def _separate_pairs_by_delimiter(guid: str):
    split_guid: str = ""
    for i in range(0, len(guid), 2):
        split_guid += guid[i:i+2] + ","
        i = i + 3
    return split_guid[0:len(split_guid)-1]

def _hexdump(guid: str):
    b = guid.encode("utf-8") + b"\x00\x00"
    out_bytes = "".join(f"{byte:02x}00" for byte in b)
    return out_bytes