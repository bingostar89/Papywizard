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

Tests

Implements
==========

- MerlinOrionHandler
- Simulator

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: serialDriver.py 557 2008-09-18 18:51:24Z fma $"

import SocketServer

import serial
import bluetooth

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.common.helpers import decodeAxisValue, encodeAxisValue, deg2cod, cod2deg
from papywizard.hardware.head import HeadSimulation


class MerlinOrionBaseHandler(object):
    """ Abstract handler for Merlin/Orion commands set.
    """
    def __init__(self):
        """ Init the abstract handler.
        """
        super(MerlinOrionBaseHandler, self).__init__()
        self._head = HeadSimulation()
        self._axis = {1: self._head.yawAxis,
                      2: self._head.pitchAxis}
        self._axisCmd = {}
        self._axisDir = {}
        self._axisSpeed = {}
        self._axisPos = {}

    def _handleCmd(self, cmdStr):
        """ Handle a command.

        @param cmdStr: command to simulate
        @type cmdStr: str

        @return: response
        @rtype: str

        raise HardwareError: wrong command
        """
        if not cmdStr.startswith(':'):
            raise HardwareError("Invalid command format")

        # Split cmdStr
        cmd = cmdStr[1]
        numAxis = int(cmdStr[2])
        if numAxis not in (1, 2):
            raise HardwareError("Invalid axis number")
        param = cmdStr[3:-1]
        Logger().debug("MerlinOrionBaseHandler._handleCmd(): cmdStr=%s, cmd=%s, numAxis=%d, param=%s" % (repr(cmdStr), cmd, numAxis, param))

        # Compute command response
        # Stop command
        if cmd == 'L':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): stop")
            self._axis[numAxis].stop()
            response = ""

        # ??? command
        elif cmd == 'F':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): ???")
            response = ""

        # ??? command
        elif cmd == 'a':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): ???")
            response = "D3620E"

        # ??? command
        elif cmd == 'D':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): ???")
            response = "F90600"

        # read command
        elif cmd == 'j':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): read")
            pos = self._axis[numAxis].read()
            response = encodeAxisValue(deg2cod(pos))

        # status command
        elif cmd == 'f':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): status")
            if self._axis[numAxis].isMoving():
                response = "-1-"
            else:
                response = "-0-"

        # command command
        elif cmd == 'G':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): command")
            if param[0] == '0':
                self._axisCmd[numAxis] = 'drive'
            elif param[0] == '3':
                self._axisCmd[numAxis] = 'jog'
                if param[1] == '0':
                    self._axisDir[numAxis] = '+'
                elif param[1] == '1':
                    self._axisDir[numAxis] = '-'
                else:
                    raise HardwareError("Invalid param")
                Logger().debug("MerlinOrionBaseHandler._handleCmd(): axis %d direction=%s" % (numAxis, self._axisDir[numAxis]))
            else:
                raise NotImplementedError
            response = ""

        # speed command
        elif cmd == 'I':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): speed")
            try:
                speed = decodeAxisValue(param)
                Logger().debug("MerlinOrionBaseHandler._handleCmd(): axis %d speed=%d" % (numAxis, speed))
                self._axisSpeed[numAxis] = speed
                response = ""
            except KeyError:
                raise HardwareError("No direction has been set")

        # position command
        elif cmd == 'S':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): position")
            self._axisPos[numAxis] = cod2deg(decodeAxisValue(param))
            response = ""

        # run command
        elif cmd == 'J':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): run")
            try:
                if self._axisCmd[numAxis] == 'jog':
                    dir_ = self._axisDir[numAxis]
                    speed = self._axisSpeed[numAxis]
                    self._axis[numAxis].startJog(dir_)
                elif self._axisCmd[numAxis] == 'drive':
                    pos = self._axisPos[numAxis]
                    self._axis[numAxis].drive(pos, wait=False)
                response = ""
            except KeyError:
                raise HardwareError("Missing one axis cmd/direction/speed value")

        # shutter command
        elif cmd == 'O':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): shutter")
            response = ""

        else:
            raise HardwareError("Invalid command")

        return "=%s\r" % response


