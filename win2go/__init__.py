#!/usr/bin/env python3
import sys

from os import environ

pkgdatadir = '@pkgdatadir@'
if environ.get("FLATPAK_ID") is not None:
    sys.path.insert(1, pkgdatadir)

from win2go.const import LOCALE_DIR

import gettext

gettext.install('win2go', LOCALE_DIR)


def run():
    print("Works!")


if __name__ == '__main__':
    run()
