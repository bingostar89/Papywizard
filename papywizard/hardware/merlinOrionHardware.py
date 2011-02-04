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

 - MerlinOrionHardware

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore

from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.abstractHardware import AbstractHardware

ENCODER_ZERO = 0x800000


class MerlinOrionHardware(AbstractHardware):
    """ Merlin/Orion low-level hardware.
    """
    def _init(self):
        AbstractHardware._init(self)
        self.__encoderFullCircle = None

    def __decodeAxisValue(self, strValue):
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

    def __encodeAxisValue(self, value):
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
        cmd = ":%s%d%s\r" % (cmd, self._axis, param)
        #Logger().debug("MerlinOrionHardware.__sendCmd(): axis %d cmd=%s" % (self._axis, repr(cmd)))
        for nbTry in xrange(self._nbRetry):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write(cmd)
                c = ''
                while c not in ('=', '!'):
                    c = self._driver.read(1)
                    #Logger().debug("MerlinOrionHardware.__sendCmd(): c=%s" % repr(c))
                if c == '!':
                    c = self._driver.read(1) # Get error code
                    raise IOError("Error in command %s (err=%s)" % (repr(cmd), c))
                answer = ""
                while True:
                    c = self._driver.read(1)
                    #Logger().debug("MerlinOrionHardware.__sendCmd(): c=%s" % repr(c))
                    if c == '\r':
                        break
                    answer += c

            except IOError:
                Logger().exception("MerlinOrionHardware.__sendCmd")
                Logger().warning("MerlinOrionHardware.__sendCmd(): axis %d can't sent command %s. Retrying..." % (self._axis, repr(cmd)))
            else:
                break
        else:
            raise HardwareError("axis %d can't send command %s" % (self._axis, repr(cmd)))
        #Logger().debug("MerlinOrionHardware.__sendCmd(): axis %d ans=%s" % (self._axis, repr(answer)))

        return answer

    def init(self):
        """ Init the MerlinOrion hardware.

        Done only once per axis.
        """
        self._driver.acquireBus()
        try:

            # Stop motor
            self.__sendCmd("L")

            # Check motor?
            self.__sendCmd("F")

            # Get firmeware version
            value = self.__sendCmd("e")
            Logger().debug("MerlinOrionHardware.init(): firmeware version=%s" % value)

            # Get encoder full circle
            value = self.__sendCmd("a")
            self.__encoderFullCircle = self.__decodeAxisValue(value)
            Logger().debug("MerlinOrionHardware.init(): encoder full circle=%s" % hex(self.__encoderFullCircle))

            # Get sidereal rate
            value = self.__sendCmd("D")
            Logger().debug("MerlinOrionHardware.init(): sidereal rate=%s" % hex(self.__decodeAxisValue(value)))

        finally:
            self._driver.releaseBus()

    def read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            value = self.__sendCmd("j")
        finally:
            self._driver.releaseBus()
        pos = self.__encoderToAngle(self.__decodeAxisValue(value))
        return pos

    def drive(self, pos):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float
        """
        strValue = self.__encodeAxisValue(self.__angleToEncoder(pos))
        self._driver.acquireBus()
        try:
            self.__sendCmd("L")
            self.__sendCmd("G", "00")
            self.__sendCmd("S", strValue)
            self.__sendCmd("J")
        finally:
            self._driver.releaseBus()

    def stop(self):
        """ Stop the axis.
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd("L")
        finally:
            self._driver.releaseBus()

    def startJog(self, dir_, speed):
        """ Start the axis.

        @param dir_: direction ('+', '-')
        @type dir_: str

        @param speed: speed
        @type speed: int
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd("L")
            if dir_ == '+':
                self.__sendCmd("G", "30")
            elif dir_ == '-':
                self.__sendCmd("G", "31")
            else:
                raise ValueError("Axis %d dir. must be in ('+', '-')" % self._axis)
            self.__sendCmd("I", self.__encodeAxisValue(speed))
            self.__sendCmd("J")
        finally:
            self._driver.releaseBus()

    def getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self._driver.acquireBus()
        try:
            return self.__sendCmd("f")
        finally:
            self._driver.releaseBus()

    def setOutput(self, state):
        """ Set output state.

        @param state: new state of the the output
        @type state: bool
        """
        self._driver.acquireBus()
        try:
            self.__sendCmd("O", str(int(state)))
        finally:
            self._driver.releaseBus()
