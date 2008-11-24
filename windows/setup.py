# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Frédéric Mantegazza

This software is governed by the B{CeCILL} license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
U{http://www.cecill.info}.

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

Module purpose
==============

Installation script for Windows plateform.
Run this script as:

>>> python setup.py py2exe

Implements
==========

- Target
- setup

@author: Mario Beauchamp
@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL

@todo: l10n and i18n
"""

__revision__ = "$Id: setup.py 471 2008-09-05 07:47:31Z fma $"

import sys
import os
import os.path
from distutils.core import setup

import py2exe

sys.path.append("C:\\Documents and Settings\\fma\\Mes documents\\develop\\papywizard\\trunk")
from papywizard.common import config


dlls = ["iconv.dll", "intl.dll", "libatk-1.0-0.dll", "libgdk-win32-2.0-0.dll",
        "libgdk_pixbuf-2.0-0.dll", "libglib-2.0-0.dll", "libgmodule-2.0-0.dll",
        "libgobject-2.0-0.dll", "libgthread-2.0-0.dll", "libgtk-win32-2.0-0.dll",
        "libpangocairo-1.0-0.dll", "libcairo-2.dll", "libpango-1.0-0.dll",
        "libpangowin32-1.0-0.dll"]


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = config.VERSION
        self.company_name = ""
        self.copyright = "(C) 2007-2008 Frédéric Mantegazza"
        self.name = ""


setup(options={"py2exe": {'compressed': 1,
                          'optimize': 2,
                          'includes': ["atk", "cairo", "pango", "pangocairo", "gobject", "gtk.keysyms"],
                          'excludes': [],
                          'dll_excludes': dlls,
                          'dist_dir': "./dist",
                          'bundle_files': 1}},
      windows=[Target(description="Merlin/Orion panohead control software",
                      script="../papywizard/scripts/main.py",
                      icon_resources=[(1, "papywizard.ico")],
                      dest_base="Papywizard"),
               Target(description="Papywizard 3D view",
                      script="../papywizard/scripts/main3D.py",
                      icon_resources=[(1, "papywizard.ico")],
                      dest_base="Papywizard-3D")],
      console=[Target(description="Papywizard harware simulator",
                      script="../papywizard/scripts/mainSimul.py",
                      icon_resources=[(1, "papywizard.ico")],
                      dest_base="Papywizard-Simul")],
      data_files=[("papywizard/common", ["../papywizard/common/papywizard.conf",
                                         "../papywizard/common/presets.xml"]),
                  ("papywizard/view", ["../papywizard/view/papywizard.png",
                                       "../papywizard/view/bluetoothChooserDialog.glade",
                                       "../papywizard/view/configDialog.glade",
                                       "../papywizard/view/helpAboutDialog.glade",
                                       "../papywizard/view/loggerDialog.glade",
                                       "../papywizard/view/mainWindow.glade",
                                       "../papywizard/view/nbPictsDialog.glade",
                                       "../papywizard/view/presetInfoDialog.glade",
                                       "../papywizard/view/shootDialog.glade",
                                       "../papywizard/view/totalFovDialog.glade",
                                       "../papywizard/view/waitBanner.glade",
                                       ]),
                  ("share/locale/en/LC_MESSAGES", ["../locale/en/LC_MESSAGES/papywizard.mo"]),
                  ("share/locale/fr/LC_MESSAGES", ["../locale/fr/LC_MESSAGES/papywizard.mo"]),
                  ("share/locale/pl/LC_MESSAGES", ["../locale/pl/LC_MESSAGES/papywizard.mo"]),
                  ("share/locale/de/LC_MESSAGES", ["../locale/de/LC_MESSAGES/papywizard.mo"])]
     )

