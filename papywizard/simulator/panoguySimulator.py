# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
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

Complete simulation of the Panoguy head protocole.
This simulator can be use to check all low-level messages
between Papywizard and the head.

Implements
==========

- PanoguySerialHandler
- PanoguyEthernetHandler
- PanoguyBaseSimulator
- SimulatorTCPServer
- PanoguyEthernetSimulator
- PanoguySerialSimulator

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import SocketServer  # Use Qt classes

import serial
from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.simulator.panoguyCommandDispatcher import PanoguyCommandDispatcher
from papywizard.plugins.simulationPlugins import SimulationAxis


class PanoguySerialHandler(QtCore.QObject):
    """ Serial-based handler.
    """
    def __init__(self, serial):
        QtCore.QObject.__init__(self)
        self.serial = serial

    def handle(self):
        Logger().info("New serial connection established")
        while True:
            try:
                cmd = ""
                while not cmd.endswith('\r'):
                    data = self.serial.read(1)
                    #Logger().debug("PanoguySerialHandler.handle(): data=%s" % repr(data))
                    if not data:
                        Logger().error("Timeout while reading on serial bus")
                        break
                    cmd += data
                if cmd:
                    response = PanoguyCommandDispatcher().handleCmd(cmd)
                    Logger().debug("PanoguySerialHandler.handle(): response=%s" % repr(response))
                    self.serial.write(response)
                else:
                    #self.serial.close()
                    Logger().debug("PanoguySerialHandler.handle(): lost connection")
                    Logger().info("Serial connection closed")
                    break
            except KeyboardInterrupt:
                #self.serial.close()
                Logger().info("Serial connection closed")
                raise
            except:
                Logger().exception("PanoguySerialHandler.handle()")


class PanoguyEthernetHandler(SocketServer.BaseRequestHandler):
    """ Ethernet-based handler.
    """
    def handle(self):
        Logger().debug("PanoguyEthernetHandler.handle(): connection request from ('%s', %d)" % self.client_address)
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
                    response = PanoguyCommandDispatcher().handleCmd(cmd)
                    Logger().debug("PanoguyEthernetHandler.handle(): response=%s" % repr(response))
                    self.request.sendall(response)
                else:
                    self.request.close()
                    Logger().debug("PanoguyEthernetHandler.handle(): lost connection with ('%s', %d)" % self.client_address)
                    Logger().info("Ethernet connection closed")
                    break
            except KeyboardInterrupt:
                self.request.close()
                Logger().info("Ethernet connection closed")
                break
            except:
                Logger().exception("PanoguyEthernetHandler.handle()")


class PanoguyBaseSimulator(QtCore.QObject):
    """ Abstract Panoguy simulator.
    """
    def __init__(self):
        """ Init the Panoguy base simulator.
        """
        QtCore.QObject.__init__(self)
        self._init()

    def _init(self):
        """ Init the siumlator IO.
        """
        raise NotImplementedError

    def run(self):
        """ Run the simulator.
        """
        raise NotImplementedError


class PanoguySerialSimulator(PanoguyBaseSimulator):
    """ Serial-based simulator.
    """
    def __init__(self, port):
        Logger().debug("PanoguySerialSimulator.__init__(): port=%s" % port)
        self.__port = port
        PanoguyBaseSimulator.__init__(self)

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
                    handler = PanoguySerialHandler(self.__serial)
                    handler.handle()
        except KeyboardInterrupt:
            pass


class SimulatorTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        Logger().error("Error while handling request from ('%s', %d)" % client_address)


class PanoguyEthernetSimulator(PanoguyBaseSimulator):
    """ Ethernet-based simulator.
    """
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        PanoguyBaseSimulator.__init__(self)

    def _init(self):
        self.__server = SimulatorTCPServer((self.__host, self.__port), PanoguyEthernetHandler)
        self.__server.socket.setblocking(1)

    def run(self):
        try:
            self.__server.serve_forever()
        except KeyboardInterrupt:
            pass
