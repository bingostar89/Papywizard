# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- BluetoothDriver

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time

import bluetooth

from common import config
from common.loggingServices import Logger
from common.exception import HardwareError
from busDriver import BusDriver


class BluetoothDriver(BusDriver):
    """ Passive driver.
    
    This driver only uses bluetooth socket.
    
    @todo: dynamically get bluetooth device address.
    """
    def init(self):
        try:
            self.setDeviceAddress(config.BLUETOOTH_DEVICE_ADDRESS)
            self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self._sock.connect((self.__deviceAddress, 1))
            self._init = True
            
        except:
            Logger().exception("BluetoothDriver.init()")
            raise HardwareError("Can't init BluetoothDriver object")

    def shutdown(self):
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
        if not self._init:
            raise HardwareError("BluetoothDriver not initialized")

        self.acquireBus()
        try:
            # Empty buffer
            #self._sock.read(self._sock.inWaiting())
            
            self._sock.send(":%s\r" % cmd)
            c = ''
            while c != '=':
                #while not self._sock.inWaiting():
                    #time.sleep(0.01)
                c = self._sock.recv(1)
                #Logger().debug("BluetoothDriver.sendCmd(): c=%s" % repr(c))
                if not c:
                    raise IOError("Timeout while reading on bluetooth bus")
            data = ""
            while True:
                c = self._sock.recv(1)
                #Logger().debug("BluetoothDriver.sendCmd(): c=%s, data=%s" % (repr(c), repr(data)))
                if not c:
                    raise IOError("Timeout while reading on bluetooth bus")
                elif c == '\r':
                    break
                data += c

        finally:
            self.releaseBus()
            
        return data
