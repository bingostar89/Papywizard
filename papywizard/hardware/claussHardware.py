# -*- coding: utf-8 -*-

""" Clauss head remote control.

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

 - ClaussHardware

Claus protocol
==============

The Clauss protocol is available on Kolor wiki : http://www.autopano.net/wiki-fr/action/view/Tête_panoramique_Clauss

@author: Martin Loyer
@copyright: (C) 2010 Martin Loyer
@license: CeCILL
"""

__revision__ = "$Id: claussHardware.py 2300 2011-01-02 22:18:09Z martinlbb $"

import time

from PyQt4 import QtCore

from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.abstractHardware import AbstractHardware


class ClaussHardware(AbstractHardware):
    """ Clauss head low-level hardware.
    """
    def _init(self):
        AbstractHardware._init(self)

        # Speed table with default walues.
        # On init, genuine values will be computed with max speed info.
        self.__speedTable = {'slow': 250,
                             'normal': 1125,
                             'fast': 2250
                         }

        # Number of steps for a full turn
        self.__encoderFullCircle = None

        # Used to memorize previous position while driving to position
        self.__drivePos = 0

        # Used to know if it's moving
        self.__firstMove = False

        # Usefull for first manual mode
        self.__firstJog = False

    def __encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        #Logger().debug("ClaussHardware.encoderToAngle(): pos=%s, encoderFullCircle=%s" % (codPos, self.__encoderFullCircle))
        return -codPos * 360. / self.__encoderFullCircle

    def __angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: long
        """
        #Logger().debug("ClaussHardware.angleToEncoder(): pos=%s, encoderFullCircle=%s" % (pos, self.__encoderFullCircle))
        return int(-pos * self.__encoderFullCircle / 360.)

    def __toHex(self, cmd):
        """ Convert command to human readable hexa string for debugging.

        @param cmd: hardware command
        @type pos: string

        @return: hardware command, shown in hexa
        @rtype: string
        """
        hexStr = ""
        for i in range(len(cmd)):
            hexStr += "%02x " % ord(cmd[i])
        return hexStr

    def __sendCmd(self, cmd, element=0, cr=1, param=""):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @param element: element ID (0 for transceiver, 1 for motor H, 2 for motor V)
        @type element: int

        @param cr: number of CR normally returned.
        @type cr: int

        @param param: additionnal parameter
        @type param: str

        @return: answer
        @rtype: str
        """

        # Append 'c' and element number to a single hexa value
        hexQuery = "0x%c%d" % ('c', element)
        hexPredictedAnswer = "0x%c%d" % ('a', element)

        # Create command, ended by CR.
        hexcmd = "%c%c%s%c" % (int(hexQuery, 16), cmd, param, '\r')

        for nbTry in xrange(self._nbRetry):
            try:
                self._driver.empty()
                self._driver.write(hexcmd)

                answer = ""
                crCount = 1
                begin = False
                magic = False

                while True:
                    c = self._driver.read(1)

                    # Valid answer, processing
                    if ord(c) == int(hexPredictedAnswer, 16) and not begin:
                         magic = True
                         begin = True
                         continue

                    # Valid answer, processing
                    elif ord(c) == int(hexPredictedAnswer, 16) and begin:
                        magic = True
                        continue

                    # Invalid value, waiting answer pattern
                    elif ord(c) != int(hexPredictedAnswer, 16) and not begin:
                        continue

                    # Verifying validity of answer
                    elif c == cmd and magic:
                        magic = False

                        # For short command with 1 CR, just return an ack.
                        if cr == 1:
                            answer += c
                        continue

                    # Correct number of CR : end of processing
                    elif c == '\r' and crCount == cr:
                        break

                    # CR
                    elif c == '\r':
                        crCount += 1

                    # Usefull char for answer
                    elif crCount == cr:
                        answer += c

            except (IOError, HardwareError):
                Logger().exception("ClaussHardware.__sendCmd()")
                Logger().warning("ClaussHardware.__sendCmd(): Can't sent command %s to element %d. Retrying..." % (repr(cmd), element))
            else:
                break
        else:
            raise HardwareError("Can't send command %s to element %d" % (repr(cmd), element))

        #Logger().debug("ClaussHardware.__sendCmd(): element=%d, ans=%s" % (element, repr(answer)))

        # empty ignored part of actual answer
        #self._driver.empty()
        return answer

    def init(self):
        #self._driver.setTimeout(0.1)

        # Only initialize if we have yaw or pitch, not shutter class
        if self._axis != 0:
            self._driver.acquireBus()
            try:

                # Rodeon head also had a transceiver to initialize. Do it before anything.
                # When done, don't initialize twice...
                if self._axis == 1:

                    # Reset transceiver twice
                    value = self.__sendCmd("R", 0)

                    # Is transceiver answering to reset order?
                    if len(value) == 0:
                        raise HardwareError("No answer at all. Check baudrate (must be 19200, not 9600). Stopping...")

                    elif value == 'R':

                        # Good answer
                        Logger().debug("ClaussHardware.init(): Transceiver answer successfully to reset order")

                    else:

                        # No, probably bad serial or hardware
                        raise HardwareError("Is it a Clauss hardware? I can't talk with it. Stopping...")

                    # Get brand
                    value = self.__sendCmd("m", 0, 2, "")
                    if value != "CLAUSS":

                        # Retry...
                        Logger().debug("ClaussHardware.init(): BRAND ERROR. Retrying...")
                        value = self.__sendCmd("m", 0, 2, "")
                        if value != "CLAUSS":
                            raise HardwareError("'%s' is not a Clauss head. Stopping..." % value)
                    Logger().debug("ClaussHardware.init(): Transceiver brand=%s" % value)
                    value = self.__sendCmd("w", 0, 2, "")
                    Logger().debug("ClaussHardware.init(): Transceiver reference number=%s" % value)
                    value = self.__sendCmd("v", 0, 2, "")
                    Logger().debug("ClaussHardware.init(): Transceiver firmware version=%s" % value)

                # Reset motor
                self.__sendCmd("R", self._axis)

                # Go to factory position 0°
                self.__sendCmd("Y", self._axis)

                # Get reference number transceiver
                value = self.__sendCmd("w", self._axis, 2, "")
                Logger().debug("ClaussHardware.init(): axis=%d, motor reference number=%s" % (self._axis, value))

                # Get brand
                value = self.__sendCmd("m", self._axis, 2, "")
                if value != "CLAUSS":
                    raise HardwareError("ClaussHardware.init(): '%s' is not a Clauss head, stopping..." % value)
                Logger().debug("ClaussHardware.init(): axis=%d, motor brand=%s" % (self._axis, value))

                # Get firmware version
                value = self.__sendCmd("v", self._axis, 2, "")
                Logger().debug("ClaussHardware.init(): axis=%d, motor firmware version=%s" % (self._axis, value))

                # Get number of steps
                value = self.__sendCmd("u", self._axis, 2, "")
                self.__encoderFullCircle = int(value)
                Logger().debug("ClaussHardware.init(): axis=%d, encoderFullCircle=%s" % (self._axis, value))

                # Get max speed
                value = int(self.__sendCmd("f", self._axis, 2))
                Logger().debug("ClaussHardware.init(): axis=%d, motor max speed=%s" % (self._axis, value))

                # Formatting speed to Clauss as needed
                self.__speedTable['slow'] = int(value / 12.)
                self.__speedTable['normal'] = int(value / 2.66)
                self.__speedTable['fast'] = int(value / 1.33)
                Logger().debug("ClaussHardware.init(): axis=%d, speed : slow=%s, normal=%s, fast=%s (max speed is %d)" % (self._axis, self.__speedTable['slow'], self.__speedTable['normal'], self.__speedTable['fast'], value))

                # Unknow command
                self.__sendCmd("a", self._axis, 2, "")

                # Wait motor to reach 0° position (issued by command Y)
                while self.isMoving():
                    time.sleep(1)
                    Logger().debug("ClaussHardware.init(): axis=%d, motor is still moving. Waiting..." % self._axis)

                # Reset position to 0°
                self.__sendCmd("N", self._axis)

                # Acheive initialisation with this unknow commands for transceiver...
                # Do it after anything.
                if self._axis == 2:
                    Logger().debug("ClaussHardware.init(): axis=%d, finalizing transceiver init" % self._axis)
                    self.__sendCmd("L", 0, 1, "00")
                    self.__sendCmd("L", 0, 1, "10")
                    self.__sendCmd("L", 0, 1, "20")
                    self.__sendCmd("L", 0, 1, "30")
                    self.__sendCmd("L", 0, 1, "40")
                    self.__sendCmd("L", 0, 1, "50")
                    self.__sendCmd("L", 0, 1, "60")
                    self.__sendCmd("L", 0, 1, "70")
                    self.__sendCmd("L", 0, 1, "80")
                    self.__sendCmd("L", 0, 1, "90")
                    Logger().debug("ClaussHardware.init(): axis=%d, init done" % self._axis)

                    if self.isOnBattery():
                        Logger().debug("ClaussHardware.init(): Clauss head is on battery (%d)" % self.checkBattery())
                    else:
                        Logger().debug("ClaussHardware.init(): Clauss head is on AC power")
            finally:
                self._driver.releaseBus()

    def shutdown(self, parkHead=True):
        self._driver.acquireBus()
        try:
            if self._axis == 2 and parkHead:
                 self.drive(-90., self.__speedTable['fast'])
            else:
                 self.drive(0., self.__speedTable['fast'])
        finally:
            self._driver.releaseBus()

    def indexToSpeed(self, index):
        """ Return the speed at given index.

        @param index: index of the speed, in ('slow', 'normal', 'fast')
        @type: str

        @return: speed
        @rtype: float
        """
        return self.__speedTable[index]

    def read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            value = self.__sendCmd("p", self._axis, 2, "")
            #Logger().debug("ClaussHardware.drive(): axis=%d, value(%d)=%s" % (self._axis, len(value), value))

        finally:
            self._driver.releaseBus()

        #Sometimes, Rodeon head answer a break value (b0) instead of head position. Catch it.
        try:
            pos = self.__encoderToAngle(long(value))
        except ValueError:
            return self.__drivePos

        return pos

    def drive(self, pos, speed):
        """ Drive the axis (auto mode).

        @param pos: position to reach, in °
        @type pos: float

        @param speed: drive speed
        @type: int
        """
        strPos = "%+08d" % self.__angleToEncoder(pos)
        strSpeed = "%05d" % speed
        Logger().debug("ClaussHardware.drive(): axis=%d, pos=%d, encoded=%s, speed=%s" % (self._axis, pos, strPos, strSpeed))
        self._driver.acquireBus()
        try:

            # Drive to given position
            self.__sendCmd("S", self._axis, 1, strPos)

            # Define motor speed
            self.__sendCmd("F", self._axis, 1, strSpeed)

            # Goto position
            self.__sendCmd("G", self._axis, 1, "0")
        finally:
            self._driver.releaseBus()

    def stop(self):
        """ Stop the axis, when moving on manual mode.
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd("O", self._axis, 1, "3")
        finally:
            self._driver.releaseBus()

    def isMoving(self):
        acPos = 0.
        if not self.__firstMove:
            self.__drivePos = self.read()
            #Logger().debug("ClaussHardware.isMoving(): firstMove(%d) %d" % (self._axis, self.__drivePos))
            self.__firstMove = True
            return True

        else:
            acPos = self.read()
            if acPos != self.__drivePos:
                self.__drivePos = acPos
                #Logger().debug("ClaussHardware.isMoving(): Still moving(%d), acPos=%s, drivePos=%s" % (self._axis, acPos, self.__drivePos))
                return True

            else:
                self.__drivePos = acPos
                self.__firstMove = False
                #Logger().debug("ClaussHardware.isMoving(): not moving(%d), acPos=%s, drivePos=%s" % (self._axis, acPos, self.__drivePos))
                return False

    def startJog(self, dir_, speed, maxPos):
        """ Start the axis, to move on manual mode

        @param dir_: direction ('+', '-')
        @type dir_: str

        @param speed: speed
        @type speed: int

        @param maxPos: maximal position to reach, defined by high/low limit
        @type maxPos: float
        """
        Logger().debug("ClaussHardware.startJog(): axis=%d, dir=%c, speed=%s, maxPos=%s" % (self._axis, dir_, speed, maxPos))

        self._driver.acquireBus()
        try:
            if dir_ == '-':
                dir_ = '+'
            else:
                dir_ = '-'
            strPos = "%c%07d" % (dir_, self.__angleToEncoder(maxPos))
            Logger().debug("ClaussHardware.startJog(): Encoded request=%s" % strPos)

            # Jog to given position
            self.__sendCmd("S", self._axis, 1, strPos)

            # Define motor speed
            strSpeed = "%05d" % speed
            self.__sendCmd("F", self._axis, 1, strSpeed)

            # Unknow commands
            if not self.__firstJog:
                if self._axis == 1:
                    self.__sendCmd("I", self._axis, 1, "2")
                elif self._axis == 2:
                    self.__sendCmd("I", self._axis, 1, "9")
                self.__sendCmd("J", self._axis, 1, "9")
                self.__sendCmd("A", self._axis, 1, "00010")
                self.__firstJog = True

            # Go to position
            if self._axis == 1:
                self.__sendCmd("G", self._axis, 1, "1")
            elif self._axis == 2:
                self.__sendCmd("G", self._axis, 1, "0")
        finally:
            self._driver.releaseBus()

    def isOnBattery(self):
        """ Check if head is plugged on AC power.

        @return: True if head is on batteries
        @rtype: bool
        """
        value = self.__sendCmd("x", 0, 2, "")
        value = value[value.find('x') + 1:]
        if int(value) != 125:
            return True
        else:
            return False

    def checkBattery(self):
        """ Check battery state.

        @return: Battery state, in range(0, 100)
        @rtype: int
        """
        value = self.__sendCmd("x", 0, 2, "")
        value = value[value.find('x') + 1:]
        value = int(value)
        if value >= 100:
            value = 100

        return value

    def setShutter(self, state):
        """ Set output state.

        AF is autofocus (pin 3-4 connected)
        ON is AF + shutter (pin 3-4 and 5-6 connected)
        OFF is release all (no pin connected)

        @param state: new state of the the output, in (AF, ON, OFF)
        @type state: str
        """
        self._driver.acquireBus()
        try:
            Logger().debug("ClaussHardware.setShutter(): %s" % state)
            if state == "OFF":
                self.__sendCmd("L", 0, 1, "00")
                self.__sendCmd("L", 0, 1, "10")
                self.__sendCmd("L", 0, 1, "00")
                self.__sendCmd("L", 0, 1, "10")
            elif state == "AF":
                self.__sendCmd("L", 0, 1, "01")
            elif state == "ON":
                self.__sendCmd("L", 0, 1, "11")
        finally:
            self._driver.releaseBus()
