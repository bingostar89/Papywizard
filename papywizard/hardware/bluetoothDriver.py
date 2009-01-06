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

- BluetoothDriver

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import bluetooth

from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.hardware.busDriver import BusDriver


class BluetoothDriver(BusDriver):
    """ Driver for bluetooth connection.

    This driver only uses bluetooth socket.
    """
    def init(self):
        if not self._init:
            address = ConfigManager().get('Preferences', 'HARDWARE_BLUETOOTH_DEVICE_ADDRESS')
            Logger().debug("BluetoothDriver.init(): trying to connect to %s..." % address)
            try:
                #import time
                #time.sleep(3)
                self.setDeviceAddress(address)
                self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self._sock.connect((self.__deviceAddress, 1))
                try:
                    self._sock.settimeout(1.)
                except NotImplementedError:
                    Logger().warning("BluetoothDriver.init(): bluetooth stack does not implment settimeout()")
                self._init = True
            except bluetooth.BluetoothError, error:
                Logger().exception("BluetoothDriver.init()")
                err, msg = eval(error.message)
                raise HardwareError(msg)
            except Exception, msg:
                Logger().exception("BluetoothDriver.init()")
                raise HardwareError(str(msg))
            else:
                Logger().debug("BluetoothDriver.init(): successfully connected to %s" % address)

    def shutdown(self):
        if self._init:
            self._sock.close()
            self._init = False

    def setDeviceAddress(self, address):
        """ Set the address of the device to connect to.

        @param address: address of the device
        @type address: str
        """
        self.__deviceAddress = address

    def discoverDevices(self):
        """ Discover bluetooth devices.

        @return: devices addresses and names
        @rtype: list of tuple
        """
        return bluetooth.discover_devices(lookup_names=True)

    def sendCmd(self, cmd):
        """
        @todo: see how to empty buffer.
        """
        #Logger().debug("BluetoothDriver.sendCmd(): cmd=%s" % cmd)
        if not self._init:
            raise HardwareError(_("Bluetooth driver not initialized"))

        self.acquireBus()
        try:
            # Empty buffer
            #self._sock.read(self._sock.inWaiting())

            self._sock.send(":%s\r" % cmd)
            c = ''
            while c != '=':
                c = self._sock.recv(1)
                #Logger().debug("BluetoothDriver.sendCmd(): c=%s" % repr(c))
                if not c:
                    raise IOError(_("Timeout while reading on bluetooth bus"))
            data = ""
            while True:
                c = self._sock.recv(1)
                #Logger().debug("BluetoothDriver.sendCmd(): c=%s, data=%s" % (repr(c), repr(data)))
                if not c:
                    raise IOError(_("Timeout while reading on bluetooth bus"))
                elif c == '\r':
                    break
                data += c

        finally:
            self.releaseBus()

        return data
