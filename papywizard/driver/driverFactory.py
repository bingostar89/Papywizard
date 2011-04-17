# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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

- DriverFactory

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore

from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger

driverFactory = None


class DriverFactoryObject(QtCore.QObject):
    """ Class for creating hardware drivers.
    """
    def __init__(self):
        """ Init the DriverFactory object.
        """
        self.__drivers = {'bluetooth': None,
                          'serial': None,
                          'ethernet': None}

    def create(self, type_):
        """ create a hardware driver object.

        @param type_: type of hardware object
        @type type_: str

        @raise HardwareError: unknown type
        """
        try:
            # Bluetooth driver
            if type_ == 'bluetooth':
                if self.__drivers['bluetooth'] is None:
                    from bluetoothDriver import BluetoothDriver
                    mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
                    self.__drivers['bluetooth'] = BluetoothDriver(mutex)
                return self.__drivers['bluetooth']

            # Serial driver
            elif type_ == 'serial':
                if self.__drivers['serial'] is None:
                    from serialDriver import SerialDriver
                    mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
                    self.__drivers['serial'] = SerialDriver(mutex)
                return self.__drivers['serial']

            # Ethernet driver
            elif type_ == 'ethernet':
                if self.__drivers['ethernet'] is None:
                    from ethernetDriver import EthernetDriver
                    mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
                    self.__drivers['ethernet'] = EthernetDriver(mutex)
                return self.__drivers['ethernet']

            else:
                raise HardwareError("Unknown '%s' driver type" % type_)

        except Exception, msg:
            Logger().exception("DriverFactory.create()")
            raise HardwareError(unicode(msg))

    get = create # compatibility


def DriverFactory():
    global driverFactory
    if driverFactory is None:
        driverFactory = DriverFactoryObject()

    return driverFactory
