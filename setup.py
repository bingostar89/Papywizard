#import bdist_debian
from distutils.core import setup

setup(name="papywizard",
      version="0.9 beta 2",
      author="Frederic Mantegazza",
      author_email="Frederic Mantegazza <frederic.mantegazza@gbiloba.org>",
      maintainer="Frederic Mantegazza",
      maintainer_email="Frederic Mantegazza <frederic.mantegazza@gbiloba.org>",
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

      # pymaemo stuff
      #section="user/backup",
      #depends="python2.5, python2.5-hildon, python2.5-gtk2",
      #icon="papywizard.png",
      #cmdclass={'bdist_debian': bdist_debian.bdist_debian},
  )

