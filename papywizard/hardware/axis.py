# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Frédéric Mantegazza

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

- AbstractAxis
- Axis
- AxisSimulation

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import threading

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.common.helpers import decodeAxisValue, encodeAxisValue, deg2cod, cod2deg


class AbstractAxis(object):
    """ Abstract axis.
    """
    def __init__(self, num):
        """ Init the axis.

        @param num: axis num (1: yaw, 2: pitch)
        @type num: int
        """
        super(AbstractAxis, self).__init__()

        self._num = num
        self._plusLimit = 9999.9
        self._minusLimit = -9999.9

    def _checkLimits(self, pos):
        """ Check if position is in axis limits.

        @param pos: position to check
        @type pos: float
        """
        if not self._minusLimit <= pos <= self._plusLimit:
            raise HardwareError("Axis %d limit reached: %.1f not in [%.1f:%.1f]" % \
                                 (self._num, pos, self._minusLimit, self._plusLimit))

    def init(self):
        """ Init the axis hardware.
        """
        raise NotImplementedError

    def reset(self):
        """ Reset the axis hardware.
        """
        raise NotImplementedError

    def setOrigin(self):
        """ Set current axis positions as origin.

        Use offset.
        """
        raise NotImplementedError

    def setLimit(self, dir_, limit):
        """ Set the minus limit.

        @param dir_: direction to limit ('+', '-')
        @type dir_: char

        @param limit: minus limit to set
        @type limit: float
        """
        if dir_ == '+':
            self._plusLimit = limit
        elif dir_ == '-':
            self._minusLimit = limit
        else:
            raise ValueError("dir must be in ('+', '-')")

    def clearLimits(self):
        """ Clear all limits.
        """
        self._plusLimit = 9999.9
        self._minusLimit = -9999.9

    def read(self):
        """ Return the current position of axis.

        @return: position, in °
        @rtype: float
        """
        raise NotImplementedError

    def drive(self, pos, inc=False, wait=True):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float

        @param inc: if True, pos is an increment
        @type inc: bool

        @param wait: if True, wait for end of movement,
                     returns immediatly otherwise.
        @type wait: boot
        """
        raise NotImplementedError

    def stop(self):
        """ stop drive axis.
        """
        raise NotImplementedError

    def waitEndOfDrive(self):
        """ Wait for end of drive.
        """
        raise NotImplementedError

    def startJog(self, dir_):
        """ Start axis in specified direction.

        @param dir_: direction ('+', '-')
        @type dir_: char
        """
        raise NotImplementedError

    def waitStop(self):
        """ Wait until axis does not move anymore (inertia).
        """
        raise NotImplementedError

    def isMoving(self):
        """ Check if axis is moving.

        @return: True if moving, False if stopped
        @rtype: bool
        """
        raise NotImplementedError

    def getStatus(self):
        """ Return the status of the axis.
        """
        raise NotImplementedError

    def setOutput(self, level):
        """ Set souput to level.

        The output of the V axis is wired to the shoot opto.
        Using thie method on the other axis does nothing.

        @param level: level to set to shoot output
        @type level: int
        """
        raise NotImplementedError


class Axis(AbstractAxis):
    """ Hardware axis.
    """
    def __init__(self, num, driver):
        super(Axis, self).__init__(num)

        self.__driver = driver
        self.__offset = 0

    def _sendCmd(self, cmd, param=""):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @return: answer
        @rtype: str

        @todo: check if bus is busy before sending command (really usefull?) -> in acquireBus ?
        """
        cmd = "%s%d%s" % (cmd, self._num, param)
        for nbTry in xrange(3):
            try:
                answer = self.__driver.sendCmd(cmd)
            except IOError:
                Logger().exception("Axis._sendCmd")
                Logger().warning("Axis._sendCmd(): axis %d can't sent command. Retrying..." % self._num)
            else:
                break
        if nbTry == 2:
            raise HardwareError("Axis %d can't send command" % self._num)
        #Logger().debug("Axis._sendCmd(): axis %d cmd=%s, ans=%s" % (self._num, cmd, answer))
        return answer

    def init(self):
        self.__driver.acquireBus()
        try:
            self._sendCmd("L")
            self._sendCmd("F")
            self._sendCmd("a")
            self._sendCmd("D")
        finally:
            self.__driver.releaseBus()

    def reset(self):
        pass # find commands to send...

    def setOrigin(self):
        self.__offset += self.read()

    def read(self):
        self.__driver.acquireBus()
        try:
            value = self._sendCmd("j")
        finally:
            self.__driver.releaseBus()
        pos = cod2deg(decodeAxisValue(value))
        pos -= self.__offset

        return pos

    def drive(self, pos, inc=False, wait=True):
        currentPos = self.read()

        # Compute absolute position from increment if needed
        if inc:
            pos = currentPos + inc
        else:
            pos += self.__offset

        self._checkLimits(pos)

        # Choose between default (hardware) method or external closed-loop method
        if pos - currentPos > 6.:
            self._driveWithInternalClosedLoop(pos)
        else:
            self._driveWithInternalClosedLoop(pos)

        # Wait end of movement
        # Does not work for external closed-loop drive. Need to execute drive in a thread.
        if wait:
            self.waitEndOfDrive()

    def _driveWithInternalClosedLoop(self, pos):
        """ Default (hardware) drive.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("Axis._drive1()")
        strValue = encodeAxisValue(deg2cod(pos))
        self.__driver.acquireBus()
        try:
            self._sendCmd("L")
            self._sendCmd("G", "00")
            self._sendCmd("S", strValue)
            self._sendCmd("J")
        finally:
            self.__driver.releaseBus()

    def _driveWithExternalClosedLoop(self, pos):
        """ External closed-loop drive.

        This method implements an external closed-loop regulation.
        It is faster for angles < 6-7°, because in this case, the
        head does not accelerate to full speed, but rather stays at
        very low speed.
        
        Problem: this drive can't be stopped, neither run concurrently
        on both axis without big modifications in multi-threading stuff.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("Axis._drive2()")
        self.__driver.acquireBus()
        try:
            self._sendCmd("L")
            initialPos = self.read()

            # Compute direction
            if pos > initialPos:
                self._sendCmd("G", "30")
            else:
                self._sendCmd("G", "31")

            # Load speed
            self._sendCmd("I", "500000")

            # Start move
            self._sendCmd("J")
        finally:
            self.__driver.releaseBus()

        # Closed-loop drive
        stopRequest = False
        while abs(pos - self.read()) > .5: # optimal delta depends on speed/inertia

            # Test if a stop request has been sent
            if not self.isMoving():
                break
            time.sleep(0.1)
        self.stop()

        # Final drive (auto) if needed
        if abs(pos - self.read()) > config.AXIS_ACCURACY and not stopRequest:
            self._drive1(pos)

    def stop(self):
        self._sendCmd("L")
        self.waitStop()

    def waitEndOfDrive(self):
        while True:
            if not self.isMoving():
                break
            time.sleep(0.1)
        self.waitStop()

    def startJog(self, dir_):
        self.__driver.acquireBus()
        try:
            self._sendCmd("L")
            if dir_ == '+':
                self._sendCmd("G", "30")
            elif dir_ == '-':
                self._sendCmd("G", "31")
            else:
                raise ValueError("Axis %d dir. must be in ('+', '-')" % self._num)

            self._sendCmd("I", "220000")
            self._sendCmd("J")
        finally:
            self.__driver.releaseBus()

    def waitStop(self):
        pos = self.read()
        time.sleep(0.05)
        while True:
            if round(abs(pos - self.read()), 1) == 0:
                break
            pos = self.read()
            time.sleep(0.05)

    def isMoving(self):
        status = self.getStatus()
        if status[1] != '0':
            return True
        else:
            return False

    def getStatus(self):
        return self._sendCmd("f")

    def setOutput(self, level):
        self.__driver.acquireBus()
        try:
            if level:
                self._sendCmd("O", "1")
            else:
                self._sendCmd("O", "0")
        finally:
            self.__driver.releaseBus()


