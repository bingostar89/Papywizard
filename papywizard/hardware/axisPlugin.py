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

Hardware plugin

Implements
==========

- HardwarePlugin
- AxisPlugin

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common.abstractPlugin import AbstractPlugin


class HardwarePlugin(AbstractPlugin):
    """
    """
    def _defineConfig(self):
        AbstractPlugin._defineConfig(self)
        self._addConfigKey('_driver', 'DRIVER', default='bluetooth')
        self._addConfigKey('_btDevAdd', 'BT_DEVICE_ADDRESS', default="00:50:C2:58:55:B9")
        self._addConfigKey('_serPort', 'SERIAL_PORT', default="0")
        self._addConfigKey('_ethHost', 'ETHERNET_HOST', default="localhost")
        self._addConfigKey('_ethPort', 'ETHERNET_PORT', default=7165)

    # Plugin specific interface
    def connect(self):
        """ Connect to the hardware.
        """

    def disconnect(self):
        """ Disconnect from the hardware.
        """


class AxisPlugin(HardwarePlugin):
    """ Plugin for axis.
    """

    # Plugin specific interface
    def init(self):
        """ Init the axis.
        """
        raise NotImplementedError("AxisPlugin.init() must be overidden")

    def reset(self):
        """ Reset the axis.
        """
        raise NotImplementedError("AxisPlugin.reset() must be overidden")

    def drive(self, pos):
        """ Drive the axis to the given position.

        @param pos: position to reach
        @type pos: float
        """
        raise NotImplementedError("AxisPlugin.drive() must be overidden")

    def read(self):
        """ Read the axis current position

        @return: current position of the axis
        @rtype: float
        """
        raise NotImplementedError("AxisPlugin.read() must be overidden")

    def startJog(self, dir_):
        """
        """
        raise NotImplementedError("AxisPlugin.startJog() must be overidden")

    def stop(self):
        """ Stop the axis.
        """
        raise NotImplementedError("AxisPlugin.stop() must be overidden")
