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

 - PixOrbHardware

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.abstractHardware import AbstractHardware

ENCODER_FULL_CIRCLE = 1000000  # steps per turn
SPEED_TABLE = { 1: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider': 160},  #  1 rev/day
                2: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider':  80},  #  2 rev/day
                3: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider':  40},  #  6 rev/day
                4: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':  20},  #  1 rev/h
                5: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':  10},  #  2 rev/h
                6: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':   6},  #  5 rev/h
                7: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   5},  #  1 °/s
                8: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   4},  #  3 °/s
                9: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   3},  #  6 °/s
               10: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   1}   # 12 °/s
               }


class PixOrbHardware(AbstractHardware):
    """ PoxOrb hardware class.
    """
    def _encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        return codPos * 360. / ENCODER_FULL_CIRCLE

    def _angleToEncoder(self, position):
        """ Convert degres to encoder value.

        @param position: position, in °
        @type position: float

        @return: encoder position
        @rtype: int
        """
        return int(position / 360. * ENCODER_FULL_CIRCLE)

    def __sendCmd(self, cmd, axis):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @param table: controller name table to use for this command
        @type table: dict

        @return: answer
        @rtype: str
        """
        cmd = "%s%s" % (axis, cmd)
        #Logger().debug("PixOrbHardware.__sendCmd(): axis %s cmd=%s" % (axis, repr(cmd)))
        for nbTry in xrange(self._nbRetry):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write("%s\n" % cmd)
                c = ''
                while c != '\r':
                    c = self._driver.read(1)
                    if c in ('#', '!', '$'):
                        self._driver.read(2)  # Read last CRLF
                        raise IOError("Error on command '%s' (answer=%s)" % (cmd, answer))
                    else:
                        answer += c

            except IOError:
                Logger().exception("PixOrbHardware.__sendCmd")
                Logger().warning("PixOrbHardware.__sendCmd(): axis %s failed to send command '%s'. Retrying..." % (axis, cmd))
            else:
                answer = answer.strip()  # Remove final CRLF
                break
        else:
            raise HardwareError("Axis %s can't send command %s (answer=%s)" % (axis, repr(cmd), repr(answer)))
        #Logger().debug("PixOrbHardware.__sendCmd(): axis %s, ans=%s" % (axis, repr(answer)))

        return answer

    def setBreakAxis(self, axis):
        """ Set the break axis number
        """
        self.__breakAxis = axis

    def configure(self, speedIndex):
        """ Configure the PixOrb hardware.

        @param speedIndex: speed params table index
        @type speedIndex: int
        """
        Logger().debug("PixOrbHardware.configure(): speedIndex=%d" % speedIndex)
        self._driver.acquireBus()
        try:

            # Set initial velocity
            self.__sendCmd("I%d" % SPEED_TABLE[speedIndex]['initVelocity'], self._axis)

            # Set accel/decel
            self.__sendCmd("K%d %d" % (SPEED_TABLE[speedIndex]['accel'], SPEED_TABLE[speedIndex]['decel']), self._axis)

            # Set slew speed
            self.__sendCmd("V%d" % SPEED_TABLE[speedIndex]['slewSpeed'], self._axis)

            # Set divider
            self.__sendCmd("D%d" % SPEED_TABLE[speedIndex]['divider'], self._axis)
        finally:
            self._driver.releaseBus()

    def read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            answer = self.__sendCmd("Z", self._axis)
        finally:
            self._driver.releaseBus()
        value = answer[1:]
        position = self._encoderToAngle(int(value))
        #Logger().debug("PixOrbHardware.read(): position=%d" % position)

        return position

    def drive(self, position):
        """ Drive the axis.

        @param position: position to reach, in °
        @type position: float
        """
        Logger().debug("PixOrbHardware.drive(): position=%d" % position)
        self._driver.acquireBus()
        try:
            self.__sendCmd("R%+d" % self._angleToEncoder(position), self._axis)
        finally:
            self._driver.releaseBus()

    def wait(self):
        """ Wait until motion is complete.
        """
        Logger().trace("PixOrbHardware.wait()")
        self._driver.acquireBus()
        try:
            self.__sendCmd("W", self._axis)
        finally:
            self._driver.releaseBus()

    def stop(self):
        """ Stop the axis.
        """
        Logger().trace("PixOrbHardware.stop()")
        self._driver.acquireBus()
        try:
            self.__sendCmd("@", self._axis)
        finally:
            self._driver.releaseBus()

    def startJog(self, dir_, speedIndex):
        """ Start the axis.

        @param dir_: direction ('+', '-')
        @type dir_: str

        @param speed: speed
        @type speed: int
        """
        Logger().debug("PixOrbHardware.startJog(): dir_=%s, speed=%d" % (dir_, speedIndex))
        if dir_ not in ('+', '-'):
            raise ValueError("Axis %d dir. must be in ('+', '-')" % self._axis)
        self._driver.acquireBus()
        try:
            speed = SPEED_TABLE[speedIndex]['slewSpeed']
            self.__sendCmd("M%s%d" % (dir_, speed), self._axis)
        finally:
            self._driver.releaseBus()

    def releaseBreak(self):
        """ Release the (opional) break.
        """
        Logger().trace("PixOrbHardware.releaseBreak()")
        self._driver.acquireBus()
        try:
            self.__sendCmd("A8", self.__breakAxis)
        finally:
            self._driver.releaseBus()
        #time.sleep(.1)  # Ensure break is released

    def activateBreak(self):
        """ Release the (opional) break.
        """
        Logger().trace("PixOrbHardware.activateBreak()")
        self._driver.acquireBus()
        try:
            self.__sendCmd("A0", self.__breakAxis)
        finally:
            self._driver.releaseBus()

    def getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self._driver.acquireBus()
        try:
            answer = self.__sendCmd("^", self._axis)
        finally:
            self._driver.releaseBus()
        axis, status = answer.split()
        #Logger().debug("PixOrbHardware.startJog(): status=%s" % status)
        return status

    def setOutput(self, state):
        """ Set the output state.
        """
        self._driver.acquireBus()
        try:
            if state:
                self.__sendCmd("A8", self._axis)
            else:
                self.__sendCmd("A0", self._axis)
        finally:
            self._driver.releaseBus()
