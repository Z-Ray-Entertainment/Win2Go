from os import environ

if environ.get("FLATPAK_ID") is not None:
    VERSION = "@VERSION@"
    LOCALE_DIR = "@localedir@"
else:
    VERSION = "0.dev0"
    LOCALE_DIR = "data/po"
APP_NAME = "Win2Go"
APP_ID = "@APPID@"
