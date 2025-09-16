import subprocess


def merge_bcd_with_reg(bcd_path: str, reg_path: str):
    subprocess.run(["hivexregedit", "--merge", "--prefix", "BCD00000001", bcd_path, reg_path])