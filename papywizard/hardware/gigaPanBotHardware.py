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

 - GigaPanBotHardware

GigaPanBot protocol
===================

The GigaPanBot protocol is based on the Merlin/Orion one. A command starts
with ':', and ends with '\r'. A command is made of 1 letter, followed by
the axis number (1 digit), and an optional param. Param format is either 1
simple digit (decimal), or a full value on 6 digits (hex).

When the GigaPanBot receives a command, it answers immediatly. The answer
starts with '=', and ends with '\r'.

An unknown or invalid command should return '!' followed by 1 digit for
the error code.

<nd> n digit (dec)
<nh> n digit (hex)
<s>  string

(In the following table, ':', '=' and '\r' chars are not shown).

Command                    Name                               Answer
L<axis(1d)>                Stop                               None
F<axis(1d)>                Check axis                         None
a<axis(1d)>                Get full circle encoder value      <value(6h)>
e<axis(1d)>                Get firmeware version              <version(s)> (6 chars maxi)
S<axis(1d)><pos(6h)>       Goto position                      None
j<axis(1d)>                Read position                      <pos(6h)>
f<axis(1d)>                Get status                         <status(1d)> (status 1=moving, 0=not moving)
G<axis(1d)><dir(1d)>       Start moving (dir 0=+, 1=-)        None
O<axis(1d)><state(1d)>     Output (state O=open, 1=close)     None
I<axis(1d)><speed(3h)>     Set manual speed                   None

(also see U{http://www.autopano.net/forum/p58659-yesterday-23-48-24#p58659}).

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


class GigaPanBotHardware(AbstractHardware):
    """ GigaPanBot low-level hardware.
    """
    def _init(self):
        AbstractHardware._init(self)
        self.__encoderFullCircle = None

    def __decodeAxisValue(self, strValue):
        """ Decode value from axis.

        Values (position, speed...) returned by axis are
        24bits-encoded strings, high byte first.

        @param strValue: value returned by axis
        @type strValue: str

        @return: value
        @rtype: int
        """
        value = eval("0x%s" % strValue)

        return value

    def __encodeAxisValue(self, value):
        """ Encode value for axis.

        Values (position, speed...) to send to axis must be
        24bits-encoded strings, high byte first.

        @param value: value
        @type value: int

        @return: value to send to axis
        @rtype: str
        """
        strHexValue = "000000%s" % hex(value)[2:]
        strValue = strHexValue[-6:]

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
        cmd = "%s%d%s" % (cmd, self._axis, param)
        #Logger().debug("GigaPanBotHardware.__sendCmd(): axis %d cmd=%s" % (self._axis, repr(cmd)))
        for nbTry in xrange(self._nbRetry):
            try:
                self._driver.empty()
                self._driver.write(":%s\r" % cmd)
                answer = ""
                while True:
                    c = self._driver.read(1)
                    #Logger().debug("GigaPanBotHardware.__sendCmd(): c=%s" % repr(c))
                    if c == '=':
                        continue
                    elif c == '!':
                        c = self._driver.read(1)  # Get error code
                        # Do we need to read an additional '\r', here?
                        raise IOError("Error in command %s (err=%s)" % (repr(cmd), repr(c)))
                    elif c == '\r':
                        break
                    else:
                        answer += c

            except IOError:
                Logger().exception("GigaPanBotHardware.__sendCmd")
                Logger().warning("GigaPanBotHardware.__sendCmd(): %s axis %d can't sent command %s. Retrying..." % (NAME, self._axis, repr(cmd)))
            else:
                break
        else:
            raise HardwareError("%s axis %d can't send command %s" % (NAME, self._axis, repr(cmd)))
        #Logger().debug("GigaPanBotHardware.__sendCmd(): axis %d ans=%s" % (self._axis, repr(answer)))

        return answer

    def init(self):
        """ Init the GigaPanBot hardware.

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
            Logger().debug("GigaPanBotHardware.init(): firmeware version=%s" % value)

            # Get encoder full circle
            value = self.__sendCmd("a")
            self.__encoderFullCircle = self.__decodeAxisValue(value)
            Logger().debug("GigaPanBotHardware.init(): full circle count=%s" % hex(self.__encoderFullCircle))

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
            self.__sendCmd("S", strValue)
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
            self._sendCmd("I", self.__encodeAxisValue(speed))
            if dir_ == '+':
                self.__sendCmd("G", "0")
            elif dir_ == '-':
                self.__sendCmd("G", "1")
            else:
                raise ValueError("Axis %d dir. must be in ('+', '-')" % self._axis)
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
