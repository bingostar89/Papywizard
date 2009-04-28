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

Hardware

Implements
==========

- PololuServoHardware
- PololuServoAxis
- PololuServoAxisController
- PololuServoYawAxis
- PololuServoYawAxisController
- PololuServoPitchAxis
- PololuServoPitchAxisController
- PololuServoShutter
- PololuServoShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import struct

from papywizard.common import config
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.common.pluginManager import PluginManager
from papywizard.hardware.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.hardware.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.hardware.hardwarePlugin import HardwarePlugin
from papywizard.controller.axisPluginController import AxisPluginController
from papywizard.controller.hardwarePluginController import HardwarePluginController
from papywizard.controller.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

from PyQt4 import QtCore

DEFAULT_SPEED = 5 # deg/s
DEFAULT_DIRECTION = 'forward'
DEFAULT_RATIO = 1
DEFAULT_TIME_VALUE = 0.5 # s
DEFAULT_MIRROR_LOCKUP = False
DEFAULT_BRACKETING_NBPICTS = 1
DEFAULT_BRACKETING_INTENT = 'exposure'
DEFAULT_PULSE_WIDTH_HIGH = 100 # ms
DEFAULT_PULSE_WIDTH_LOW = 100 # ms
DEFAULT_VALUE_OFF = 0
DEFAULT_VALUE_ON = 127

SPEED_COEF = 0.18 # deg. (angle for 1µs)
POSITION_COEF = 0.09 # deg. (angle for 1 controller unit)
NEUTRAL_POSITION = 3000 # controller value for neutral position (1.5ms)
DIRECTION_INDEX = {'forward': 1,
                   'reverse': -1}
MANUAL_SPEED_INDEX = {'slow': .5,
                      'normal': 2.,
                      'fast': 5.}
DIRECTION_INDEX = {'forward': 0, 'reverse': 1,
                   0: 'forward', 1: 'reverse'}

