import os
import shutil
import subprocess

from win2go.const import SHARE_DIR


async def create_bootloader(boot_mount_path: str, windows_mount_path: str):
    print("Creating bootloader...")
    if boot_mount_path != "" and windows_mount_path != "":
        _copy_bootmgr(boot_mount_path, windows_mount_path)
        _build_bcd_store(boot_mount_path)
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


def _build_bcd_store(boot_mount_path: str):
    print("Setup BCD...")

    bcd_path = _copy_bcd(boot_mount_path)
    _patch_bcd(bcd_path, boot_mount_path)
    winload_path = _extract_winload(bcd_path, boot_mount_path)
    _create_windows_boot_entry(bcd_path, winload_path)

    print("Done building bcd store")

def _copy_bcd(boot_mount_path: str) -> str:
    print("Copying BCD...")

    bsc_src = "{share}/win2go/bcd/BCD".format(share=SHARE_DIR)
    bcd_dst = "{boot}/EFI/Microsoft/Boot/BCD".format(boot=boot_mount_path)
    shutil.copy(bsc_src, bcd_dst)

    print("BCD created at {}".format(bcd_dst))
    return bcd_dst

def _patch_bcd(bcd_path: str, boot_path: str):
    print("Patching BCD...")
    boot_reg_src = "{share}/win2go/bcd/boot.reg".format(share=SHARE_DIR)
    subprocess.run(["hivexregedit", "--merge", "--prefix", "BCD00000001", bcd_path, boot_reg_src])

def _extract_winload(bcd_path: str, boot_path: str) -> str:
    print("Extract winload info from BCD...")
    winload_dst = "{boot_path}/winload.txt".format(boot_path=boot_path)
    subprocess.run(["hivexsh", "-w", bcd_path, "-f", winload_dst])

    print("Winload extracted to {}".format(winload_dst))
    return winload_dst

def _create_windows_boot_entry(bcd_path: str, winload_path: str):
    print("Creating windows boot entry...")
