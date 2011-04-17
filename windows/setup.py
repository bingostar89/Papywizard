# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL

@todo: l10n and i18n
"""

__revision__ = "$Id$"

import sys
import os
import os.path
from distutils.core import setup

import py2exe

from papywizard.common import config


includes = ["sip", "elementtree"]
excludes = []
dlls_excludes = []

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = "%s" % config.VERSION
        self.company_name = ""
        self.copyright = "(C) 2007-2011 Frédéric Mantegazza"
        self.name = ""


setup(options={"py2exe": {'compressed': 1,
                          'optimize': 2,
                          'includes': includes,
                          'excludes': excludes,
                          'dll_excludes': dlls_excludes,
                          'dist_dir': "./dist",
                          'bundle_files': 1}},
      #zipfile = None,
      windows=[Target(description="Merlin/Orion panohead control software",
                      script="../papywizard/scripts/main.py",
                      icon_resources=[(1, "papywizard.ico")],
                      dest_base="Papywizard")],
      data_files=[("papywizard/common", ["../papywizard/common/papywizard.conf",
                                         "../papywizard/common/presets.xml"]),
                  ("papywizard/view/ui", ["../papywizard/view/ui/bluetoothChooserDialog.ui",
                                          "../papywizard/view/ui/configDialog.ui",
                                          "../papywizard/view/ui/helpAboutDialog.ui",
                                          "../papywizard/view/ui/loggerDialog.ui",
                                          "../papywizard/view/ui/mainWindow.ui",
                                          "../papywizard/view/ui/nbPictsDialog.ui",
                                          "../papywizard/view/ui/pluginsConfigDialog.ui",
                                          "../papywizard/view/ui/pluginsDialog.ui",
                                          "../papywizard/view/ui/pluginsStatusDialog.ui",
                                          "../papywizard/view/ui/shootDialog.ui",
                                          "../papywizard/view/ui/totalFovDialog.ui"
                                          ])]
     )
