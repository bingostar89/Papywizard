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

Complete simulation of the Merlin/Orion head protocole.
This simulator can be use to check all low-level messages
between Papywizard and the head.

Implements
==========

- PixOrbCommandDispatcherObject
- PixOrbCommandDispatcher

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore

from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.plugins.simulationPlugins import SimulationAxis

ENCODER_FULL_CIRCLE = 1000000

pixOrbCommandDispatcher = None


class PixOrbCommandDispatcherObject(QtCore.QObject):
    """ Abstract handler for Merlin/Orion commands set.
    """
    def __init__(self):
        """ Init the abstract handler.
        """
        QtCore.QObject.__init__(self)
        yawAxis = SimulationAxis('yawAxis', "Simulation")
        pitchAxis = SimulationAxis('pitchAxis', "Simulation")
        yawAxis.activate()
        pitchAxis.activate()
        self._axis = {'B': yawAxis,
                      'C': pitchAxis,
                      'A': None
                      }

    def activate(self):
        """ Activate threads.
        """
        self._axis['B'].activate()
        self._axis['C'].activate()

    def deactivate(self):
        """ Deactivate threads.
        """
        self._axis['B'].deactivate()
        self._axis['C'].deactivate()

    def _encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        return codPos * 360. / ENCODER_FULL_CIRCLE

    def _angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: int
        """
        return int(pos * ENCODER_FULL_CIRCLE / 360.)

    def handleCmd(self, cmdStr):
        """ Handle a command.

        @param cmdStr: command to simulate
        @type cmdStr: str

        @return: answer
        @rtype: str

        raise HardwareError: wrong command
        """
        Logger().debug("PixOrbBaseHandler.handleCmd(): cmdStr=%s" % repr(cmdStr))

        # SIN-11 specific command
        if cmdStr.startswith('&'):
            time.sleep(5)  # Simulate SIN-11 scan
            answer = "ABC"
        else:

            # Split cmdStr
            controllerName = cmdStr[0]
            cmd = cmdStr[1]
            param = cmdStr[2:-1]
            if controllerName not in ('A', 'B', 'C'):
                #raise HardwareError("Invalid controller name (%s)" % controllerName)
                answer = "?%s#" % controllerName
            Logger().debug("PixOrbBaseHandler.handleCmd(): cmd=%s, controllerName=%s, param=%s" % (cmd, controllerName, param))
    
            # Compute command answer
            answer = ""
    
            # Stop command
            if cmd == '@':
                Logger().debug("PixOrbBaseHandler.handleCmd(): stop")
                self._axis[controllerName].stop()
    
            # read command
            elif cmd == 'Z':
                Logger().debug("PixOrbBaseHandler.handleCmd(): read")
                pos = self._axis[controllerName].read()
                answer = "%s% d" % (controllerName, self._angleToEncoder(pos))
    
            # Status command
            elif cmd == '^':
                Logger().debug("PixOrbBaseHandler.handleCmd(): status")
                if self._axis[controllerName].isMoving():
                    answer = "%s 1" % controllerName
                else:
                    answer = "%s 0" % controllerName
    
            # Initial Velocity command
            elif cmd == 'I':
                Logger().debug("PixOrbBaseHandler.handleCmd(): initial velocity")
                initVelocity = int(param)
                Logger().debug("PixOrbBaseHandler.handleCmd(): axis %s initVelocity=%d" % (controllerName, initVelocity))
    
            # Slew speed command
            elif cmd == 'V':
                Logger().debug("PixOrbBaseHandler.handleCmd(): slew speed")
                speed = int(param)
                Logger().debug("PixOrbBaseHandler.handleCmd(): axis %s speed=%d" % (controllerName, speed))
    
            # Ramp command
            elif cmd == 'K':
                Logger().debug("PixOrbBaseHandler.handleCmd(): ramp")
                param1, param2 = param.split()
                accel = int(param1)
                decel = int(param2)
                Logger().debug("PixOrbBaseHandler.handleCmd(): axis %s accel=%d decel=%d" % (controllerName, accel, decel))
    
            # Divider command
            elif cmd == 'D':
                Logger().debug("PixOrbBaseHandler.handleCmd(): divider")
                divider = int(param)
                Logger().debug("PixOrbBaseHandler.handleCmd(): axis %s divider=%d" % (controllerName, divider))
    
            # Drive command
            elif cmd == 'R':
                Logger().debug("PixOrbBaseHandler.handleCmd(): drive")
                pos = self._encoderToAngle(int(param))
                self._axis[controllerName].drive(pos, wait=False)
    
            # Jog command
            elif cmd == 'M':
                Logger().debug("PixOrbBaseHandler.handleCmd(): jog")
                speed = int(param)
                if speed > 0:
                    self._axis[controllerName].startJog('+')
                elif speed < 0:
                    self._axis[controllerName].startJog('-')
    
            # Shutter command
            elif cmd == 'A':
                Logger().debug("PixOrbBaseHandler.handleCmd(): shutter")
    
            # Wait command
            elif cmd == 'A':
                Logger().debug("PixOrbBaseHandler.handleCmd(): wait")
                while self._axis[controllerName].isMoving():
                    time.sleep(0.1)
    
            # Invalid command
            else:
                #raise HardwareError("Invalid command")
                answer = "#"  # Or only '\n'?

        return "%s\n\r" % answer


# Command dispatcher factory
def PixOrbCommandDispatcher(model=None):
    global pixOrbCommandDispatcher
    if pixOrbCommandDispatcher is None:
        pixOrbCommandDispatcher = PixOrbCommandDispatcherObject()

    return pixOrbCommandDispatcher