class MerlinOrionSocketHandler(MerlinOrionBaseHandler, SocketServer.BaseRequestHandler):
    """ Socket-based handler.
    """
    def __init__(self, *args, **kwargs):
        MerlinOrionBaseHandler.__init__(self)
        SocketServer.BaseRequestHandler.__init__(self, *args, **kwargs)

    def handle(self):
        Logger().debug("MerlinOrionHandler.handle(): connection request from ('%s', %d)" % self.client_address)
        Logger().info("New connection established")
        while True:
            try:
                cmd = ""
                while not cmd.endswith('\r'):
                    data = self.request.recv(1)
                    if not data: # connection lost?
                        Logger().error("MerlinOrionSocketHandler.handle(): can't read data")
                        break
                    cmd += data
                if cmd:
                    response = self._handleCmd(cmd)
                    Logger().debug("MerlinOrionHandler.handle(): response=%s" % repr(response))
                    self.request.sendall(response)
                else:
                    self.request.close()
                    Logger().debug("MerlinOrionHandler.handle(): lost connection with ('%s', %d)" % self.client_address)
                    Logger().info("Connection closed")
                    break
            except KeyboardInterrupt:
                self.request.close()
                Logger().info("Connection closed")
                break
            except:
                Logger().exception("MerlinOrionHandler.handle()")


class MerlinOrionBaseSimulator(object):
    """ Abstract Merlin/Orion simulator.
    """
    def __init__(self):
        """ Init the Merlin/Orion base simulator.
        """
        super(MerlinOrionBaseSimulator, self).__init__()
        self._init()

    def _init(self):
        """ Init the siumlator IO.
        """
        raise NotImplementedError

    def run(self):
        """ Run the simulator.
        """
        raise NotImplementedError


class MerlinOrionSocketSimulator(MerlinOrionBaseSimulator):
    """ Socket-based simulator.
    """
    class SimulatorTCPServer(SocketServer.TCPServer):
        allow_reuse_address = True

        def handle_error(self, request, client_address):
            Logger().error("Error while handling request=from ('%s', %d)" % client_address)

    def _init(self):
        self.__server = MerlinOrionSocketSimulator.SimulatorTCPServer(("localhost", config.SIMUL_SOCKET_PORT), MerlinOrionSocketHandler)
        self.__server.socket.settimeout(1.)

    def run(self):
        Logger().debug("Starting ocket-based simulator...")
        try:
            self.__server.serve_forever()
        except KeyboardInterrupt:
            Logger().debug("Socket-based simulator stopped")


class MerlinOrionSerialHandler(object):
    """ Serial-based handler.
    """
    def __init__(self):
        """ Init the base handler.
        """
        super(MerlinOrionBaseHandler, self).__init__()

    def handle(self):
        data = ""
        while True:
            data = self.__serial.read()
            if not data:
                raise IOError("Timeout while reading on serial bus")
            while data[-1] != '\r':
                c = self.__serial.read()
                if not c:
                    raise IOError("Timeout while reading on serial bus")
                else:
                    data += c


class MerlinOrionSerialSimulator(object):
    """ Serial-based simulator.
    """
    def _init(self):
        self.__serial = serial.Serial(config.DEFAULT_SERIAL_PORT)
        self.__serial.setBaudrate(config.SIMUL_SERIAL_BAUDRATE)
        self.__serial.setTimeout(1.)

    def run(self):
        """ Run the sniffer.

        Listen to the serial line and display commands/responses.
        """
        Logger().info("Serial-based simulator started")
        try:
            while True:
                data = self.__serial.read()
                if not data:
                    raise IOError("Timeout while reading on serial bus")
                while data[-1] != '\r':
                    c = self.__serial.read()
                    if not c:
                        raise IOError("Timeout while reading on serial bus")
                    else:
                        data += c
                if data[0] == ':':
                    cmd = data[1:-1]
                elif data[0] == '=':
                    resp = data[1:-1]
                    Logger().info("%10s -> %10s" % (cmd, resp))
                else:
                    Logger().debug("%s" % data[1:-1])
        except:
            Logger().exception("Serial-based simulator.run()")
            Logger().info("Serial-based simulator stopped")
