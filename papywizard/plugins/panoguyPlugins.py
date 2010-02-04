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

Hardware

Implements
==========

- PanoguyLowLevelHardware
- PanoguyAxis
- PanoguyAxisController
- PanoguyShutter
- PanoguyShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import sys
import threading

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.abstractStandardShutterPlugin import AbstractStandardShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.standardShutterPluginController import StandardShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

NAME = "Panoguy"

ENCODER_ZERO = 0x800000
AXIS_ACCURACY = 0.1 # °
AXIS_TABLE = {'yawAxis': 1,
              'pitchAxis': 2,
              'shutter': 1
              }
MANUAL_SPEED_TABLE = {'slow': 170,  # "AA0000"  / 5
                      'normal': 34, # "220000" nominal
                      'fast': 17   # "110000"  * 2
                      }


class PanoguyLowLevelHardware(QtCore.QObject):  # Inherits abstract???
    """ Low-level access to Panoguy controller.
    """
    def __init__(self,):
        """ Init PanoguyLowLevelHardware Object.
        """
        QtCore.QObject.__init__(self)

        self.__capacity = None
        self.__driver = None
        self.__encoderFullCircle = None

    def setCapacity(self, capacity):
        """
        """
        self.__capacity = capacity

    def setDriver(self, driver):
        """
        """
        self.__driver = driver

    def __decodeAxisValue(self, strValue):
        """ Decode value from axis.

        Values (position, speed...) returned by axis are
        24bits-encoded strings, high byte first.

        @param strValue: value returned by axis
        @type strValue: str

        @return: value
        @rtype: int
        """
        value = eval("0x%s" % strValue)

        return value

    def __encodeAxisValue(self, value):
        """ Encode value for axis.

        Values (position, speed...) to send to axis must be
        24bits-encoded strings, high byte first.

        @param value: value
        @type value: int

        @return: value to send to axis
        @rtype: str
        """
        strHexValue = "000000%s" % hex(value)[2:]
        strValue = strHexValue[-6:]

        return strValue.upper()

    def __encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        return (codPos - ENCODER_ZERO) * 360. / self.__encoderFullCircle

    def __angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: int
        """
        return int(pos * self.__encoderFullCircle / 360. + ENCODER_ZERO)

    def __sendCmd(self, cmd, param=""):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @return: answer
        @rtype: str
        """
        cmd = "%s%d%s" % (cmd, AXIS_TABLE[self.__capacity], param)
        for nbTry in xrange(ConfigManager().getInt('Plugins/HARDWARE_COM_RETRY')):
            try:
                self.__driver.empty()
                self.__driver.write(":%s\r" % cmd)
                answer = ""
                while True:
                    c = self.__driver.read(1)
                    #Logger().debug("PanoguyLowLevelHardware.__sendCmd(): c=%s" % c)
                    if c == '=':
                        continue
                    if c == '!':
                        c = self.__driver.read(1) # Get error code
                        raise IOError("Unknown command '%s' (err=%s)" % (cmd, c))
                    elif c == '\r':
                        break
                    else:
                        answer += c

            except IOError:
                Logger().exception("PanoguyLowLevelHardware.__sendCmd")
                Logger().warning("PanoguyLowLevelHardware.__sendCmd(): %s axis %d can't sent command '%s'. Retrying..." % (NAME, AXIS_TABLE[self.__capacity], cmd))
            else:
                break
        else:
            raise HardwareError("%s axis %d can't send command '%s'" % (NAME, AXIS_TABLE[self.__capacity], cmd))
        #Logger().debug("PanoguyLowLevelHardware._sendCmd(): axis %d cmd=%s, ans=%s" % (AXIS_TABLE[self.__capacity], cmd, answer))

        return answer

    def initHardware(self):
        """ Init the Panoguy hardware.

        Done only once per axis.
        """
        self.__driver.acquireBus()
        try:

            # Stop motor
            self.__sendCmd("L")

            # Check motor?
            self.__sendCmd("F")

            # Get encoder full circle
            value = self.__sendCmd("a")
            self.__encoderFullCircle = self.__decodeAxisValue(value)
            Logger().debug("PanoguyLowLevelHardware.init(): full circle count=%s" % hex(self.__encoderFullCircle))

            # Get firmeware version
            value = self.__sendCmd("e")
            Logger().debug("PanoguyLowLevelHardware.init(): firmeware version=%s" % value)

        finally:
            self.__driver.releaseBus()

    def read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self.__driver.acquireBus()
        try:
            value = self.__sendCmd("j")
        finally:
            self.__driver.releaseBus()
        pos = self.__encoderToAngle(self.__decodeAxisValue(value))
        return pos

    def drive(self, pos):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float
        """
        strValue = self.__encodeAxisValue(self.__angleToEncoder(pos))
        self.__driver.acquireBus()
        try:
            self.__sendCmd("L")
            self.__sendCmd("S", strValue)
        finally:
            self.__driver.releaseBus()

    def stop(self):
        """ Stop the axis.
        """
        self.__driver.acquireBus()
        try:
            self.__sendCmd("L")
        finally:
            self.__driver.releaseBus()

    def startJog(self, dir_, speed):
        """ Start the axis.

        @param dir_: direction ('+', '-')
        @type dir_: str

        @param speed: speed
        @type speed: int
        """
        self.__driver.acquireBus()
        try:
            self.__sendCmd("L")
            if dir_ == '+':
                self.__sendCmd("G", "0")
            elif dir_ == '-':
                self.__sendCmd("G", "1")
            else:
                raise ValueError("%s axis %d dir. must be in ('+', '-')" % (NAME, AXIS_TABLE[self.__capacity]))
        finally:
            self.__driver.releaseBus()

    def getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self.__driver.acquireBus()
        try:
            return self.__sendCmd("f")
        finally:
            self.__driver.releaseBus()

    def setOutput(self, state):
        """ Set output state.

        @param state: new state of the the output
        @type state: bool
        """
        self.__driver.acquireBus()
        try:
            self.__sendCmd("O", str(int(state)))
        finally:
            self.__driver.releaseBus()


class PanoguyAxis(AbstractHardwarePlugin, AbstractAxisPlugin):
    def __init__(self, *args, **kwargs):
        AbstractHardwarePlugin.__init__(self, *args, **kwargs)
        AbstractAxisPlugin.__init__(self, *args, **kwargs)

    def _init(self):
        Logger().trace("PanoguyAxis._init()")
        AbstractHardwarePlugin._init(self)
        AbstractAxisPlugin._init(self)
        self.__lowLevelHardware = PanoguyLowLevelHardware()  # Move to parent class?

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        AbstractAxisPlugin._defineConfig(self)

    def init(self):
        Logger().trace("PanoguyAxis.init()")
        AbstractAxisPlugin.init(self)
        self.__lowLevelHardware.setCapacity(self.capacity),
        self.__lowLevelHardware.setDriver(self._driver)
        self.__lowLevelHardware.initHardware()

    def shutdown(self):
        Logger().trace("PanoguyAxis.shutdown()")
        self.stop()
        AbstractAxisPlugin.shutdown(self)

    def read(self):
        pos = self.__lowLevelHardware.read() - self._offset
        return pos

    def drive(self, pos, useOffset=True, wait=True):
        Logger().debug("PanoguyAxis.drive(): '%s' drive to %.1f" % (self.capacity, pos))
        currentPos = self.read()

        self._checkLimits(pos)

        if useOffset:
            pos += self._offset

        # Only move if needed
        if abs(pos - currentPos) > AXIS_ACCURACY:
            self.__lowLevelHardware.drive(pos)

            # Wait end of movement
            if wait:
                self.waitEndOfDrive()

    def waitEndOfDrive(self):
        while self.isMoving():
            time.sleep(config.SPY_REFRESH_DELAY / 1000.)
        self.waitStop()

    def startJog(self, dir_):
        self.__lowLevelHardware.startJog(dir_, MANUAL_SPEED_TABLE[self._manualSpeed])

    def stop(self):
        self.__driveFlag = False
        self.__lowLevelHardware.stop()
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
        status = self.__lowLevelHardware.getStatus()
        if status != '0':
            return True
        else:
            return False


class PanoguyAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


class PanoguyShutter(AbstractHardwarePlugin, AbstractStandardShutterPlugin):
    def __init__(self, *args, **kwargs):
        """
        """
        AbstractHardwarePlugin.__init__(self, *args, **kwargs)
        AbstractStandardShutterPlugin.__init__(self, *args, **kwargs)

    def _init(self):
        Logger().trace("PanoguyShutter._init()")
        AbstractHardwarePlugin._init(self)
        AbstractStandardShutterPlugin._init(self)
        self.__lowLevelHardware = PanoguyLowLevelHardware()  # Move to parent class?

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self.__lowLevelHardware.setOutput(True)

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self.__lowLevelHardware.setOutput(False)

    def init(self):
        Logger().trace("PanoguyShutter.init()")
        AbstractHardwarePlugin.init(self)
        AbstractStandardShutterPlugin.init(self)
        self.__lowLevelHardware.setCapacity(self.capacity),
        self.__lowLevelHardware.setDriver(self._driver)
        self.__lowLevelHardware.initHardware()

    def shutdown(self):
        Logger().trace("PanoguyShutter.shutdown()")
        self._triggerOffShutter()
        AbstractHardwarePlugin.shutdown(self)
        AbstractStandardShutterPlugin.shutdown(self)


class PanoguyShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


def register():
    """ Register plugins.
    """
    PluginsManager().register(PanoguyAxis, PanoguyAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(PanoguyAxis, PanoguyAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(PanoguyShutter, PanoguyShutterController, capacity='shutter', name=NAME)
