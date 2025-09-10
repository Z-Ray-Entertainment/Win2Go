import json
import subprocess


def lsblk() -> dict:
    result = subprocess.run(["lsblk", "--json", "-dpno", "NAME,SIZE,MODEL,HOTPLUG"], stdout=subprocess.PIPE)
    if result.returncode == 0:
        return json.loads(result.stdout.decode("utf-8").rstrip())
    else:
        return {}
