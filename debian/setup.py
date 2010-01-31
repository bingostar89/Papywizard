# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2009 Frédéric Mantegazza

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

Installation for maemo plateform

Implements
==========

- setup

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: setup.py 2157 2009-10-03 12:05:54Z fma $"

import os
import os.path
import sys
from distutils.core import setup

from bdist_debian import bdist_debian

path = os.path.dirname(__file__)
sys.path.append(os.path.join(path, os.pardir))
from papywizard.common import config

VERSION_PACKAGE = 1


setup(name="papywizard",
      version="%s-%d" % (config.VERSION, VERSION_PACKAGE),
      author="Frederic Mantegazza",
      author_email="frederic.mantegazza@gbiloba.org",
      maintainer="Frédéric Mantegazza",
      maintainer_email="frederic.mantegazza@gbiloba.org",
      url="http://www.papywizard.org",
      description="Merlin/Orion panohead control software",
      #long_description="",
      download_url="http://www.papywizard.org/wiki/Download",
      scripts=["papywizard.sh"],
      #package_dir={'papywizard': "papywizard"},
      packages=["papywizard", "papywizard.common", "papywizard.model",
                "papywizard.controller", "papywizard.hardware",
                "papywizard.view", "papywizard.scripts",
                "papywizard.plugins"],
      package_data={'papywizard': ["view/ui/*.ui", "common/papywizard.conf", "common/presets.xml"]},
      data_files=[("share/applications", ["debian/papywizard.desktop"]),
                  ('share/pixmaps', ["debian/icons/48x48/papywizard.png"]),
                  ('share/icons/hicolor/48x48', ["debian/icons/48x48/papywizard.png"]),
                  ('share/icons/hicolor/scalable/apps/', ["debian/icons/scalable/papywizard.png"])],

      # Debian package
      section="user/graphics",
      depends="python, python-qt4, python-serial, python-bluez",
      #icon="maemo/icons/26x26/papywizard.png",
      cmdclass={'bdist_debian': bdist_debian},
  )

