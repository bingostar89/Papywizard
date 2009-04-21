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

__revision__ = "$Id: merlinPlugins.py 1743 2009-04-17 17:46:43Z fma $"

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

DEFAULT_SPEED = 63 # Medium speed
DEFAULT_DIRECTION = 'forward'
MANUAL_SPEED = {'slow': 127,
                'normal': 63,
                'fast': 0}


class PololuServoHardware(HardwarePlugin):
    _name = "PololuServo"

    def _init(self):
        Logger().trace("PololuServoHardware._init()")
        HardwarePlugin._init(self)
        self._numAxis = None
        #self._serial.setRTS(0)
        #self._serial.setDTR(0)

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
        Logger().debug("PololuServoHardware._sendCmd: command=%d, servo=%d, data1=%s, data2=%s" % (command, self._numAxis, hex(data1), data2Str))
        if command in (0, 1, 2):
            if data2 is not None:
                raise ValueError("Command %d takes only 1 data parameter" % command)
            else:
                self._driver.write(struct.pack("BBBBB", 0x80, 0x01, command, self._numAxis, data1))
                size = 5
        elif command in (3, 4, 5):
            if data2 is None:
                raise ValueError("Command %d takes 2 data parameters" % command)
            else:
                self._driver.write(struct.pack("BBBBBB", 0x80, 0x01, command, self._numAxis, data1, data2))
                size = 6
        else:
            raise ValueError("Command must be in [0-5]")

        # Purge buffer
        Logger().debug("PololuServoHardware._sendCmd: pololu returned: %s" % repr(self._driver.read(size)))

    def _setParameters(self, on=True, direction='forward', range_=15):
        """ Set servo parameters.

        @param on: if True, turn on servo power
        @type on: bool

        @param direction: direction of rotation, in ('forward', 'reverse')
        @type diretion: str

        @param range: range for 7/8 bits positionning functions, in [0-31]
        @type range: int
        """
        if direction not in ('forward', 'reverse'):
            raise ValueError("direction parameter must be in ('forward', 'reverse')")
        if not 0 <= range_ <= 31:
            raise ValueError("range parameter must be in [0-31]")
        data1 = on << 6 | (direction != 'forward') << 5 | (range_ & 31)
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

    def _initPololuServo(self):
        """ Turn on servo power.
        """
        self._driver.acquireBus()
        try:
            self._setParameters(on=True, direction=self._config['DIRECTION'])
        finally:
            self._driver.releaseBus()

    def _shutdownPololuServo(self):
        """ Turn off servo power.
        """
        self._driver.acquireBus()
        try:
            self._setParameters(on=False, direction=self._config['DIRECTION'])
        finally:
            self._driver.releaseBus()


class PololuServoAxis(PololuServoHardware, AbstractAxisPlugin):
    def _init(self):
        Logger().trace("PololuServoAxis._init()")
        PololuServoHardware._init(self)
        AbstractAxisPlugin._init(self)
        self._position = None

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        HardwarePlugin._defineConfig(self)
        self._addConfigKey('_speed', 'SPEED', default=DEFAULT_SPEED)
        self._addConfigKey('_direction', 'DIRECTION', default=DEFAULT_DIRECTION)
        self._addConfigKey('_ratio', 'RATIO', default=1.)

    def activate(self):
        Logger().trace("PololuServoHardware.activate()")

    def shutdown(self):
        Logger().trace("PololuServoHardware.shutdown()")

    def establishConnection(self):
        Logger().trace("PololuServoAxis.establishConnection()")
        PololuServoHardware.establishConnection(self)
        self._initPololuServo()
        self._position = 0.

    def shutdownConnection(self):
        Logger().trace("PololuServoAxis.shutdownConnection()")
        #self.stop()
        self._shutdownPololuServo()
        PololuServoHardware.shutdownConnection(self)

    def read(self):
        return self._position - self._offset

    def drive(self, position, inc=False, useOffset=True, wait=True):
        currentPos = self.read()

        # Compute absolute position from increment if needed
        if inc:
            position = currentPos + inc
        else:
            if useOffset:
                position += self._offset

        self._checkLimits(position)
        self._driver.acquireBus()
        try:
            self._setSpeed(self._config['SPEED'])
            self._drive(position)
        finally:
            self._driver.releaseBus()

        # Wait end of movement
        # Does not work for external closed-loop drive. Need to execute drive in a thread.
        if wait:
            self.waitEndOfDrive()

    def _drive(self, pos):
        """ Real drive.

        @param pos: position to reach, in °
        @type pos: float
        """
        if not -90. <= pos <= 90.:
            raise HardwareError("Position must be in [-90-90]")
        value = int(pos * (4000 - 1000) / (90. - (-90.)) + (4000 + 1000) / 2)
        self._driver.acquireBus()
        try:
            self._setPositionAbsolute(value)
        finally:
            self._driver.releaseBus()
        self._position = pos

    def stop(self):
        pass
        self.waitStop()

    def waitEndOfDrive(self):
        while True:
            if not self.isMoving():
                break
            time.sleep(0.1)
        self.waitStop()

    def startJog(self, dir_):
        """ Need to be run in a thread.
        """
        pos = self._position + self._offset
        if dir_ == '+':
            pos += 0.5
        else:
            pos -= 0.5
        self._checkLimits(pos)
        self._driver.acquireBus()
        try:
            self._setSpeed(MANUAL_SPEED[self._manualSpeed])
            self._drive(pos)
        finally:
            self._driver.releaseBus()
        self._position = pos

    def waitStop(self):
        pass

    def isMoving(self):
        return False

    def setManualSpeed(self, speed):
        self._manualSpeed = speed


class PololuServoAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Servo')
        self._addWidget('Servo', "Speed", SpinBoxField, (1, 127), 'SPEED')
        self._addWidget('Servo', "Direction", ComboBoxField, (['forward', 'reverse'],), 'DIRECTION')
        self._addWidget('Servo', "Ratio", DoubleSpinBoxField, (0.1, 9.9), 'RATIO')


class PololuServoYawAxis(PololuServoAxis):
    _capacity = 'yawAxis'

    def _init(self):
        Logger().trace("PololuServoYawAxis._init()")
        PololuServoAxis._init(self)
        self._numAxis = 1


class PololuServoYawAxisController(PololuServoAxisController):
    pass


class PololuServoPitchAxis(PololuServoAxis):
    _capacity = 'pitchAxis'

    def _init(self):
        Logger().trace("PololuServoPitchAxis._init()")
        PololuServoAxis._init(self)
        self._numAxis = 2


class PololuServoPitchAxisController(PololuServoAxisController):
    pass


class PololuServoShutter(PololuServoHardware, AbstractShutterPlugin):
    def _init(self):
        Logger().trace("PololuServoShutter._init()")
        PololuServoHardware._init(self)
        AbstractShutterPlugin._init(self)
        self._numAxis = 0
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
        self._addConfigKey('_timeValue', 'TIME_VALUE', default=0.5)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=False)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=1)
        self._addConfigKey('_bracketingIntent', 'BRACKETING_INTENT', default='exposure')
        self._addConfigKey('_pulseWidthHigh', 'PULSE_WIDTH_HIGH', default=100)
        self._addConfigKey('_pulseWidthLow', 'PULSE_WIDTH_LOW', default=100)

    def activate(self):
        Logger().trace("PololuServoShutter.activate()")

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


def register():
    """ Register plugins.
    """
    PluginManager().register(PololuServoYawAxis, PololuServoYawAxisController)
    PluginManager().register(PololuServoPitchAxis, PololuServoPitchAxisController)
    PluginManager().register(PololuServoShutter, PololuServoShutterController)
