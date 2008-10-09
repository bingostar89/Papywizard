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


class MerlinOrionBaseHandler(object):
    """ Abstract handler for Merlin/Orion commands set.
    """
    def __init__(self, *args, **kwargs):
        """ Init the abstract handler.
        """
        super(MerlinOrionBaseHandler, self).__init__()

    def _handleCmd(self, cmd):
        """ Handle a command.

        @param cmd: commande to simulate
        @type cmd: str

        @return: response
        @rtype: str

        raise HardwareError: wrong command
        """
        Logger().debug("MerlinOrionBaseHandler._handleCmd(): cmd=%s" % (repr(cmd)))
        if not cmd.startswith(':'):
            raise HardwareError("Invalid command format")

        return "=\r"


class MerlinOrionSocketHandler(SocketServer.BaseRequestHandler, MerlinOrionBaseHandler):
    """ Socket-based handler.
    """
    def __init__(self, *args, **kwargs):
        super(MerlinOrionSocketHandler, self).__init__(*args, **kwargs)

    def handle(self):
        Logger().debug("MerlinOrionHandler.handle(): connection request from ('%s', %d)" % self.client_address)
        Logger().info("New connection established")
        while True:
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

    handle_error(request, client_address)
    """
    def _init(self):
        self.__server = SocketServer.TCPServer(("localhost", config.SIMUL_SOCKET_PORT), MerlinOrionSocketHandler)
        self.__server.socket.settimeout(1.)

    def run(self):
        Logger().info("Socket-based simulator started")
        try:
            self.__server.serve_forever()
        except KeyboardInterrupt:
            Logger().info("Socket-based simulator stopped")


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


def main():
    simulator = MerlinOrionSocketSimulator()
    simulator.run()


if __name__ == "__main__":
    main()
