# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2009 Frédéric Mantegazza

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

- SerialDriver

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import serial

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.abstractDriver import AbstractDriver


class SerialDriver(AbstractDriver):
    """ Driver for serial connection.
    """
    def _init(self):
        try:
            try:
                port = ConfigManager().getInt('Preferences/HARDWARE_SERIAL_PORT')
            except ValueError:
                port = ConfigManager().get('Preferences/HARDWARE_SERIAL_PORT')
            self._serial = serial.Serial(port=port)
            self._serial.timeout = config.SERIAL_TIMEOUT
            self._serial.baudrate = config.SERIAL_BAUDRATE
            self.empty()
        except:
            Logger().exception("SerialDriver._init()")
            raise

    def _shutdown(self):
        self._serial.close()

    def setCS(self, level):
        """ Set CS signal to specified level.

        @param level: level to set to CS signal
        @type level: int
        """
        #self._serial.setDTR(level)

    def empty(self):
        if hasattr(self._serial, "inWaiting"):
            self.read(self._serial.inWaiting())

    def write(self, data):
        #Logger().debug("SerialDriver.write(): data=%s" % repr(data))
        size = self._serial.write(data)
        return size

    def read(self, size):
        data = self._serial.read(size)
        #Logger().debug("SerialDriver.read(): data=%s" % repr(data))
        if size and not data:
            raise IOError("Timeout while reading on serial bus")
        else:
            return data
