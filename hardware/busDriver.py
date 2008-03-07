# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- BusDriver

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import threading

from common.loggingServices import Logger
from common.exception import HardwareError


class BusDriver(object):
    """ Base (abstract) class for bus drivers.
    """
    def __init__(self):
        """ Init the object.
        """
        self._lock = threading.RLock()
        try:
            self._init()
            self._initHardware()
        except:
            Logger().exception("BusDriver.__init__()")
            raise HardwareError("Can't init BusDriver object")

    def _init(self):
        """ Init hardware dependencies.
        """
        raise NotImplementedError

    def _initHardware(self):
        """ Init the hardware.
        """
        #self._setCS(1)

    def _setCS(self, level):
        """ Set CS signal to specified level.
        
        @param level: level to set to CS signal
        @type level: int
        """
        raise NotImplementedError
    
    def sendCmd(self, cmd):
        """ Send a command over the serial line, and return the answer.
        
        @param cmd: command to send
        @type cmd: str
        
        @return: answer
        @rtype: str
        """
        raise NotImplementedError
        
    def acquireBus(self):
        """ Acquire and lock the bus.
        """
        self._lock.acquire()
        
    def releaseBus(self):
        """ Unlock and release the bus.
        """
        self._lock.release()
