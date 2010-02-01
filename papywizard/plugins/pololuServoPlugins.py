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

- PololuServoHardware
- PololuServoAxis
- PololuServoAxisController
- PololuServoShutter
- PololuServoShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import struct

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

from PyQt4 import QtCore

NAME = "Pololu Servo"

DEFAULT_CHANNEL = {'yawAxis': 1,
                   'pitchAxis': 2,
                   'shutter': 0
                   }
DEFAULT_SPEED = 30 # deg/s
DEFAULT_DIRECTION = QtGui.QApplication.translate("pololuServoPlugins", 'forward')
DEFAULT_ANGLE_1MS = 120. # angle for 1ms, which is 2 servo units (deg)
DEFAULT_NEUTRAL_POSITION = 3000 # controller value for neutral position
DEFAULT_VALUE_OFF = 0
DEFAULT_VALUE_ON = 127

DIRECTION_INDEX = {'forward': 1,
                   'reverse': -1
                   }
DIRECTION_TABLE = {'forward': QtGui.QApplication.translate("pololuServoPlugins", 'forward'),
                   'reverse': QtGui.QApplication.translate("pololuServoPlugins", 'reverse'),
                   QtGui.QApplication.translate("pololuServoPlugins", 'forward'): 'forward',
                   QtGui.QApplication.translate("pololuServoPlugins", 'reverse'): 'reverse'
                   }
MANUAL_SPEED_TABLE = {'slow': .5,
                      'normal': 2.,
                      'fast': 5.
                      }


class PololuServoHardware(AbstractHardwarePlugin):
    """
    """
    def _init(self):
        Logger().trace("PololuServoHardware._init()")
        AbstractHardwarePlugin._init(self)
        self._channel = None

    def _sendCmd(self, command, data1, data2=None):
        """ Send a command to Pololu controller.

        @param command: id of the command, in [0-5]
        @type command: int

        @param data1: first data byte, in [0-127]
        @type data1: int

        @param data2: second data byte, in [0-127]
        @type data2: int

        @todo: add retry
        """
        if data2 is not None:
           data2Str = hex(data2)
        else:
           data2Str = 'None'
        Logger().debug("PololuServoHardware._sendCmd: command=%d, servo=%d, data1=%s, data2=%s" % (command, self._channel, hex(data1), data2Str))
        if command in (0, 1, 2):
            if data2 is not None:
                raise ValueError("Command %d takes only 1 data parameter" % command)
            else:
                self._driver.write(struct.pack("BBBBB", 0x80, 0x01, command, self._channel, data1))
                size = 5
        elif command in (3, 4, 5):
            if data2 is None:
                raise ValueError("Command %d takes 2 data parameters" % command)
            else:
                self._driver.write(struct.pack("BBBBBB", 0x80, 0x01, command, self._channel, data1, data2))
                size = 6
        else:
            raise ValueError("Command must be in [0-5]")

        # Check controller answer
        data = self._driver.read(size)
        Logger().debug("PololuServoHardware._sendCmd: pololu returned: %s" % repr(data))

    def _initPololuServo(self):
        """ Turn on servo power.
        """
        self._driver.acquireBus()
        try:
            self._reset()
            self._setParameters(on=True)
        finally:
            self._driver.releaseBus()

    def _shutdownPololuServo(self):
        """ Turn off servo power.
        """
        self._driver.acquireBus()
        try:
            self._setParameters(on=False)
        finally:
            self._driver.releaseBus()

    def _configurePololuServo(self, speed, direction):
        """ Turn on servo power.

        @param speed: rotation speed
        @type speed: int

        @param direction: direction of rotation, in ('forward', 'reverse')
        @type direction: str
        """
        self._driver.acquireBus()
        try:
            self._setSpeed(speed)
            self._setParameters(on=True, direction=direction) # Add range_?
        finally:
            self._driver.releaseBus()

    def _reset(self):
        """ Reset the controller.

        How to do this with all drivers?
        """
        try:
            self._driver.setRTS(1)
            self._driver.setDTR(1)
            self._driver.setRTS(0)
            self._driver.setDTR(0)
        except AttributeError:
            Logger().exception("PololuServoHardware._reset()", debug=True)

    def _setParameters(self, on=True, direction='forward', range_=15):
        """ Set servo parameters.

        @param on: if True, turn on servo power
        @type on: bool

        @param direction: direction for 7/8 bits positionning function, in ('forward', 'reverse')
        @type direction: str

        @param range_: range for 7/8 bits positionning functions, in [0-31]
        @type range_: int
        """
        if direction not in ('forward', 'reverse'):
            raise ValueError("direction parameter must be in ('forward', 'reverse')")
        if not 0 <= range_ <= 31:
            raise ValueError("range parameter must be in [0-31]")
        data1 = (on << 6) | ((direction != 'forward') << 5) | range_
        self._driver.acquireBus()
        try:
            self._sendCmd(0, data1)
        finally:
            self._driver.releaseBus()

    def _setSpeed(self, speed):
        """ Set servo speed.

        @param speed: servo speed, in [0-127]
        @type speed: int
        """
        if not 0 <= speed <= 127:
            raise ValueError("speed must be in [0-127] (%d)" % speed)
        self._driver.acquireBus()
        try:
            self._sendCmd(1, speed)
        finally:
            self._driver.releaseBus()

    def _setPosition7bits(self, position):
        """ Set servo position (7 bits).

        @param position: servo position, in [0-127]
        @type position: int
        """
        if not 0 <= position <= 127:
            raise ValueError("position must be in [0-127] (%d)" % position)
        self._driver.acquireBus()
        try:
            self._sendCmd(2, position)
        finally:
            self._driver.releaseBus()

    def _setPosition8bits(self, position):
        """ Set servo position (8 bits).

        @param position: servo position, in [0-255]
        @type position: int
        """
        if not 0 <= position <= 255:
            raise ValueError("position must be in [0-255] (%d)" % position)
        data1 = position / 128
        data2 = position % 128
        self._driver.acquireBus()
        try:
            self._sendCmd(3, data1, data2)
        finally:
            self._driver.releaseBus()

    def _setPositionAbsolute(self, position):
        """ Set servo position.

        @param position: servo position, in [500-5500]
        @type position: int
        """
        if not 500 <= position <= 5500:
            raise ValueError("position must be in [500-5500] (%d)" % position)
        Logger().debug("PololuServoHardware._setPositionAbsolute(): position=%d" % position)
        data1 = position / 128
        data2 = position % 128
        self._driver.acquireBus()
        try:
            self._sendCmd(4, data1, data2)
        finally:
            self._driver.releaseBus()

    def _setNeutral(self, position):
        """ Set servo neutral position.

        @param position: servo neutral position, in [500-5500]
        @type position: int
        """
        if not 500 <= position <= 5500:
            raise ValueError("position must be in [500-5500] (%d)" % position)
        data1 = position / 128
        data2 = position % 128
        self._driver.acquireBus()
        try:
            self._sendCmd(5, data1, data2)
        finally:
            self._driver.releaseBus()


