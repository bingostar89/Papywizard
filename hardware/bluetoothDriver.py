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

from common.loggingServices import Logger
from busDriver import BusDriver

#bluetooth.discover_devices(lookup_names=True)

class BluetoothDriver(BusDriver):
    """ Passive driver.
    
    This driver only uses bluetooth socket.
    
    @todo: dynamically get bluetooth device address.
    """
    def _init(self):
        self._sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self._sock = sock.connect(("00:50:C2:58:55:B9", 1))

    def _setCS(self, level):
        pass
    
    def sendCmd(self, cmd):
        """
        
        @todo: see how to empty buffer.
        """
        self.acquireBus()
        try:
            # Empty buffer
            #self._sock.read(self._sock.inWaiting())
            
            self._setCS(0)
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
                c = self._sock.recv()
                #Logger().debug("BluetoothDriver.sendCmd(): c=%s, data=%s" % (repr(c), repr(data)))
                if not c:
                    raise IOError("Timeout while reading on bluetooth bus")
                elif c == '\r':
                    break
                data += c

        finally:
            self._setCS(1)
            self.releaseBus()
            
        return data
