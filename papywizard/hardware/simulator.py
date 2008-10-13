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

Complete simulation of the Merlin/Orion head protocole.
This simulator can be use to check all low-level messages
between Papywizard and the head.

Implements
==========

- MerlinOrionBaseHandler
- MerlinOrionEthernetHandler
- MerlinOrionSerialHandler
- MerlinOrionBaseSimulator
- SimulatorTCPServer
- MerlinOrionEthernetSimulator
- MerlinOrionSerialSimulator

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: serialDriver.py 557 2008-09-18 18:51:24Z fma $"

import SocketServer

import serial
#import bluetooth

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
            raise HardwareError("Invalid command format (%s)" % repr(cmdStr))

        # Split cmdStr
        cmd = cmdStr[1]
        numAxis = int(cmdStr[2])
        if numAxis not in (1, 2):
            raise HardwareError("Invalid axis number (%d)" % numAxis)
        param = cmdStr[3:-1]
        Logger().debug("MerlinOrionBaseHandler._handleCmd(): cmdStr=%s, cmd=%s, numAxis=%d, param=%s" % (repr(cmdStr), cmd, numAxis, param))

        # Compute command response
        response = ""

        # Stop command
        if cmd == 'L':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): stop")
            self._axis[numAxis].stop()
            response = ""

        # ??? command
        elif cmd == 'F':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): ???")

        # ??? command
        elif cmd == 'a':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): ???")

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

        # speed command
        elif cmd == 'I':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): speed")
            try:
                speed = decodeAxisValue(param)
                Logger().debug("MerlinOrionBaseHandler._handleCmd(): axis %d speed=%d" % (numAxis, speed))
                self._axisSpeed[numAxis] = speed
            except KeyError:
                raise HardwareError("No direction has been set")

        # position command
        elif cmd == 'S':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): position")
            self._axisPos[numAxis] = cod2deg(decodeAxisValue(param))

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
            except KeyError:
                raise HardwareError("Missing one axis cmd/direction/speed value")

        # shutter command
        elif cmd == 'O':
            Logger().trace("MerlinOrionBaseHandler._handleCmd(): shutter")

        else:
            raise HardwareError("Invalid command")

        return "=%s\r" % response


class MerlinOrionBluetoothHandler(MerlinOrionBaseHandler):
    """ Bluetooth-based handler.
    """
    def __init__(self, serial):
        raise NotImplementedError


class MerlinOrionSerialHandler(MerlinOrionBaseHandler):
    """ Serial-based handler.
    """
    def __init__(self, serial):
        super(MerlinOrionSerialHandler, self).__init__()
        self.serial = serial

    def handle(self):
        Logger().info("New serial connection established")
        while True:
            try:
                cmd = ""
                while not cmd.endswith('\r'):
                    data = self.serial.read(1)
                    #Logger().debug("MerlinOrionSerialHandler.handle(): data=%s" % repr(data))
                    if not data:
                        Logger().error("Timeout while reading on serial bus")
                        break
                    cmd += data
                if cmd:
                    response = self._handleCmd(cmd)
                    Logger().debug("MerlinOrionSerialHandler.handle(): response=%s" % repr(response))
                    self.serial.write(response)
                else:
                    #self.serial.close()
                    Logger().debug("MerlinOrionSerialHandler.handle(): lost connection")
                    Logger().info("Serial connection closed")
                    break
            except KeyboardInterrupt:
                #self.serial.close()
                Logger().info("Serial connection closed")
                raise
            except:
                Logger().exception("MerlinOrionSerialHandler.handle()")


class MerlinOrionEthernetHandler(MerlinOrionBaseHandler, SocketServer.BaseRequestHandler):
    """ Ethernet-based handler.
    """
    def __init__(self, *args, **kwargs):
        MerlinOrionBaseHandler.__init__(self)
        SocketServer.BaseRequestHandler.__init__(self, *args, **kwargs)

    def handle(self):
        Logger().debug("MerlinOrionEthernetHandler.handle(): connection request from ('%s', %d)" % self.client_address)
        Logger().info("New ethernet connection established")
        while True:
            try:
                cmd = ""
                while not cmd.endswith('\r'):
                    data = self.request.recv(1)
                    if not data: # connection lost?
                        Logger().error("Can't read data from ethernet")
                        break
                    cmd += data
                if cmd:
                    response = self._handleCmd(cmd)
                    Logger().debug("MerlinOrionEthernetHandler.handle(): response=%s" % repr(response))
                    self.request.sendall(response)
                else:
                    self.request.close()
                    Logger().debug("MerlinOrionEthernetHandler.handle(): lost connection with ('%s', %d)" % self.client_address)
                    Logger().info("Ethernet connection closed")
                    break
            except KeyboardInterrupt:
                self.request.close()
                Logger().info("Ethernet connection closed")
                break
            except:
                Logger().exception("MerlinOrionEthernetHandler.handle()")


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


class MerlinOrionBluetoothSimulator(MerlinOrionBaseSimulator):
    """ Bluetooth-based simulator.
    """
    def __init__(self):
        raise NotImplementedError


class MerlinOrionSerialSimulator(MerlinOrionBaseSimulator):
    """ Serial-based simulator.
    """
    def __init__(self, port):
        self.__port = port
        super(MerlinOrionSerialSimulator, self).__init__()

    def _init(self):
        self.__serial = serial.Serial(self.__port)
        self.__serial.timeout = 5. # This force the server to close the connection
                                   # after a while.The timeout must be greater than
                                   # the spy refresh value (~ 0.5 s)

    def run(self):

        # Empty serial buffer
        self.__serial.read(self.__serial.inWaiting())
        try:
            while True:
                if self.__serial.inWaiting():
                    handler = MerlinOrionSerialHandler(self.__serial)
                    handler.handle()
        except KeyboardInterrupt:
            pass


class SimulatorTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        Logger().error("Error while handling request from ('%s', %d)" % client_address)


class MerlinOrionEthernetSimulator(MerlinOrionBaseSimulator):
    """ Ethernet-based simulator.
    """
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        super(MerlinOrionEthernetSimulator, self).__init__()

    def _init(self):
        self.__server = SimulatorTCPServer((self.__host, self.__port), MerlinOrionEthernetHandler)
        self.__server.socket.settimeout(1.)

    def run(self):
        try:
            self.__server.serve_forever()
        except KeyboardInterrupt:
            pass
