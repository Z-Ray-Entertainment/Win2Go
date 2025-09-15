import os
import shutil


async def create_bootloader(boot_mount_path: str, windows_mount_path: str):
    print("Creating bootloader...")
    if boot_mount_path != "" and windows_mount_path != "":
        _copy_bootmgr(boot_mount_path, windows_mount_path)
    else:
        print("No boot mount path or windows mount path")


def _copy_bootmgr(boot_mount_path: str, windows_mount_path: str):
    print("Copying bootmgr...")
    recovery_path = "{boot}/EFI/Microsoft/Recovery".format(boot=boot_mount_path)
    os.makedirs(recovery_path, exist_ok=True)

    efi_src = "{winmnt}/Windows/Boot/EFI".format(winmnt=windows_mount_path)
    boot_dst = "{bootmnt}/EFI/Microsoft/Boot".format(bootmnt=boot_mount_path)
    shutil.copytree(efi_src, boot_dst, dirs_exist_ok=True)

    font_src = "{winmnt}/Windows/Boot/Fonts".format(winmnt=windows_mount_path)
    shutil.copytree(font_src, boot_dst, dirs_exist_ok=True)

    res_src = "{winmnt}/Windows/Boot/Resources".format(winmnt=windows_mount_path)
    if os.path.exists(res_src):
        shutil.copytree(res_src, boot_dst, dirs_exist_ok=True)

    print("Done copying bootmgr")