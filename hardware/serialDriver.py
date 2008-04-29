# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- SerialDriver

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import serial

from common import config
from common.exception import HardwareError
from common.loggingServices import Logger
from busDriver import BusDriver


class SerialDriver(BusDriver):
    """ Base class for serial bus drivers.
    """
    def init(self):
        if not self._init:
            try:
                self._serial = serial.Serial(port=config.SERIAL_PORT)
                self._serial.timeout = config.SERIAL_TIMEOUT
                self._serial.baudrate = config.SERIAL_BAUDRATE
                self._serial.read(self._serial.inWaiting()) # Empty buffer
                self._init = True
                
            except:
                Logger().exception("SerialDriver.init()")
                raise HardwareError("Can't init SerialDriver object")

    def shutdown(self):
        if self._init:
            self._serial.close()
            self._init = False