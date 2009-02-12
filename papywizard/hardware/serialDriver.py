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
from papywizard.hardware.busDriver import BusDriver


class SerialDriver(BusDriver):
    """ Driver for serial connection.
    """
    def init(self):
        if not self._init:
            try:
                try:
                    port = ConfigManager().getInt('Preferences', 'HARDWARE_SERIAL_PORT')
                except ValueError:
                    port = ConfigManager().get('Preferences', 'HARDWARE_SERIAL_PORT')
                self._serial = serial.Serial(port=port)
                self._serial.timeout = config.SERIAL_TIMEOUT
                self._serial.baudrate = config.SERIAL_BAUDRATE
                self._serial.read(self._serial.inWaiting()) # Empty buffer
                self._init = True
            #except ???, msg:
                #Logger().exception("BluetoothDriver.init()")
                #raise HardwareError(msg)
            except:
                Logger().exception("SerialDriver.init()")
                raise

    def shutdown(self):
        if self._init:
            self._serial.close()
            self._init = False

    def _setCS(self, level):
        """ Set CS signal to specified level.

        @param level: level to set to CS signal
        @type level: int
        """
        #self._serial.setDTR(level)

    def sendCmd(self, cmd):
        if not self._init:
            raise HardwareError(self.tr("SerialDriver not initialized"))

        self.acquireBus()
        try:
            # Empty buffer
            self._serial.read(self._serial.inWaiting())

            self._setCS(0)
            self._serial.write(":%s\r" % cmd)
            c = ''
            while c != '=':
                c = self._serial.read()
                #Logger().debug("SerialPassiveDriver.sendCmd(): c=%s" % repr(c))
                if not c:
                    raise IOError(self.tr("Timeout while reading on serial bus"))
            data = ""
            while True:
                c = self._serial.read()
                #Logger().debug("SerialPassiveDriver.sendCmd(): c=%s, data=%s" % (repr(c), repr(data)))
                if not c:
                    raise IOError(self.tr("Timeout while reading on serial bus"))
                elif c == '\r':
                    break
                data += c

        finally:
            self._setCS(1)
            self.releaseBus()

        return data