class AxisSimulation(AbstractAxis, threading.Thread):
    """ Simulated hardware axis.
    """
    def __init__(self, num):
        super(AxisSimulation, self).__init__(num)

        self.setDaemon(1)
        self.setName("Axis #%d" % num)

        self.__pos = 0.
        self.__jog = False
        self.__drive = False
        self.__setpoint = None
        self.__dir = None
        self.__time = None
        self.__run = False

    def run(self):
        """ Main entry of the thread.
        """
        self.__run = True
        while self.__run:

            # Jog command
            if self.__jog:
                if self.__time == None:
                    self.__time = time.time()
                else:
                    inc = (time.time() - self.__time) * config.AXIS_SPEED
                    self.__time = time.time()
                    if self.__dir == '+':
                        self.__pos += inc
                    elif self.__dir == '-':
                        self.__pos -= inc
                    #Logger().debug("AxisSimulation.run(): axis %d inc=%.1f, new __pos=%.1f" % (self._num, inc, self.__pos))
            else:
                self.__time = None

            # Drive command. Check when stop
            if self.__drive:
                #Logger().trace("AxisSimulation.run(): axis %d driving" % self._num)
                if self.__dir == '+':
                    if self.__pos >= self.__setpoint:
                        self.__jog = False
                        self.__drive = False
                        self.__pos = self.__setpoint
                elif self.__dir == '-':
                    if self.__pos <= self.__setpoint:
                        self.__jog = False
                        self.__drive = False
                        self.__pos = self.__setpoint

            time.sleep(config.SPY_FAST_REFRESH)

        Logger().debug("AxisSimulation.run(): axis simulation thread terminated")

    def stopThread(self):
        """ Stop the thread.
        """
        self.__run = False

    def init(self):
        self.__jog = False
        self.__drive = False

    def reset(self):
        self.__jog = False
        self.__drive = False

    def setOrigin(self):
        self.__pos = 0.

    def read(self):
        return self.__pos

    def drive(self, pos, inc=False, wait=True):
        Logger().debug("AxisSimulation.drive(): axis %d drive to %.1f" % (self._num, pos))

        # Compute absolute position from increment if needed
        if inc:
            self.__setpoint = self.__pos + inc
        else:
            self.__setpoint = pos

        self._checkLimits(self.__setpoint)

        # Drive to requested position
        if self.__setpoint > self.__pos:
            self.__dir = '+'
        elif self.__setpoint < self.__pos:
            self.__dir = '-'
        else:
            return
        self.__drive = True
        self.__jog = True

        # Wait end of movement
        if wait:
            self.waitEndOfDrive()

    def stop(self):
        self.__jog = False
        self.__drive = False

    def waitEndOfDrive(self):
        while self.__drive:
            time.sleep(0.1)

    def startJog(self, dir_):
        self.__dir = dir_
        self.__jog = True

    def waitStop(self):
        pass

    def isMoving(self):
        return self.__jog

    def getStatus(self):
        return "000"

    def setOutput(self, level):
        Logger().debug("AxisSimulation.setOutput(): axis %d level=%d" % (self._num, level))

