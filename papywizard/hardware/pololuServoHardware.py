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

 - PololuServoHardware

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import struct

from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.abstractHardware import AbstractHardware

SPEED_TABLE = { 1: {'speed': 5, 'accel':  1,},
                2: {'speed': 10, 'accel':  5},
                3: {'speed': 20, 'accel':  10}
               }


class PololuServoHardware(AbstractHardware):
    pass


class PololuMicroMaestroHardware(PololuServoHardware):
    """ Micro Maestro low-level hardware
    """
    SERVO_MIN = 64
    SERVO_MAX = 83280

    def __splitLowHigh(self, value):
        """ Split value in low/high bytes.

        Also set the MSB to 0, as controller expects.

        @param value: value to split
        @type value: int

        @return: (low, high) value
        @rtype: tuple of int
        """
        low = value & 0x7f
        high = (value >> 7) & 0x7f

        return low, high

    def __sendCmd(self, command, *args):
        """ Send a command to Pololu controller.

        @param command: command to send
        @type command: int

        @todo: add retry
        """
        #Logger().debug("PololuMicroMaestroHardware.__sendCmd: command=0x%x, args=%s" % (command, args))

        # Send command to controller
        size = len(args) + 1
        self._driver.write(struct.pack(size * 'B', 0x80 + command, *args))

    def init(self):
        """ Turn on servo power.
        """
        self._driver.acquireBus()
        try:
            self.reset()

            # Stop internal script
            self.stopScript()
        finally:
            self._driver.releaseBus()

    def shutdown(self):
        """ Turn off servo power.
        """
        self._driver.acquireBus()
        try:

            # Restart internal script
            #self.restartScriptAt(0)
            pass
        finally:
            self._driver.releaseBus()

    def configure(self, speedIndex):
        """ Turn on servo power.

        @param speed: rotation speed
        @type speed: int

        @param accel: acceleration
        @type direction: int
        """
        self._driver.acquireBus()
        try:
            self.setSpeed(SPEED_TABLE[speedIndex]['speed'])
            self.setAcceleration(SPEED_TABLE[speedIndex]['accel'])
        finally:
            self._driver.releaseBus()

    def reset(self):
        """ Reset the controller.

        How to do this with all drivers?
        """
        self._driver.acquireBus()
        try:
            self._driver.setRTS(1)
            self._driver.setDTR(1)
            self._driver.setRTS(0)
            self._driver.setDTR(0)
        except AttributeError:
            Logger().exception("PololuMicroMaestroHardware.reset()", debug=True)
        finally:
            self._driver.releaseBus()

    def setTarget(self, target):
        """ Set servo target.

        @param target: servo target, in µs
        @type position: float
        """
        if not PololuMicroMaestroHardware.SERVO_MIN <= target <= PololuMicroMaestroHardware.SERVO_MAX:
            raise ValueError("position must be in [%d-%d] (%.2f)" %
                             (PololuMicroMaestroHardware.SERVO_MIN, PololuMicroMaestroHardware.SERVO_MAX, position))
        Logger().debug("PololuMicroMaestroHardware.setTarget(): target=%.2fµs (%d)" % (target, int(target * 4)))
        low, high = self.__splitLowHigh(int(target * 4))
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x04, self._axis, low, high)
        finally:
            self._driver.releaseBus()

    def setSpeed(self, speed):
        """ Set servo speed.

        @param speed: servo speed, in [0-255]
        @type speed: int
        """
        if not 0 <= speed <= 255:
            raise ValueError("speed must be in [0-255] (%d)" % speed)
        low, high = self.__splitLowHigh(speed)
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x07, self._axis, low, high)
        finally:
            self._driver.releaseBus()

    def setAcceleration(self, accel):
        """ Set servo speed.

        @param accel: servo acceleration, in [0-255]
        @type accel: int
        """
        if not 0 <= accel <= 255:
            raise ValueError("accel must be in [0-255] (%d)" % accel)
        low, high = self.__splitLowHigh(accel)
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x09, self._axis, low, high)
        finally:
            self._driver.releaseBus()

    def getPosition(self):
        """ Get servo position.

        @return: servo position, in µs
        @ttype: float
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x10, self._axis)
            ans = self._driver.read(2)
        finally:
            self._driver.releaseBus()
        #Logger().debug("PololuMicroMaestroHardware.getPosition: Pololu returned %s" % repr(ans))
        low, high = struct.unpack("BB", ans)
        position = (low + 255 * high) / 4.

        return position

    def getMovingState(self):
        """ Get servos moving state.

        @return: 0: servos are not moving
                 1: at least one servo is moving
        @rtype: int
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x13)
            ans = self._driver.read(1)
        finally:
            self._driver.releaseBus()
        #Logger().debug("PololuMicroMaestroHardware.getMovingState: Pololu returned %s" % repr(ans))
        movingState = struct.unpack('B', ans)[0]

        return movingState

    def getErrors(self):
        """ Get controller errors.

        @return: error code
        @rtype: int

        @todo: add a method to retreive error message(s)
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x21)
            ans = self._driver.read(2)
        finally:
            self._driver.releaseBus()
        Logger().debug("PololuMicroMaestroHardware.getError: Pololu returned %s" % repr(ans))
        low, high = struct.unpack("BB", ans)
        errorCode = low + 255 * high

        return errorCode

    def goHome(self):
        """ Set servos to their home position.

        Note: the controller must be configured with Pololu interface.
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x22)
        finally:
            self._driver.releaseBus()

    def stopScript(self):
        """ Stop internal script.
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x24)
        finally:
            self._driver.releaseBus()

    def restartScriptAt(self, subroutine):
        """ Restart internal script at subroutine.
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x27, subroutine)
        finally:
            self._driver.releaseBus()

    def restartScriptAtWithParam(self, subroutine, param):
        """ Stop internal script.
        """
        self._driver.acquireBus()
        try:
            low, high = self.__splitLowHigh(param)
            self.__sendCmd(0x28, subroutine, low, high)
        finally:
            self._driver.releaseBus()

    def getScriptStatus(self):
        """ Get script status.

        @return: 0: script is running
                 1: script is stopped
        @rtype: int
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd(0x2e)
            ans = self._driver.read(1)
        finally:
            self._driver.releaseBus()
        Logger().debug("PololuMicroMaestroHardware.getScriptStatus: Pololu returned %s" % repr(ans))
        status = struct.unpack('B', ans)[0]

        return status


class PololuSerialHardware(PololuServoHardware):
    """ Pololu serial low-level hardware.
    """
    def __sendCmd(self, command, data1, data2=None):
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
        #Logger().debug("PololuServoHardware.__sendCmd: command=%d, servo=%d, data1=0x%x, data2=%s" % (command, self._axis, data1, data2Str))
        if command in (0, 1, 2):
            if data2 is not None:
                raise ValueError("Command %d takes only 1 data parameter" % command)
            else:
                self._driver.write(struct.pack("BBBBB", 0x80, 0x01, command, self._axis, data1))
                size = 5
        elif command in (3, 4, 5):
            if data2 is None:
                raise ValueError("Command %d takes 2 data parameters" % command)
            else:
                self._driver.write(struct.pack("BBBBBB", 0x80, 0x01, command, self._axis, data1, data2))
                size = 6
        else:
            raise ValueError("Command must be in [0-5]")

        # Check controller answer
        data = self._driver.read(size)
        #Logger().debug("PololuServoHardware.__sendCmd: Pololu returned: %s" % repr(data))

    def init(self):
        """ Turn on servo power.
        """
        self._driver.acquireBus()
        try:
            self.reset()
            self.setParameters(on=True)
        finally:
            self._driver.releaseBus()

    def shutdown(self):
        """ Turn off servo power.
        """
        self._driver.acquireBus()
        try:
            self.setParameters(on=False)
        finally:
            self._driver.releaseBus()

    def configure(self, speed, direction):
        """ Turn on servo power.

        @param speed: rotation speed
        @type speed: int

        @param direction: direction of rotation, in ('forward', 'reverse')
        @type direction: str
        """
        self._driver.acquireBus()
        try:
            self.setSpeed(speed)
            self.setParameters(on=True, direction=direction) # Add range_?
        finally:
            self._driver.releaseBus()

    def reset(self):
        """ Reset the controller.

        How to do this with all drivers?
        """
        try:
            self._driver.setRTS(1)
            self._driver.setDTR(1)
            self._driver.setRTS(0)
            self._driver.setDTR(0)
        except AttributeError:
            Logger().exception("PololuServoHardware.reset()", debug=True)

    def setParameters(self, on=True, direction='forward', range_=15):
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
            self.__sendCmd(0, data1)
        finally:
            self._driver.releaseBus()

    def setSpeed(self, speed):
        """ Set servo speed.

        @param speed: servo speed, in [0-127]
        @type speed: int
        """
        if not 0 <= speed <= 127:
            raise ValueError("speed must be in [0-127] (%d)" % speed)
        self._driver.acquireBus()
        try:
            self.__sendCmd(1, speed)
        finally:
            self._driver.releaseBus()

    def setPosition7bits(self, position):
        """ Set servo position (7 bits).

        @param position: servo position, in [0-127]
        @type position: int
        """
        if not 0 <= position <= 127:
            raise ValueError("position must be in [0-127] (%d)" % position)
        self._driver.acquireBus()
        try:
            self.__sendCmd(2, position)
        finally:
            self._driver.releaseBus()

    def setPosition8bits(self, position):
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
            self.__sendCmd(3, data1, data2)
        finally:
            self._driver.releaseBus()

    def setPositionAbsolute(self, position):
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
            self.__sendCmd(4, data1, data2)
        finally:
            self._driver.releaseBus()

    def setNeutral(self, position):
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
            self.__sendCmd(5, data1, data2)
        finally:
            self._driver.releaseBus()
