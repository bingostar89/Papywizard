# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Fr�d�ric Mantegazza

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

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common.exception import HardwareError


class DriverFactory(object):
    """ Class for creating hardware driver.
    """
    def create(self, type_):
        """ create a hardware driver object.

        @param type_: type of hardware object
        @type type_: str

        @raise HardwareError: unknown type
        """
        try:
            if type_ == "bluetooth":
                from bluetoothDriver import BluetoothDriver
                return BluetoothDriver()
            elif type_ == "serial":
                from serialDriver import SerialDriver
                return SerialDriver()
            elif type_ == "usb":
                from usbDriver import USBDriver
                return USBDriver()
            else:
                raise HardwareError("Unknown '%s' driver type" % type_)
        except:
            raise HardwareError("Can't create '%s' driver" % type_)
            
