# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- HardwareFactory

@author: Frederic Mantegazza
@copyright: 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

from papywizard.common.exception import HardwareError
from papywizard.hardware.head import Head, HeadSimulation


class HardwareFactory(object):
    """ Class for creating hardware.
    """
    def create(self, type_):
        """ create a hardware object.

        @param type_: type of hardware object
        @type type_: str

        @raise HardwareError: unknown type
        """
        if type_ == "head":
            return Head()
        elif type_ == "headSimulation":
            return HeadSimulation()

        else:
            raise HardwareError("Unknow '%s' driver type" % type_)