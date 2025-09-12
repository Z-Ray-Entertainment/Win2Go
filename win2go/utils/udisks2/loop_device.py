from win2go.utils.udisks2.udisks2_dasbus import filesystem_mount


class LoopDevice:
    obj_path: str
    mount_path: str

    def __init__(self, obj_path: str, mount_path: str = ""):
        self.obj_path = obj_path
        self.mount_path = mount_path

    def mount(self):
        self.mount_path = filesystem_mount(self.obj_path)
        print(self.mount_path)