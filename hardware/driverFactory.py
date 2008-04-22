# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- DriverFactory

@author: Frederic Mantegazza
@copyright: 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

from common.exception import HardwareError


class DriverFactory(object):
    """ Class for creating hardware driver.
    """
    def create(self, type_):
        """ create a hardware driver object.
        
        @param type_: type of hardware object
        @type type_: str
        
        @raise HardwareError: unknown type
        """
        if type_ == "serialPassive":
            from serialPassiveDriver import SerialPassiveDriver
            return SerialPassiveDriver()
        elif type_ == "serialStamp":
            from serialStampDriver import SerialStampDriver
            return SerialStampDriver()
        elif type_ == "usb":
            from usbDriver import USBDriver
            return USBDriver()
        elif type_ == "bluetooth":
            from bluetoothDriver import BluetoothDriver
            return BluetoothDriver()

        else:
            raise HardwareError("Unknow '%s' driver type" % type_)