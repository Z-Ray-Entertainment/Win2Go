from dasbus.connection import SystemMessageBus
sys_bus = SystemMessageBus()

def get_supported_filesystems():
    proxy = sys_bus.get_proxy("org.freedesktop.DBus.Properties", "/org/freedesktop/UDisks2/Manager")
    help(proxy)