class PololuServoHardware(HardwarePlugin):
    _name = "Pololu Servo"

    def _init(self):
        Logger().trace("PololuServoHardware._init()")
        HardwarePlugin._init(self)
        self._channel = None

    def _sendCmd(self, command, data1, data2=None):
        """ Send a command to Pololu controller.

        @param command: id of the command, in [0-5]
        @type command: int

        @param data1: first data byte, in [0-127]
        @type data1: int

        @param data2: second data byte, in [0-127]
        @type data2: int
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
                #self._driver.write(struct.pack("BBBBB", 0x80, 0x01, command, self._channel, data1))
                size = 5
        elif command in (3, 4, 5):
            if data2 is None:
                raise ValueError("Command %d takes 2 data parameters" % command)
            else:
                #self._driver.write(struct.pack("BBBBBB", 0x80, 0x01, command, self._channel, data1, data2))
                size = 6
        else:
            raise ValueError("Command must be in [0-5]")

        # Purge buffer (does not work anymore!)
        #data = self._driver.read(size)
        #Logger().debug("PololuServoHardware._sendCmd: pololu returned: %s" % repr(data))

    def _reset(self):
        """ Reset the controller.

        How to do this with all drivers?
        """
        #self._serial.setRTS(1)
        #self._serial.setDTR(1)
        #self._serial.setRTS(0)
        #self._serial.setDTR(0)

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

    def _initPololuServo(self, speed=0, direction='forward'):
        """ Turn on servo power.

        @param speed: rotation speed
        @type speed: int

        @param direction: direction of rotation, in ('forward', 'reverse')
        @type diretion: str
        """
        self._driver.acquireBus()
        try:
            #self._reset()
            self._setParameters(on=True, direction=direction) # Add range_?
            self._setSpeed(speed)
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


class PololuServoAxis(PololuServoHardware, AbstractAxisPlugin):
    def _init(self):
        Logger().trace("PololuServoAxis._init()")
        PololuServoHardware._init(self)
        AbstractAxisPlugin._init(self)
        self._position = None
        self._endDrive = None

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        HardwarePlugin._defineConfig(self)
        #self._addConfigKey('_channel', 'CHANNEL', default=DEFAULT_CHANNEL)
        self._addConfigKey('_speed', 'SPEED', default=DEFAULT_SPEED)
        self._addConfigKey('_direction', 'DIRECTION', default=DEFAULT_DIRECTION)
        self._addConfigKey('_ratio', 'RATIO', default=DEFAULT_RATIO)

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

    def activate(self):
        Logger().trace("PololuServoHardware.activate()")

    def shutdown(self):
        Logger().trace("PololuServoHardware.shutdown()")

    def establishConnection(self):
        Logger().trace("PololuServoAxis.establishConnection()")
        PololuServoHardware.establishConnection(self)
        speed = self._computeServoSpeed(self._config['SPEED'])
        self._initPololuServo(speed, self._config['DIRECTION'])
        self._position = 0.
        self._endDrive = 0

    def shutdownConnection(self):
        Logger().trace("PololuServoAxis.shutdownConnection()")
        self.stop()
        self._shutdownPololuServo()
        PololuServoHardware.shutdownConnection(self)

    def read(self):
        return self._position - self._offset

    def _computeServoSpeed(self, speed):
        """ Compute controller servo value from position.

        @param speed: speed, in °/s
        @type speed: float

        @return: value to send to servo controller
        @rtype: int
        """
        servoSpeed = int(speed * self._config['RATIO'] / SPEED_COEF)
        return servoSpeed

    def _computeServoPosition(self, position):
        """ Compute controller servo value from position.

        @param position: position, in °
        @type position: float

        @return: value to send to servo controller
        @rtype: int
        """
        dir_ = DIRECTION_INDEX[self._config['DIRECTION']]
        servoPosition = int(NEUTRAL_POSITION + dir_ * position / (self._config['RATIO'] * POSITION_COEF))
        return servoPosition

    def drive(self, position, inc=False, useOffset=True, wait=True):
        """ @todo: use thread.
        """
        currentPos = self.read()

        # Compute absolute position from increment if needed
        if inc:
            position += currentPos
        else:
            if useOffset:
                position += self._offset

        self._checkLimits(position)
        self._driver.acquireBus()
        try:
            value = self._computeServoPosition(position)
            self._setPositionAbsolute(value)
            self._endDrive = time.time() + abs(position - self._position) / self._config['SPEED']
            if wait:
                self.waitEndOfDrive()
            self._position = position
        finally:
            self._driver.releaseBus()

    def stop(self):
        self.waitStop()

    def waitEndOfDrive(self):
        remaingTimeToWait = self._endDrive - time.time()
        Logger().debug("PololuServoAxis.waitEndOfDrive(): remaing time to wait %d" % remaingTimeToWait)
        if remaingTimeToWait > 0:
            time.sleep(remaingTimeToWait)
        self.waitStop()

    def startJog(self, dir_):
        """ Need to be run in a thread.
        """
        position = self._position + self._offset
        if dir_ == '+':
            position += MANUAL_SPEED_INDEX[self._manualSpeed]
        else:
            position -= MANUAL_SPEED_INDEX[self._manualSpeed]

        # Call self.drive() ???

        self._checkLimits(position)
        self._driver.acquireBus()
        try:
            value = self._computeServoPosition(position)
            self._setPositionAbsolute(value)
            self._position = position
        finally:
            self._driver.releaseBus()

    def waitStop(self):
        pass

    def isMoving(self):
        if self._endDrive >= time.time():
            return False
        else:
            return True


class PololuServoAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', "Speed", SpinBoxField, (1, 25, "", " deg/s"), 'SPEED')
        self._addTab('Servo')
        #self._addWidget('Servo', "Channel", SpinBoxField, (0, 7), 'CHANNEL')
        self._addWidget('Servo', "Direction", ComboBoxField, (['forward', 'reverse'],), 'DIRECTION')
        self._addWidget('Servo', "Ratio", DoubleSpinBoxField, (0.01, 10., 2., 0.01), 'RATIO')

class PololuServoYawAxis(PololuServoAxis):
    _capacity = 'yawAxis'

    def _init(self):
        Logger().trace("PololuServoYawAxis._init()")
        PololuServoAxis._init(self)
        self._channel = 1


class PololuServoYawAxisController(PololuServoAxisController):
    pass


class PololuServoPitchAxis(PololuServoAxis):
    _capacity = 'pitchAxis'

    def _init(self):
        Logger().trace("PololuServoPitchAxis._init()")
        PololuServoAxis._init(self)
        self._channel = 2


class PololuServoPitchAxisController(PololuServoAxisController):
    pass


class PololuServoShutter(PololuServoHardware, AbstractShutterPlugin):
    def _init(self):
        Logger().trace("PololuServoShutter._init()")
        PololuServoHardware._init(self)
        AbstractShutterPlugin._init(self)
        self._channel = 0
        self.__LastShootTime = time.time()

    def _getTimeValue(self):
        return self._config["TIME_VALUE"]

    def _getMirrorLockup(self):
        return self._config["MIRROR_LOCKUP"]

    def _getBracketingNbPicts(self):
        return self._config["BRACKETING_NB_PICTS"]

    def _getBracketingIntent(self):
        return self._config["BRACKETING_INTENT"]

    def _defineConfig(self):
        PololuServoHardware._defineConfig(self)
        AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_timeValue', 'TIME_VALUE', default=DEFAULT_TIME_VALUE)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NBPICTS)
        self._addConfigKey('_bracketingIntent', 'BRACKETING_INTENT', default=DEFAULT_BRACKETING_INTENT)
        self._addConfigKey('_pulseWidthHigh', 'PULSE_WIDTH_HIGH', default=DEFAULT_PULSE_WIDTH_HIGH)
        self._addConfigKey('_pulseWidthLow', 'PULSE_WIDTH_LOW', default=DEFAULT_PULSE_WIDTH_LOW)
        self._addConfigKey('_valueOff', 'VALUE_OFF', default=DEFAULT_VALUE_OFF)
        self._addConfigKey('_valueOn', 'VALUE_ON', default=DEFAULT_VALUE_ON)

    def activate(self):
        Logger().trace("PololuServoShutter.activate()")
        self._initialPosition = self._config['VALUE_OFF']

    def shutdown(self):
        Logger().trace("PololuServoShutter.shutdown()")

    def establishConnection(self):
        Logger().trace("PololuServoShutter.establishConnection()")
        PololuServoHardware.establishConnection(self)
        self._initPololuServo()
        self._position = 0.

    def shutdownConnection(self):
        Logger().trace("PololuServoShutter.establishConnection()")
        self._shutdownPololuServo()
        PololuServoHardware.shutdownConnection(self)

    def lockupMirror(self):
        Logger().trace("PololuServoShutter.lockupMirror()")
        self._driver.acquireBus()
        try:
            self._setPosition7bits(127)
            time.sleep(self.config['PULSE_WIDTH_HIGH'] / 1000.)
            self._setPosition7bits(0)
            return 0
        finally:
            self._driver.releaseBus()

    def shoot(self, bracketNumber):

        # Ensure that PULSE_WIDTH_LOW delay has elapsed before last shoot
        delay = self._config['PULSE_WIDTH_LOW'] / 1000. - (time.time() - self.__LastShootTime)
        if delay > 0:
            time.sleep(delay)
        Logger().trace("PololuServoShutter.shoot()")
        self._driver.acquireBus()

        try:

            # Trigger
            self._setPosition7bits(127)
            time.sleep(self._config['PULSE_WIDTH_HIGH'] / 1000.)
            self._setPosition7bits(0)

            # Wait for the end of shutter cycle
            delay = self._config['TIME_VALUE'] - self._config['PULSE_WIDTH_HIGH'] / 1000.
            if delay > 0:
                time.sleep(delay)

            self.__LastShootTime = time.time()
            return 0
        finally:
            self._driver.releaseBus()


class PololuServoShutterController(ShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', "Time value", DoubleSpinBoxField, (0.1, 3600, 1, 0.1, "", " s"), 'TIME_VALUE')
        self._addWidget('Main', "Mirror lockup", CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', "Bracketing nb picts", SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')
        self._addWidget('Main', "Bracketing intent", ComboBoxField, (['exposure', 'focus', 'white balance', 'movement'],), 'BRACKETING_INTENT')
        self._addWidget('Main', "Pulse width high", SpinBoxField, (10, 1000, "", " ms"), 'PULSE_WIDTH_HIGH')
        self._addWidget('Main', "Pulse width low", SpinBoxField, (10, 1000, "", " ms"), 'PULSE_WIDTH_LOW')
        self._addTab('Servo')
        self._addWidget('Servo', "Value off", SpinBoxField, (0, 127), 'VALUE_OFF')
        self._addWidget('Servo', "Value on", SpinBoxField, (0, 127), 'VALUE_ON')


def register():
    """ Register plugins.
    """
    PluginManager().register(PololuServoYawAxis, PololuServoYawAxisController)
    PluginManager().register(PololuServoPitchAxis, PololuServoPitchAxisController)
    PluginManager().register(PololuServoShutter, PololuServoShutterController)
