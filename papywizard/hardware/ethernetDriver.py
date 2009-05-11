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

__revision__ = "$Id$"

import socket

from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.hardware.abstractDriver import AbstractDriver


class EthernetDriver(AbstractDriver):
    """ Driver for TCP ethernet connection.
    """
    def _init(self):
        host = ConfigManager().get('Plugins/HARDWARE_ETHERNET_HOST')
        port = ConfigManager().getInt('Plugins/HARDWARE_ETHERNET_PORT')
        Logger().debug("EthernetDriver._init(): trying to connect to %s:%d..." % (host, port))
        try:
            #import time
            #time.sleep(3)
            self.setDeviceHostPort(host, port)
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self.__host, self.__port))
            self._sock.settimeout(1.)
            self.empty()
        except Exception, msg:
            Logger().exception("EthernetDriver._init()")
            raise HardwareError(msg)
        else:
            Logger().debug("EthernetDriver._init(): successfully connected to %s:%d" % (host, port))

    def _shutdown(self):
        self._sock.close()

    def setDeviceHostPort(self, host, port):
        """ Set the host and port of the device to connect to.

        @param host: host of the ethernet device
        @type host: str

        @param port: port of the ethernet device
        @type port: int
        """
        self.__host = host
        self.__port = port

    def empty(self):
        pass

    def write(self, data):
        #Logger().debug("EthernetDriver.write(): data=%s" % repr(data))
        try:
            size = self._sock.send(data)
            if size != len(data) + 2:
                raise IOError("Failed to send data on ethernet")
            else:
                return size
        except socket.timeout:
            raise IOError("Timeout while writing on ethernet")
        except socket.error, msg:
            raise IOError(msg)

    def read(self, size):
        try:
            data = self._sock.recv(size)
            #Logger().debug("EthernetDriver.read(): data=%s" % repr(data))
            if not data:
                raise IOError("Connection lost")
            else:
                return data
        except socket.timeout:
            raise IOError("Timeout while reading on ethernet bus")
        except socket.error, msg:
            raise IOError(msg)
