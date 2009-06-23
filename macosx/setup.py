# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
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

Installation from source

Implements
==========

- setup

@author: Jeremy Pronk
@author: Frédéric Mantegazza
@copyright: (C) 2009 Jeremy Pronk
@copyright: (C) 2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: setup.py 1895 2009-06-06 21:02:22Z fma $"

from setuptools import setup

from papywizard.common import config

VERSION_PACKAGE = 1

setup(name="papywizard",
      version="%s-%d" % (config.VERSION, VERSION_PACKAGE),
      author="Frederic Mantegazza",
      author_email="frederic.mantegazza@gbiloba.org",
      maintainer="Frederic Mantegazza",
      maintainer_email="frederic.mantegazza@gbiloba.org",
      url="http://trac.gbiloba.org/papywizard",
      description="Merlin/Orion panohead control software",
      #long_description="",
      download_url="http://trac.gbiloba.org/papywizard/wiki/WikiStart#Download",
      app=['Papywizard.py'],
      #data_files=[("share/applications", ["debian/papywizard.desktop"]),
                  #('share/pixmaps', ["debian/papywizard.png"]),
                  #("share/icons/hicolor/48x48/apps", ["debian/papywizard.png"])
                  #],
      options={'py2app': {'argv_emulation': True,
                          #'iconfile': "macosx/papywizard.icns"
                          }
               },
      setup_requires=['py2app'],
),