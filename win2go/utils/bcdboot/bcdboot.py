import os
import shutil

from win2go.const import SHARE_DIR
from win2go.utils.bcdboot import hivex, boot_reg

async def create_bootloader(boot_mount_path: str, windows_mount_path: str, disk_guid: str, boot_guid: str, win_guid: str):
    print("Creating bootloader...")
    if boot_mount_path != "" and windows_mount_path != "":
        _copy_bootmgr(boot_mount_path, windows_mount_path)
        _build_bcd_store(boot_mount_path, disk_guid, boot_guid, win_guid)
    else:
        print("No boot mount path or windows mount path")


def _copy_bootmgr(boot_mount_path: str, windows_mount_path: str):
    print("Copying bootmgr...")

    efi_src = "{winmnt}/Windows/Boot/EFI".format(winmnt=windows_mount_path)
    boot_dst = "{bootmnt}/EFI/Microsoft/Boot".format(bootmnt=boot_mount_path)
    shutil.copytree(efi_src, boot_dst, dirs_exist_ok=True)

    font_src = "{winmnt}/Windows/Boot/Fonts".format(winmnt=windows_mount_path)
    shutil.copytree(font_src, boot_dst, dirs_exist_ok=True)

    res_src = "{winmnt}/Windows/Boot/Resources".format(winmnt=windows_mount_path)
    if os.path.exists(res_src):
        shutil.copytree(res_src, boot_dst, dirs_exist_ok=True)

    print("Done copying bootmgr")


def _build_bcd_store(boot_mount_path: str, disk_guid: str, boot_guid: str, win_guid: str):
    print("Setup BCD...")

    bcd_path = _copy_bcd(boot_mount_path)

    boot_reg_src = "{share}/win2go/bcd/boot.reg".format(share=SHARE_DIR)
    boot_reg_dst = "{boot}/boot.reg".format(boot=boot_mount_path)
    shutil.copy(boot_reg_src, boot_reg_dst)
    boot_reg.patch_boot_reg(boot_reg_dst, win_guid, boot_guid, disk_guid)
    hivex.merge_bcd_with_reg(bcd_path, boot_reg_dst)

    print("Done building bcd store")

def _copy_bcd(boot_mount_path: str) -> str:
    print("Copying BCD...")

    bsc_src = "{share}/win2go/bcd/BCD".format(share=SHARE_DIR)
    bcd_dst = "{boot}/EFI/Microsoft/Boot/BCD".format(boot=boot_mount_path)
    shutil.copy(bsc_src, bcd_dst)

    print("BCD created at {}".format(bcd_dst))
    return bcd_dst
