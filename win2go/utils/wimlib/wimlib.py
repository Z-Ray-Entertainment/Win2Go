import asyncio
import subprocess

from win2go.utils.wimlib.wim_info import WIMInfo
from win2go.utils.wimlib.windows_edition import WindowsEdition


def create_windows(device_name, image_index, iso_file):
    pass


def get_wim_info(iso_mount_path: str) -> WIMInfo:
    return build_wiminfo(
        parse_image_definitions(
            iso_mount_path + "/sources/install.wim"
        )
    )


def parse_image_definitions(path: str) -> dict:
    full_image_info = {}

    wiminfo_result = subprocess.run(["wiminfo", path], stdout=subprocess.PIPE)
    all_lines = wiminfo_result.stdout.decode("utf-8").rstrip().split("\n")

    build_wiminfo = False
    build_images = False
    skip_line = False

    wiminfo = {}
    images = []

    current_image = {}

    for line in all_lines:
        if line.startswith("WIM Information"):
            build_wiminfo = True
            build_images = False
            skip_line = True
        if line.startswith("Available Images"):
            build_wiminfo = False
            build_images = True
            skip_line = True
        if not skip_line:
            if build_wiminfo:
                if not line.startswith("-") and not line == "":
                    line_split = line.split(":")
                    wiminfo[line_split[0].strip()] = line_split[1].strip()

            if line == "" and build_images:
                images.append(current_image)
                current_image = {}

            if build_images:
                if not line.startswith("-") and not line == "":
                    line_split = line.split(":")
                    current_image[line_split[0].strip()] = line_split[1].strip()
        skip_line = False

    full_image_info["wiminfo"] = wiminfo
    full_image_info["images"] = images

    return full_image_info


def build_wiminfo(wim_dict: dict) -> WIMInfo:
    images = []

    for image in wim_dict["images"]:
        index = int(image["Index"])
        name = image["Name"]
        description = image["Description"]
        display_name = image["Display Name"]
        display_description = image["Display Description"]
        directory_count = int(image["Directory Count"])
        file_count = int(image["File Count"])
        total_bytes = int(image["Total Bytes"])
        hard_link_bytes = int(image["Hard Link Bytes"])
        creation_time = image["Creation Time"]
        last_modification_time = image["Last Modification Time"]
        architecture = image["Architecture"]
        product_name = image["Product Name"]
        edition_id = image["Edition ID"]
        installation_type = image["Installation Type"]
        product_type = image["Product Type"]
        product_suite = image["Product Suite"]
        languages = image["Languages"]
        default_language = image["Default Language"]
        system_root = image["System Root"]
        major_version = int(image["Major Version"])
        minor_version = int(image["Minor Version"])
        build = int(image["Build"])
        service_pack_build = int(image["Service Pack Build"])
        service_pack_level = image["Service Pack Level"]
        flags = image["Flags"]
        wimboot_compatible = bool(image["WIMBoot compatible"])

        images.append(WindowsEdition(index, name, description, display_name, display_description, directory_count,
                                     file_count, total_bytes, hard_link_bytes, creation_time, last_modification_time,
                                     architecture, product_name, edition_id, installation_type, product_type,
                                     product_suite, languages, default_language, system_root, major_version,
                                     minor_version, build, service_pack_build, service_pack_level, flags,
                                     wimboot_compatible))

    wim_header = wim_dict["wiminfo"]
    path = wim_header["Path"]
    guid = wim_header["GUID"]
    version = wim_header["Version"]
    img_count = wim_header["Image Count"]
    compression = wim_header["Compression"]
    chunk_size = wim_header["Chunk Size"]
    part_split = wim_header["Part Number"].split("/")
    part_number = [int(part_split[0]), int(part_split[1])]
    boot_index = wim_header["Boot Index"]
    size_split = wim_header["Size"].split(" ")
    size = int(size_split[0])
    attributes = wim_header["Attributes"]
    return WIMInfo(path, guid, version, img_count, compression, chunk_size, part_number, size, boot_index, attributes, images)

async def apply_windows_edition(mount_path: str, wiminfo: WIMInfo, windows_edition: WindowsEdition):
    wim_image_path = wiminfo.path

    wimlib_cmd = "wimlib-imagex apply {image} {index} {mount} --no-acls --no-attributes --include-invalid-names".format(
        image=wim_image_path,
        index=windows_edition.index,
        mount=mount_path
    )

    process = await asyncio.create_subprocess_shell(wimlib_cmd,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()
    print("Apply boot image done. Exit code: {}".format(process.returncode))
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')