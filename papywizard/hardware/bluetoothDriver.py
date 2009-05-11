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

- BluetoothDriver

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.bluetoothTransport import BluetoothSocket, BluetoothError, RFCOMM
from papywizard.common.exception import HardwareError
from papywizard.hardware.abstractDriver import AbstractDriver


class BluetoothDriver(AbstractDriver):
    """ Driver for bluetooth connection.

    This driver only uses bluetooth socket.
    """
    def _init(self):
        Logger().trace("BluetoothDriver._init()")
        address = ConfigManager().get('Plugins/HARDWARE_BLUETOOTH_DEVICE_ADDRESS')
        Logger().debug("BluetoothDriver._init(): trying to connect to %s..." % address)
        try:
            self._sock = BluetoothSocket(RFCOMM)
            self._sock.connect((address, 1))
            try:
                self._sock.settimeout(1.)
            except NotImplementedError:
                Logger().warning("BluetoothDriver._init(): bluetooth stack does not implment settimeout()")
        except BluetoothError, error:
            Logger().exception("BluetoothDriver._init()")
            err, msg = eval(error.message)
            raise HardwareError(msg)
        except:
            Logger().exception("BluetoothDriver._init()")
            raise
        else:
            time.sleep(config.BLUETOOTH_DRIVER_CONNECT_DELAY)
            self.empty()
            Logger().debug("BluetoothDriver._init(): successfully connected to %s" % address)

    def _shutdown(self):
        self._sock.close()

    def empty(self):
        pass

    def write(self, data):
        #Logger().debug("BluetoothDriver.write(): data=%s" % repr(data))
        size = self._sock.send(data)
        return size

    def read(self, size):
        data = self._sock.recv(size)
        #Logger().debug("BluetoothDriver.read(): data=%s" % repr(data))
        if size and not data:
            raise IOError("Timeout while reading on bluetooth bus (size=%d, data=%s)" % (size, repr(data)))
        else:
            return data
