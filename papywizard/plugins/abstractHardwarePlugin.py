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

Hardware plugin

Implements
==========

- AbstractHardwarePlugin

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.plugins.abstractPlugin import AbstractPlugin
from papywizard.driver.driverFactory import DriverFactory

DEFAULT_DRIVER_TYPE = 'bluetooth'


class AbstractHardwarePlugin(AbstractPlugin):
    """ Abtract class for plugins using low-level hardware.
    """
    def __getDriver(self):
        """ Return the associated driver.
        """
        return DriverFactory().get(self._config['DRIVER_TYPE'])

    _driver = property(__getDriver)

    def _init(self):
        self._hardware = None

    def _defineConfig(self):
        Logger().trace("AbstractHardwarePlugin._defineConfig()")
        self._addConfigKey('_driverType', 'DRIVER_TYPE', default=DEFAULT_DRIVER_TYPE)

    def establishConnection(self):
        """ Establish the connexion with the driver.

        We pass self, so the driver can keep track of connected hardwares.
        """
        Logger().trace("AbstractHardwarePlugin.establishConnection()")
        self._driver.establishConnection(self)
        AbstractPlugin.establishConnection(self)

    def stopConnection(self):
        """ stop the connexion with the driver.

        We pass self, so the driver can keep track of disconnected hardwares.
        """
        Logger().trace("AbstractHardwarePlugin.stopConnection()")
        try:
            self._driver.shutdownConnection(self)
        finally:
            AbstractPlugin.stopConnection(self)

    def init(self):
        Logger().trace("AbstractHardwarePlugin.init()")
        AbstractPlugin.init(self)
        self._hardware.setDriver(self._driver)
        self._hardware.setNbRetry(ConfigManager().getInt('Plugins/HARDWARE_COM_RETRY'))
        self._hardware.init()
