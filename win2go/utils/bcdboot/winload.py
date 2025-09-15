import subprocess
import uuid

def create_winload(bcd_path: str, boot_path: str):
    winload_path = _create_winload(boot_path)
    _update_winload(bcd_path, boot_path, winload_path)

def _generate_uuid() -> uuid.UUID:
    return uuid.uuid4()

def _create_winload(boot_path: str) -> str:
    winload_dst = "{boot_path}/winload.txt".format(boot_path=boot_path)
    return winload_dst

def _update_winload(bcd_path: str, boot_path: str, winload_dst: str) -> str:
    print("Extract winload info from BCD...")
    subprocess.run(["hivexsh", "-w", bcd_path, "-f", winload_dst])

    print("Winload extracted to {}".format(winload_dst))

def _write_hivexsh_program(winload_dst: str):
    pass