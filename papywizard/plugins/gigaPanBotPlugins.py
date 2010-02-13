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

Hardware

Implements
==========

 - GigaPanBotAxis
 - GigaPanBotAxisController
 - GigaPanBotShutter
 - GigaPanBotShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.hardware.gigaPanBotHardware import GigaPanBotHardware
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.abstractStandardShutterPlugin import AbstractStandardShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.standardShutterPluginController import StandardShutterPluginController

NAME = "GigaPanBot"

AXIS_ACCURACY = 0.1 # °
AXIS_TABLE = {'yawAxis': 1,
              'pitchAxis': 2,
              'shutter': 1
              }
MANUAL_SPEED_TABLE = {'slow': 0x0aa,
                      'normal': 0x022,
                      'fast': 0x011
                      }


class GigaPanBotAxis(AbstractHardwarePlugin, AbstractAxisPlugin):
    def __init__(self, *args, **kwargs):
        AbstractHardwarePlugin.__init__(self, *args, **kwargs)
        AbstractAxisPlugin.__init__(self, *args, **kwargs)

    def _init(self):
        Logger().trace("GigaPanBotAxis._init()")
        AbstractHardwarePlugin._init(self)
        AbstractAxisPlugin._init(self)
        self._hardware = GigaPanBotHardware()

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        AbstractAxisPlugin._defineConfig(self)

    def init(self):
        Logger().trace("GigaPanBotAxis.init()")
        #AbstractAxisPlugin.init(self)
        self._hardware.setAxis(AXIS_TABLE[self.capacity]),
        #self._hardware.setDriver(self._driver)
        #self._hardware.setNbRetry(ConfigManager().getInt('Plugins/HARDWARE_COM_RETRY'))
        #self._hardware.init()
        AbstractHardwarePlugin.init(self)

    def shutdown(self):
        Logger().trace("GigaPanBotAxis.shutdown()")
        self.stop()
        AbstractAxisPlugin.shutdown(self)

    def read(self):
        pos = self._hardware.read() - self._offset
        return pos

    def drive(self, pos, useOffset=True, wait=True):
        Logger().debug("GigaPanBotAxis.drive(): '%s' drive to %.1f" % (self.capacity, pos))
        currentPos = self.read()

        self._checkLimits(pos)

        if useOffset:
            pos += self._offset

        # Only move if needed
        if abs(pos - currentPos) > AXIS_ACCURACY:
            self._hardware.drive(pos)

            # Wait end of movement
            if wait:
                self.waitEndOfDrive()

    def waitEndOfDrive(self):
        while self.isMoving():
            time.sleep(config.SPY_REFRESH_DELAY / 1000.)
        self.waitStop()

    def startJog(self, dir_):
        self._hardware.startJog(dir_, MANUAL_SPEED_TABLE[self._manualSpeed])

    def stop(self):
        self.__driveFlag = False
        self._hardware.stop()
        self.waitStop()

    def waitStop(self):
        pass
        #pos = self.read()
        #time.sleep(config.SPY_REFRESH_DELAY / 1000.)
        #while True:
            #if abs(pos - self.read()) <= AXIS_ACCURACY:
                #break
            #pos = self.read()
            #time.sleep(config.SPY_REFRESH_DELAY / 1000.)

    def isMoving(self):
        status = self._hardware.getStatus()
        if status != '0':
            return True
        else:
            return False


class GigaPanBotAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


class GigaPanBotShutter(AbstractHardwarePlugin, AbstractStandardShutterPlugin):
    def __init__(self, *args, **kwargs):
        """
        """
        AbstractHardwarePlugin.__init__(self, *args, **kwargs)
        AbstractStandardShutterPlugin.__init__(self, *args, **kwargs)

    def _init(self):
        Logger().trace("GigaPanBotShutter._init()")
        AbstractHardwarePlugin._init(self)
        AbstractStandardShutterPlugin._init(self)
        self._hardware = GigaPanBotHardware()  # Move to parent class?

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._hardware.setOutput(True)

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._hardware.setOutput(False)

    def init(self):
        Logger().trace("GigaPanBotShutter.init()")
        #AbstractAxisPlugin.init(self)
        self._hardware.setAxis(AXIS_TABLE[self.capacity]),
        #self._hardware.setDriver(self._driver)
        #self._hardware.setNbRetry(ConfigManager().getInt('Plugins/HARDWARE_COM_RETRY'))
        #self._hardware.init()
        AbstractHardwarePlugin.init(self)

    def shutdown(self):
        Logger().trace("GigaPanBotShutter.shutdown()")
        self._triggerOffShutter()
        AbstractHardwarePlugin.shutdown(self)
        AbstractStandardShutterPlugin.shutdown(self)


class GigaPanBotShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


def register():
    """ Register plugins.
    """
    PluginsManager().register(GigaPanBotAxis, GigaPanBotAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(GigaPanBotAxis, GigaPanBotAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(GigaPanBotShutter, GigaPanBotShutterController, capacity='shutter', name=NAME)
