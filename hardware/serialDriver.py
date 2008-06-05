# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- SerialDriver

@author: Frederic Mantegazza
@copyright: 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import serial

from papywizard.common.configManager import ConfigManager
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.busDriver import BusDriver


class SerialDriver(BusDriver):
    """ Base class for serial bus drivers.
    """
    def init(self):
        if not self._init:
            try:
                try:
                    port = ConfigManager().getInt('Hardware', 'SERIAL_PORT')
                except ValueError:
                    port = ConfigManager().get('Hardware', 'SERIAL_PORT')
                self._serial = serial.Serial(port=port)
                self._serial.timeout = ConfigManager().getFloat('Hardware', 'SERIAL_TIMEOUT')
                self._serial.baudrate = ConfigManager().getInt('Hardware', 'SERIAL_BAUDRATE')
                self._serial.read(self._serial.inWaiting()) # Empty buffer
                self._init = True

            except:
                Logger().exception("SerialDriver.init()")
                raise HardwareError("Can't init SerialDriver object")

    def shutdown(self):
        if self._init:
            self._serial.close()
            self._init = False