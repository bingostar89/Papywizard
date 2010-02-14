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

Complete simulation of the GigaPanBot head protocole.
This simulator can be use to check all low-level messages
between Papywizard and the head.

Implements
==========

- GigaPanBotCommandDispatcherObject
- GigaPanBotCommandDispatcher

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore

from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.plugins.simulationPlugins import SimulationAxis

ENCODER_ZERO = 0x800000
ENCODER_FULL_CIRCLE = 0xE62D3

panoguyCommandDispatcher = None


class GigaPanBotCommandDispatcherObject(QtCore.QObject):
    """ Abstract handler for GigaPanBot commands set.
    """
    def __init__(self):
        """ Init the abstract handler.
        """
        QtCore.QObject.__init__(self)
        yawAxis = SimulationAxis('yawAxis', "Simulation")
        pitchAxis = SimulationAxis('pitchAxis', "Simulation")
        yawAxis.activate()
        pitchAxis.activate()
        self._axis = {1: yawAxis,
                      2: pitchAxis}
        self._axisCmd = {}
        self._axisPos = {}

    def activate(self):
        """ Activate threads.
        """
        self._axis[1].activate()
        self._axis[2].activate()

    def deactivate(self):
        """ Deactivate threads.
        """
        self._axis[1].deactivate()
        self._axis[2].deactivate()

    def _decodeAxisValue(self, strValue):
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

    def _encodeAxisValue(self, value):
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

    def _encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        return (codPos - ENCODER_ZERO) * 360. / ENCODER_FULL_CIRCLE  # Use dynamic value

    def _angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: int
        """
        return int(pos * ENCODER_FULL_CIRCLE / 360. + ENCODER_ZERO)  # Use dynamic value

    def handleCmd(self, cmdStr):
        """ Handle a command.

        @param cmdStr: command to simulate
        @type cmdStr: str

        @return: response
        @rtype: str

        raise HardwareError: wrong command
        """
        Logger().debug("GigaPanBotBaseHandler.handleCmd(): cmdStr=%s" % cmdStr)
        if not cmdStr.startswith(':'):
            raise HardwareError("Invalid command format (%s)" % repr(cmdStr))

        # Split cmdStr
        cmd = cmdStr[1]
        numAxis = int(cmdStr[2])
        if numAxis not in (1, 2):
            raise HardwareError("Invalid axis number (%d)" % numAxis)
        param = cmdStr[3:-1]
        Logger().debug("GigaPanBotBaseHandler.handleCmd(): cmdStr=%s, cmd=%s, numAxis=%d, param=%s" % (repr(cmdStr), cmd, numAxis, param))

        # Compute command response
        response = ""

        # Stop command
        if cmd == 'L':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): stop")
            self._axis[numAxis].stop()
            response = ""

        # Get encoder full circle command
        elif cmd == 'a':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): get encoder full circle")
            response =  self._encodeAxisValue(self._angleToEncoder(0xE62D3))

        # Get firmeware version command
        elif cmd == 'e':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): get firmware version?")
            response = "Vx.x"

        # Read command
        elif cmd == 'j':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): read")
            pos = self._axis[numAxis].read()
            response = self._encodeAxisValue(self._angleToEncoder(pos))

        # Status command
        elif cmd == 'f':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): status")
            if self._axis[numAxis].isMoving():
                response = "1"
            else:
                response = "0"

        # Start jog command
        elif cmd == 'G':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): start jog")
            #self._axisCmd[numAxis] = 'jog'
            if param == '0':
                dir_ = '+'
            elif param == '1':
                dir_ = '-'
            else:
                raise HardwareError("Invalid param")
            self._axis[numAxis].startJog(dir_)
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): axis %d direction=%s" % (numAxis, dir_))

        # Goto command
        elif cmd == 'S':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): goto")
            self._axis[numAxis].drive(self._encoderToAngle(self._decodeAxisValue(param)), wait=False)

        # Speed command
        elif cmd == 'I':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): speed")
            speed = int(param)
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): axis %s speed=%d" % (numAxis, speed))

        # Output command
        elif cmd == 'O':
            Logger().debug("GigaPanBotBaseHandler.handleCmd(): output")

        # Invalid command
        else:
            raise HardwareError("Invalid command")

        return "=%s\r" % response


# Command dispatcher factory
def GigaPanBotCommandDispatcher(model=None):
    global panoguyCommandDispatcher
    if panoguyCommandDispatcher is None:
        panoguyCommandDispatcher = GigaPanBotCommandDispatcherObject()

    return panoguyCommandDispatcher
