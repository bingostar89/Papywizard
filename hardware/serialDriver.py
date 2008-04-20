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

#import serial

from common import serial
from common import config
from common.loggingServices import Logger
from busDriver import BusDriver


class SerialDriver(BusDriver):
    """ Base class for serial bus drivers.
    """
    def _init(self):
        self._serial = serial.Serial(port=config.SERIAL_PORT)
        self._serial.timeout = config.SERIAL_TIMEOUT
        self._serial.baudrate = config.SERIAL_BAUDRATE
