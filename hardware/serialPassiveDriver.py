# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- SerialPassiveDriver

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time

from common.loggingServices import Logger
from serialDriver import SerialDriver


class SerialPassiveDriver(SerialDriver):
    """ Passive driver.
    
    This driver only uses passive components.
    """
    def _setCS(self, level):
        self._serial.setRTS(level)
    
    def sendCmd(self, cmd):
        """
        
        @todo: first check if bus is free (CTS). Or in acquireBus()?
        """
        self.acquireBus()
        try:
            # Empty buffer
            self._serial.read(self._serial.inWaiting())
            
            self._setCS(0)
            self._serial.write(":%s\r" % cmd)
            c = ''
            while c != '=':
                c = self._serial.read()
                #Logger().debug("SerialPassiveDriver.sendCmd(): c=%s" % c)
                if not c:
                    raise IOError("Timeout while reading on serial bus")
            data = ""
            while True:
                c = self._serial.read()
                #Logger().debug("SerialPassiveDriver.sendCmd(): c=%s" % c)
                if not c:
                    raise IOError("Timeout while reading on serial bus")
                elif c == '\r':
                    break
                data += c

        finally:
            self._setCS(1)
            self.releaseBus()
            
        return data
