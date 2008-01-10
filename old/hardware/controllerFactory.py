# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- DriverFactory

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

from common.exception import HardwareError
from serialPassiveDriver import SerialPassiveDriver
from serialStampDriver import SerialStampDriver
from usbDriver import USBDriver


class DriverFactory(object):
    """ Class for creating hardware driver.
    """
    def create(self, type_):
        """ create a hardware driver object.
        
        @param type_: type of hardware object
        @type type_: str
        
        @raise ValueError: unknown type
        """
        if type_ == "serialPassive":
            return SerialPassiveDriver()
        elif type_ == "serialStamp":
            return SerialStampDriver()
        elif type_ == "usb":
            return USBDriver()

        else:
            raise HardwareError("Unknow '%s' driver type" % type_)