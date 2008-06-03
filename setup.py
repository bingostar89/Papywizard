import bdist_debian
from distutils.core import setup

setup(name='papywizard',
      scripts=['papywizard'],
      version='0.9 beta 2',
      section='user/backup',
      maintainer='Frederic Mantegazza',
      maintainer_email='Frederic Mantegazza <frederic.mantegazza@gbiloba.org>',
      depends='python2.5, python2.5-hildon, python2.5-gtk2',
      description="Merlin/Orion panohead control software",
      package_dir={'papywizard': ''},
      packages=['papywizard', 'papywizard.common', 'papywizard.controller', 'papywizard.controller_gtk',
                'papywizard.hardware', 'papywizard.model', 'papywizard.view', 'papywizard.view3D',
                'papywizard.view_gtk'],
      package_data={'papywizard': ['view_gtk/*.glade']},
      #icon='papywizard.png',
      cmdclass={'bdist_debian': bdist_debian.bdist_debian}
  )

