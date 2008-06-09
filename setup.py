# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Installation.

@author: Frédéric Mantegazza
@copyright: 2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

from bdist_debian import bdist_debian
from distutils.core import setup

from common import config


setup(name="papywizard",
      version="%s-%d" % (config.VERSION, config.PACKAGE_VERSION),
      author="Frederic Mantegazza",
      author_email="frederic.mantegazza@gbiloba.org",
      maintainer="Frederic Mantegazza",
      maintainer_email="frederic.mantegazza@gbiloba.org",
      url="http://trac.gbiloba.org/papywizard",
      description="Merlin/Orion panohead control software",
      #long_description="",
      download_url="http://trac.gbiloba.org/papywizard/wiki/WikiStart#Download",
      scripts=["papywizard"],
      package_dir={'papywizard': "."},
      packages=["papywizard", "papywizard.common", "papywizard.model",
                "papywizard.controller", "papywizard.hardware",
                "papywizard.view", "papywizard.view3D"],
      package_data={'papywizard': ["view/*.glade"]},
      data_files=[("share/applications/hildon", ["papywizard.desktop"]),
                  ('share/pixmaps', ["papywizard.png"]),
                  ('etc', ["papywizard.conf"])],

      # pymaemo stuff
      section="user/graphics",
      depends="python2.5, python2.5-hildon, python2.5-gtk2",
      icon="papywizard.png",
      cmdclass={'bdist_debian': bdist_debian},
  )

