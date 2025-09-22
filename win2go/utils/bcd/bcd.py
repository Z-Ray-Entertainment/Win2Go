import os
import shutil

from win2go.const import SHARE_DIR
from win2go.utils.bcd import hivex, registry_patcher


async def create_bootloader(boot_mount_path: str, windows_mount_path: str, disk_guid: str, boot_guid: str,
                            win_guid: str):
    print("Creating bootloader...")
    if boot_mount_path != "" and windows_mount_path != "":
        _copy_bootmgr(boot_mount_path, windows_mount_path)
        _build_bcd_store(boot_mount_path, disk_guid, boot_guid, win_guid)
    else:
        print("No boot mount path or windows mount path")


def _copy_bootmgr(boot_mount_path: str, windows_mount_path: str):
    print("Copying bootmgr...")

    recovery_dst = "{bootmnt}/EFI/Microsoft/Recovery".format(bootmnt=boot_mount_path)
    os.makedirs(recovery_dst, exist_ok=True)

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

    boot_reg_src = "{share}/win2go/bcd/boot.reg".format(share=SHARE_DIR)
    boot_reg_dst = "{boot}/boot.reg".format(boot=boot_mount_path)
    shutil.copy(boot_reg_src, boot_reg_dst)
    registry_patcher.patch_boot_reg(boot_reg_dst, win_guid, boot_guid, disk_guid)

    boot_bcd_path = _copy_boot_bcd(boot_mount_path)
    hivex.merge_bcd_with_reg(boot_bcd_path, boot_reg_dst)

    recovery_reg_src = "{share}/win2go/bcd/recovery.reg".format(share=SHARE_DIR)
    recovery_reg_dst = "{boot}/recovery.reg".format(boot=boot_mount_path)
    shutil.copy(recovery_reg_src, recovery_reg_dst)
    registry_patcher.patch_recovery_registry(recovery_reg_dst, disk_guid, boot_guid)

    recovery_bcd_path = _copy_recovery_bcd(boot_mount_path)
    hivex.merge_bcd_with_reg(recovery_bcd_path, recovery_reg_dst)

    print("Done building bcd store")


def _copy_boot_bcd(boot_mount_path: str) -> str:
    print("Copying Boot BCD...")

    bsc_src = "{share}/win2go/bcd/BCD-PLAIN".format(share=SHARE_DIR)
    bcd_dst = "{boot}/EFI/Microsoft/Boot/BCD".format(boot=boot_mount_path)
    shutil.copy(bsc_src, bcd_dst)

    print("BCD created at {}".format(bcd_dst))
    return bcd_dst


def _copy_recovery_bcd(boot_mount_path: str) -> str:
    print("Copying Recovery BCD...")

    bsc_src = "{share}/win2go/bcd/BCD-PLAIN".format(share=SHARE_DIR)
    bcd_dst = "{boot}/EFI/Microsoft/Recovery/BCD".format(boot=boot_mount_path)
    shutil.copy(bsc_src, bcd_dst)

    print("BCD created at {}".format(bcd_dst))
    return bcd_dst
