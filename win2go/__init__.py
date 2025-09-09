#!/usr/bin/env python3
import os
import sys

from os import environ

from gi.repository import Gio

pkgdatadir = '@pkgdatadir@'
if environ.get("FLATPAK_ID") is not None:
    sys.path.insert(1, pkgdatadir)

resource = Gio.Resource.load(filename=os.path.join(pkgdatadir, "win2go.gresource"))
Gio.resources_register(resource)

from win2go.const import LOCALE_DIR, APP_ID
from win2go.win2go_app import Win2Go

import gettext
gettext.install('win2go', LOCALE_DIR)

if __name__ == '__main__':
    sys.exit(Win2Go(application_id=APP_ID).run(sys.argv))