class PololuServoAxis(PololuServoHardware, AbstractAxisPlugin):
    def _init(self):
        Logger().trace("PololuServoAxis._init()")
        PololuServoHardware._init(self)
        AbstractAxisPlugin._init(self)
        self._pos = None
        self._endDrive = None

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_channel', 'CHANNEL', default=DEFAULT_CHANNEL[self.capacity])
        self._addConfigKey('_speed', 'SPEED', default=DEFAULT_SPEED)
        self._addConfigKey('_direction', 'DIRECTION', default=DEFAULT_DIRECTION)
        self._addConfigKey('_angle1ms', 'ANGLE_1MS', default=DEFAULT_ANGLE_1MS)
        self._addConfigKey('_neutralPos', 'NEUTRAL_POSITION', default=DEFAULT_NEUTRAL_POSITION)
        self._channel = self._config['CHANNEL']

    def _checkLimits(self, position):
        """ Check if the position can be reached.

        First check if the position in degres is in the user limits
        (done in parent class), then check if the servo can mechanically
        reach the position.
        """
        AbstractAxisPlugin._checkLimits(self, position)
        value = self._computeServoPosition(position)
        if not 500 <= value <= 5500:
            raise HardwareError("Servo limit reached: %d not in [500-5500]" % value)

    def init(self):
        Logger().trace("PololuServoAxis.init()")
        AbstractAxisPlugin.init(self)
        self._setPositionAbsolute(self._config['NEUTRAL_POSITION'])
        self._initPololuServo()
        self.configure()
        self._pos = 0.
        self._endDrive = 0

    def shutdown(self):
        Logger().trace("PololuServoAxis.shutdown()")
        self.stop()
        self._shutdownPololuServo()
        AbstractAxisPlugin.shutdown(self)

    def configure(self):
        Logger().trace("PololuServoAxis.configure()")
        AbstractAxisPlugin.configure(self)
        speed = self._computeServoSpeed(self._config['SPEED'])
        self._configurePololuServo(speed, self._config['DIRECTION'])

    def read(self):
        return self._pos - self._offset

    def _computeServoSpeed(self, speed):
        """ Compute controller servo value from position.

        @param speed: speed, in °/s
        @type speed: float

        @return: value to send to servo controller
        @rtype: int
        """
        servoSpeed = int(speed * 1000 / self._config['ANGLE_1MS'] / 50)
        return servoSpeed

    def _computeServoPosition(self, position):
        """ Compute controller servo value from position.

        @param position: position, in °
        @type position: float

        @return: value to send to servo controller
        @rtype: int
        """
        dir_ = DIRECTION_INDEX[self._config['DIRECTION']]
        servoPosition = int(self._config['NEUTRAL_POSITION'] + dir_ * position / self._config['ANGLE_1MS'] * 2000)
        return servoPosition

    def drive(self, pos, useOffset=True, wait=True):
        Logger().debug("PololuServoAxis.drive(): '%s' drive to %.1f" % (self.capacity, pos))
        currentPos = self.read()

        self._checkLimits(pos)

        if useOffset:
            position += self._offset

        self._driver.acquireBus()
        try:
            value = self._computeServoPosition(pos)
            self._setPositionAbsolute(value)
            self._endDrive = time.time() + abs(pos - self._pos) / self._config['SPEED']
            if wait:
                self.waitEndOfDrive()
            self._pos = pos
        finally:
            self._driver.releaseBus()

    def waitEndOfDrive(self):
        remaingTimeToWait = self._endDrive - time.time()
        Logger().debug("PololuServoAxis.waitEndOfDrive(): remaing time to wait %d" % remaingTimeToWait)
        if remaingTimeToWait > 0:
            time.sleep(remaingTimeToWait)
        self.waitStop()

    def startJog(self, dir_):
        """ Need to be run in a thread.
        """
        position = self._pos + self._offset
        if dir_ == '+':
            position += MANUAL_SPEED_TABLE[self._manualSpeed]
        else:
            position -= MANUAL_SPEED_TABLE[self._manualSpeed]

        # Call self.drive() ???

        self._checkLimits(position)
        self._driver.acquireBus()
        try:
            value = self._computeServoPosition(position)
            self._setPositionAbsolute(value)
            self._pos = position
        finally:
            self._driver.releaseBus()

    def stop(self):
        self.waitStop()

    def waitStop(self):
        pass

    def isMoving(self):
        if self._endDrive < time.time():
            return False
        else:
            return True


class PololuServoAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', QtGui.QApplication.translate("pololuServoPlugins", "Speed"),
                        SpinBoxField, (1, 99, "", " deg/s"), 'SPEED')
        self._addTab('Servo', QtGui.QApplication.translate("pololuServoPlugins", 'Servo'))
        self._addWidget('Servo', QtGui.QApplication.translate("pololuServoPlugins", "Channel"),
                        SpinBoxField, (0, 7), 'CHANNEL')
        directions = [DIRECTION_TABLE['forward'], DIRECTION_TABLE['reverse']]
        self._addWidget('Servo', QtGui.QApplication.translate("pololuServoPlugins", "Direction"),
                        ComboBoxField, (directions,), 'DIRECTION')
        self._addWidget('Servo', QtGui.QApplication.translate("pololuServoPlugins", "Angle for 1ms"),
                        DoubleSpinBoxField, (1., 999., 1, 0.1, "", " deg"), 'ANGLE_1MS')
        self._addWidget('Servo', QtGui.QApplication.translate("pololuServoPlugins", "Neutral position"),
                        SpinBoxField, (500, 5500), 'NEUTRAL_POSITION')


class PololuServoShutter(PololuServoHardware, AbstractStandardShutterPlugin):
    def _init(self):
        Logger().trace("PololuServoShutter._init()")
        PololuServoHardware._init(self)
        AbstractStandardShutterPlugin._init(self)

    def _defineConfig(self):
        PololuServoHardware._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)
        self._addConfigKey('_channel', 'CHANNEL', default=DEFAULT_CHANNEL[self.capacity])
        self._addConfigKey('_valueOff', 'VALUE_OFF', default=DEFAULT_VALUE_OFF)
        self._addConfigKey('_valueOn', 'VALUE_ON', default=DEFAULT_VALUE_ON)
        self._channel = self._config['CHANNEL']

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._driver.acquireBus()
        try:
            self._setPosition7bits(self._config['VALUE_ON'])
        finally:
            self._driver.releaseBus()

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._driver.acquireBus()
        try:
            self._setPosition7bits(self._config['VALUE_OFF'])
        finally:
            self._driver.releaseBus()

    def activate(self):
        Logger().trace("PololuServoShutter.activate()")
        self._initialPosition = self._config['VALUE_OFF']

    def init(self):
        Logger().trace("PololuServoShutter.init()")
        AbstractStandardShutterPlugin.init(self)
        self._initPololuServo()

    def shutdown(self):
        Logger().trace("PololuServoShutter.shutdown()")
        self._triggerOffShutter()
        self._shutdownPololuServo()
        AbstractStandardShutterPlugin.shutdown(self)


class PololuServoShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        Logger().trace("PololuServoShutterController._defineGui()")
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Servo', QtGui.QApplication.translate("pololuServoPlugins", 'Servo'))
        self._addWidget('Servo', QtGui.QApplication.translate("pololuServoPlugins", "Channel"),
                        SpinBoxField, (0, 7), 'CHANNEL')
        self._addWidget('Servo', QtGui.QApplication.translate("pololuServoPlugins", "Value off"),
                        SpinBoxField, (0, 127), 'VALUE_OFF')
        self._addWidget('Servo', QtGui.QApplication.translate("pololuServoPlugins", "Value on"),
                        SpinBoxField, (0, 127), 'VALUE_ON')


def register():
    """ Register plugins.
    """
    PluginsManager().register(PololuServoAxis, PololuServoAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(PololuServoAxis, PololuServoAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(PololuServoShutter, PololuServoShutterController, capacity='shutter', name=NAME)
