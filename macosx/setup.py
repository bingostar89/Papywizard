# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2010 Frédéric Mantegazza

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

@author: Mickaël Cornet
@author: Jeremy Pronk
@author: Frédéric Mantegazza
@copyright: (C) 2011 Mickaël Cornet
@copyright: (C) 2009 Jeremy Pronk
@copyright: (C) 2009-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

#import sys
#import pprint

from setuptools import setup

from papywizard.common import config

VERSION_PACKAGE = 1

#sys.path += ['/Library/Python/2.6/site-packages',
#             '/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/PyObjC',
#             ]
#
#pprint.pprint(sys.path)

setup(name="papywizard",
      version="%s-%d" % (config.VERSION, VERSION_PACKAGE),
      author="Frederic Mantegazza",
      author_email="frederic.mantegazza@gbiloba.org",
      maintainer="Mickael Cornet",
      maintainer_email="mickael.cornet@kolor.com",
      url="http://trac.gbiloba.org/papywizard",
      description="Merlin/Orion panohead control software",
      #long_description="",
      download_url="http://trac.gbiloba.org/papywizard/wiki/Download",
      app=['Papywizard.py'],
      options={'py2app': {'argv_emulation': False,
                          'includes': ["sip", "PyQt4.QtCore", "PyQt4.QtGui", "lightblue", "LightAquaBlue",
                                       "PyQt4.QtNetwork", "PyQt4.QtXml", "PyQt4.QtSvg"],
                          'excludes': ["PyQt4.QtDesigner", "PyQt4.QtOpenGL", "PyQt4.QtScript", "PyQt4.QtSql",
                                       "PyQt4.QtTest", "PyQt4.QtWebKit", "PyQt4.phonon"],
                          'frameworks': ["LightAquaBlue.framework"],
                          #'site_packages': True,
                          #'packages': ["Foundation", "LightAquaBlue"],
                          'iconfile': "macosx/papywizard.icns"
               },
      setup_requires=['py2app'],
      data_files=[("papywizard/common", ["./papywizard/common/papywizard.conf",
                                         "./papywizard/common/presets.xml"]),
                  ("papywizard/view/ui", ["./papywizard/view/ui/bluetoothChooserDialog.ui",
                                          "./papywizard/view/ui/configDialog.ui",
                                          "./papywizard/view/ui/helpAboutDialog.ui",
                                          "./papywizard/view/ui/loggerDialog.ui",
                                          "./papywizard/view/ui/mainWindow.ui",
                                          "./papywizard/view/ui/nbPictsDialog.ui",
                                          "./papywizard/view/ui/pluginsConfigDialog.ui",
                                          "./papywizard/view/ui/pluginsDialog.ui",
                                          "./papywizard/view/ui/pluginsStatusDialog.ui",
                                          "./papywizard/view/ui/shootDialog.ui",
                                          "./papywizard/view/ui/totalFovDialog.ui"
                                          ])]
),
