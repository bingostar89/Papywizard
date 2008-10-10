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

Hardware driver

Implements
==========

- EthernetDriver

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: bluetoothDriver.py 600 2008-09-21 21:02:48Z fma $"

import socket

from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.hardware.busDriver import BusDriver


class EthernetDriver(BusDriver):
    """ Driver for TCP ethernet connection.
    """
    def init(self):
        if not self._init:
            host = ConfigManager().get('Hardware', 'ETHERNET_HOST')
            port = ConfigManager().getInt('Hardware', 'ETHERNET_PORT')
            Logger().debug("EthernetDriver.init(): trying to connect to %s:%d..." % (host, port))
            try:
                #import time
                #time.sleep(3)
                self.setDeviceHostPort(host, port)
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.connect((self.__host, self.__port))
                self._sock.settimeout(1.)
                self._init = True
            except Exception, msg:
                Logger().exception("EthernetDriver.init()")
                raise HardwareError(msg)
            else:
                Logger().debug("EthernetDriver.init(): successfully connected to %s:%d" % (host, port))

    def shutdown(self):
        if self._init:
            self._sock.close()
            self._init = False

    def setDeviceHostPort(self, host, port):
        """ Set the host and port of the device to connect to.

        @param host: host of the ethernet device
        @type host: str

        @param port: port of the ethernet device
        @type port: int
        """
        self.__host = host
        self.__port = port

    def sendCmd(self, cmd):
        """
        @todo: see how to empty buffer.
        """
        #Logger().debug("EthernetDriver.sendCmd(): cmd=%s" % cmd)
        if not self._init:
            raise HardwareError("EthernetDriver not initialized")

        self.acquireBus()
        try:
            # Empty buffer
            #self._sock.read(self._sock.inWaiting())

            try:
                count = self._sock.send(":%s\r" % cmd)
            except socket.timeout:
                raise IOError("Timeout while writing on ethernet")
            except socket.error, msg:
                raise IOError(msg)
            if count != len(cmd) + 2:
                raise IOError("Failed to send data on ethernet")
            c = ''
            while c != '=':
                try:
                    c = self._sock.recv(1)
                    #Logger().debug("EthernetDriver.sendCmd(): c=%s" % repr(c))
                except socket.timeout:
                    raise IOError("Timeout while reading on ethernet")
                except socket.error, msg:
                    raise IOError(msg)
                if not c:
                    raise IOError("Connection lost")
            data = ""
            while True:
                try:
                    c = self._sock.recv(1)
                    #Logger().debug("EthernetDriver.sendCmd(): c=%s, data=%s" % (repr(c), repr(data)))
                except socket.timeout:
                    raise IOError("Timeout while reading on ethernet")
                except socket.error, msg:
                    raise IOError(msg)
                if not c:
                    raise IOError("Connection lost")
                if c == '\r':
                    break
                data += c

        finally:
            self.releaseBus()

        return data
