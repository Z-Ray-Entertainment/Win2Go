import os


async def create_bootloader(boot_mount_path: str, windows_install_path: str):
    print("Creating bootloader...")
    #_copy_bootmgr(boot_mount_path, windows_install_path)

def _copy_bootmgr(boot_mount_path: str, windows_install_path: str):
    recovery_path = "{boot}/EFI/Microsoft/Recovery".format(boot=boot_mount_path)
    os.makedirs(recovery_path)