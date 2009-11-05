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

- MerlinOrionHardware
- MerlinOrionAxis
- MerlinOrionAxisController
- MerlinOrionShutter
- MerlinOrionShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
@todo: add private methods to MerlinOrionHardware for sending commands to MerlinOrion
"""

__revision__ = "$Id$"

import time
import sys
import threading

from PyQt4 import QtCore, QtGui

from papywizard.common import config
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

NAME = "Merlin-Orion"

DEFAULT_ALTERNATE_DRIVE = True
DEFAULT_INERTIA_ANGLE = 1. # °
#DEFAULT_ALTERNATE_FULL_CIRCLE = False
#DEFAULT_ENCODER_FULL_CIRCLE = 0xE62D3

ALTERNATE_DRIVE_ANGLE = 7. # °
ENCODER_ZERO = 0x800000
ENCODER_FULL_CIRCLE = 0xE62D3
AXIS_ACCURACY = 0.1 # °
AXIS_TABLE = {'yawAxis': 1,
              'pitchAxis': 2,
              'shutter': 1
              }
MANUAL_SPEED_TABLE = {'slow': 170,  # "AA0000"  / 5
                      'alternate': 80, # "500000"
                      'normal': 34, # "220000" nominal
                      'fast': 17   # "110000"  * 2
                      }


class MerlinOrionHardware(AbstractHardwarePlugin):
    """
    """
    def _decodeAxisValue(self, strValue):
        """ Decode value from axis.

        Values (position, speed...) returned by axis are
        32bits-encoded strings, low byte first.

        @param strValue: value returned by axis
        @type strValue: str

        @return: value
        @rtype: int
        """
        value = 0
        for i in xrange(3):
            value += eval("0x%s" % strValue[i*2:i*2+2]) * 2 ** (i * 8)

        return value

    def _encodeAxisValue(self, value):
        """ Encode value for axis.

        Values (position, speed...) to send to axis must be
        32bits-encoded strings, low byte first.

        @param value: value
        @type value: int

        @return: value to send to axis
        @rtype: str
        """
        strHexValue = "000000%s" % hex(value)[2:]
        strValue = strHexValue[-2:] + strHexValue[-4:-2] + strHexValue[-6:-4]

        return strValue.upper()

    def _encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        return (codPos - ENCODER_ZERO) * 360. / ENCODER_FULL_CIRCLE

    def _angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: int
        """
        return int(pos * ENCODER_FULL_CIRCLE / 360. + ENCODER_ZERO)

    def _sendCmd(self, cmd, param=""):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @return: answer
        @rtype: str
        """
        cmd = "%s%d%s" % (cmd, AXIS_TABLE[self.capacity], param)
        for nbTry in xrange(3):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write(":%s\r" % cmd)
                c = ''
                while c not in ('=', '!'):
                    c = self._driver.read(1)
                if c == '!':
                    c = self._driver.read(1) # Get error code
                    raise IOError("Unknown command '%s' (err=%s)" % (cmd, c))
                answer = ""
                while True:
                    c = self._driver.read(1)
                    if c == '\r':
                        break
                    answer += c

            except IOError:
                Logger().exception("MerlinOrionHardware._sendCmd")
                Logger().warning("MerlinOrionHardware._sendCmd(): %s axis %d can't sent command '%s'. Retrying..." % (NAME, AXIS_TABLE[self.capacity], cmd))
            else:
                break
        else:
            raise HardwareError("%s axis %d can't send command '%s'" % (NAME, AXIS_TABLE[self.capacity], cmd))
        #Logger().debug("MerlinOrionHardware._sendCmd(): axis %d cmd=%s, ans=%s" % (AXIS_TABLE[self.capacity], cmd, answer))

        return answer

    def _initMerlinOrion(self):
        """ Init the MerlinOrion hardware.

        Done only once per axis.
        """
        self._driver.acquireBus()
        try:

            # Stop motor
            self._sendCmd("L")

            # Check motor?
            self._sendCmd("F")

            # Get full circle count
            value = self._sendCmd("a")
            Logger().debug("MerlinOrionHardware._initMerlinOrion(): full circle count=%s" % hex(self._decodeAxisValue(value)))

            # Get sidereal rate
            value = self._sendCmd("D")
            Logger().debug("MerlinOrionHardware._initMerlinOrion(): sidereal rate=%s" % hex(self._decodeAxisValue(value)))

            # Get firmeware version
            value = self._sendCmd("e")
            Logger().debug("MerlinOrionHardware._initMerlinOrion(): firmeware version=%s" % value)

        finally:
            self._driver.releaseBus()

    def _read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            value = self._sendCmd("j")
        finally:
            self._driver.releaseBus()
        pos = self._encoderToAngle(self._decodeAxisValue(value))
        return pos

    def _drive(self, pos):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float
        """
        strValue = self._encodeAxisValue(self._angleToEncoder(pos))
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            self._sendCmd("G", "00")
            self._sendCmd("S", strValue)
            #self._sendCmd("I", self._encodeAxisValue(MANUAL_SPEED_TABLE[self._manualSpeed]))
            self._sendCmd("J")
        finally:
            self._driver.releaseBus()

    def _stop(self):
        """ Stop the axis.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
        finally:
            self._driver.releaseBus()

    def _startJog(self, dir_, speed):
        """ Start the axis.

        @param dir_: direction ('+', '-')
        @type dir_: str

        @param speed: speed
        @type speed: int
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            if dir_ == '+':
                self._sendCmd("G", "30")
            elif dir_ == '-':
                self._sendCmd("G", "31")
            else:
                raise ValueError("%s axis %d dir. must be in ('+', '-')" % (NAME, AXIS_TABLE[self.capacity]))
            self._sendCmd("I", self._encodeAxisValue(speed))
            self._sendCmd("J")
        finally:
            self._driver.releaseBus()

    def _getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self._driver.acquireBus()
        try:
            return self._sendCmd("f")
        finally:
            self._driver.releaseBus()


