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


class PololuServoHardware(AbstractHardware):
    """ Pololu servo low-level hardware.
    """
    def _init(self):
        Logger().trace("PololuServoHardware._init()")
        AbstractHardware._init(self)
        self._channel = None

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
        Logger().debug("PololuServoHardware.__sendCmd: command=%d, servo=%d, data1=%s, data2=%s" % (command, self._channel, hex(data1), data2Str))
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
        Logger().debug("PololuServoHardware.__sendCmd: pololu returned: %s" % repr(data))

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
            self.__sendCmd(0, data1)
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
            self.__sendCmd(1, speed)
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
            self.__sendCmd(2, position)
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
            self.__sendCmd(3, data1, data2)
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
            self.__sendCmd(4, data1, data2)
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
            self.__sendCmd(5, data1, data2)
        finally:
            self._driver.releaseBus()
