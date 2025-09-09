#!/usr/bin/env python3
import sys

from os import environ

pkgdatadir = '@pkgdatadir@'
if environ.get("FLATPAK_ID") is not None:
    sys.path.insert(1, pkgdatadir)

from win2go.const import LOCALE_DIR, APP_ID
from win2go.ui.main_window import Win2Go

import gettext
gettext.install('win2go', LOCALE_DIR)


def run():
    print("Works!")
    Win2Go(application_id=APP_ID).run(sys.argv)


if __name__ == '__main__':
    run()