class MerlinOrionAxis(MerlinOrionHardware, AbstractAxisPlugin, QtCore.QThread):
    def __init__(self, *args, **kwargs):
        MerlinOrionHardware.__init__(self, *args, **kwargs)
        AbstractAxisPlugin.__init__(self, *args, **kwargs)
        QtCore.QThread.__init__(self)

    def _init(self):
        Logger().trace("MerlinOrionAxis._init()")
        MerlinOrionHardware._init(self)
        AbstractAxisPlugin._init(self)
        self.__run = False
        self.__driveFlag = False
        self.__setPoint = None

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_alternateDrive', 'ALTERNATE_DRIVE', default=DEFAULT_ALTERNATE_DRIVE)
        self._addConfigKey('_inertiaAngle', 'INERTIA_ANGLE', default=DEFAULT_INERTIA_ANGLE)
        #self._addConfigKey('_alternateEncoder360', 'ALTERNATE_FULL_CIRCLE', default=DEFAULT_ALTERNATE_FULL_CIRCLE)
        #self._addConfigKey('_encoder360', 'ENCODER_FULL_CIRCLE', default=DEFAULT_ENCODER_FULL_CIRCLE)

    def activate(self):
        Logger().trace("MerlinOrionHardware.activate()")
        AbstractAxisPlugin.activate(self)

        # Start the thread
        self.start()

    def deactivate(self):
        Logger().trace("MerlinOrionHardware.deactivate()")

        # Stop the thread
        self._stopThread()
        self.wait()
        AbstractAxisPlugin.deactivate(self)

    def init(self):
        Logger().trace("MerlinOrionAxis.init()")
        AbstractAxisPlugin.init(self)
        self._initMerlinOrion()

    def shutdown(self):
        Logger().trace("MerlinOrionAxis.shutdown()")
        self.stop()
        AbstractAxisPlugin.shutdown(self)

    def run(self):
        """ Main entry of the thread.
        """
        threadName = "%s_%s" % (self.name, self.capacity)
        threading.currentThread().setName(threadName)
        Logger().debug("MerlinOrionAxis.run(): start thread")
        self.__run = True
        while self.__run:
            if self.__driveFlag:

                # Choose alternate drive if needed
                currentPos = self.read()
                if self._config['ALTERNATE_DRIVE'] and \
                   1.1 * self._config['INERTIA_ANGLE'] < abs(self.__setPoint - currentPos) < ALTERNATE_DRIVE_ANGLE:
                    self._alternateDrive(self.__setPoint)
                else:
                    self._directDrive(self.__setPoint)
                self.__driveFlag = False
                self.waitEndOfDrive()  # ???

            self.msleep(config.SPY_REFRESH_DELAY)

        Logger().debug("MerlinOrionAxis.run(): thread terminated")

    def _stopThread(self):
        """ Stop the thread.
        """
        self.__run = False

    def read(self):
        pos = self._read() - self._offset
        return pos

    def drive(self, pos, useOffset=True, wait=True):
        Logger().debug("MerlinOrionAxis.drive(): '%s' drive to %.1f" % (self.capacity, pos))
        currentPos = self.read()

        self._checkLimits(pos)

        if useOffset:
            pos += self._offset

        # Only move if needed
        if abs(pos - currentPos) > AXIS_ACCURACY:
            self.__setPoint = pos
            self.__driveFlag = True # Start thread action

            # Wait end of movement
            if wait:
                self.waitEndOfDrive()

    def _directDrive(self, pos):
        """ Default (hardware) drive.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("MerlinOrionAxis._directDrive()")
        self._drive(pos)

    def _alternateDrive(self, pos):
        """ Alternate drive.

        This method implements an external closed-loop regulation.
        It is faster for angles < 6-7°, because in this case, the
        head does not accelerate to full speed, but rather stays at
        very low speed.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("MerlinOrionAxis._alternateDrive()")

        # Compute initial direction
        currentPos = self.read()
        if pos > currentPos:
            dir_ = '+'
        else:
            dir_ = '-'
        stopRequest = False

        # Alternate speed move
        Logger().debug("MerlinOrionAxis._alternateDrive(): alternate speed move")
        self._startJog(dir_, MANUAL_SPEED_TABLE['alternate'])

        # Check when stop
        while abs(pos - self.read()) > self._config['INERTIA_ANGLE']: # adjust inertia while moving?

            # Test if a stop request has been sent
            if not self.isMoving():
                stopRequest = True
                break
            time.sleep(0.1)
        self._stop()

        # Final move
        if abs(pos - self.read()) > AXIS_ACCURACY and not stopRequest:
            Logger().debug("MerlinOrionAxis._alternateDrive(): final move")
            self._drive(pos)

    def waitEndOfDrive(self):
        while self.isMoving():
            time.sleep(0.1)
        self.waitStop()

    def startJog(self, dir_):
        self._startJog(dir_, MANUAL_SPEED_TABLE[self._manualSpeed])

    def stop(self):
        self.__driveFlag = False
        self._stop()
        self.waitStop()

    def waitStop(self):
        pos = self.read()
        time.sleep(0.05)
        while True:
            if round(abs(pos - self.read()), 1) == 0:
                break
            pos = self.read()
            time.sleep(0.05)

    def isMoving(self):
        status = self._getStatus()
        if status[1] != '0' or self.__driveFlag:
            return True
        else:
            return False


class MerlinOrionAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Hard', QtGui.QApplication.translate("merlinOrionPlugins", 'Hard'))
        self._addWidget('Hard', QtGui.QApplication.translate("merlinOrionPlugins", "Alternate drive"),
                        CheckBoxField, (), 'ALTERNATE_DRIVE')
        self._addWidget('Hard', QtGui.QApplication.translate("merlinOrionPlugins", "Inertia angle"),
                        DoubleSpinBoxField, (0.1, 9.9, 1, .1, "", " deg"), 'INERTIA_ANGLE')
        #self._addWidget('Hard', QtGui.QApplication.translate("merlinOrionPlugins", "Alternate full circle"),
                        #CheckBoxField, (), 'ALTERNATE_FULL_CIRCLE')
        #self._addWidget('Hard', QtGui.QApplication.translate("merlinOrionPlugins", "Encoder full circle"),
                        #SpinBoxField, (0x080000, 0x380000, "", " units/turn"), 'ENCODER_FULL_CIRCLE')


class MerlinOrionShutter(MerlinOrionHardware, AbstractStandardShutterPlugin):
    def _init(self):
        Logger().trace("MerlinOrionShutter._init()")
        MerlinOrionHardware._init(self)
        AbstractStandardShutterPlugin._init(self)

    def _defineConfig(self):
        MerlinOrionHardware._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("O", "1")
        finally:
            self._driver.releaseBus()

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("O", "0")
        finally:
            self._driver.releaseBus()

    def init(self):
        Logger().trace("MerlinOrionShutter.init()")
        self._initMerlinOrion()

    def shutdown(self):
        Logger().trace("MerlinOrionShutter.shutdown()")
        self._triggerOffShutter()
        AbstractStandardShutterPlugin.shutdown(self)


class MerlinOrionShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


def register():
    """ Register plugins.
    """
    PluginsManager().register(MerlinOrionAxis, MerlinOrionAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(MerlinOrionAxis, MerlinOrionAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(MerlinOrionShutter, MerlinOrionShutterController, capacity='shutter', name=NAME)
