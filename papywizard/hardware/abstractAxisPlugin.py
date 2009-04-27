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

Plugin

Implements
==========

- AbstractAxisPlugin

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common.exception import HardwareError
from papywizard.common.abstractPlugin import AbstractPlugin

DEFAULT_LOW_LIMIT = -360.
DEFAULT_HIGH_LIMIT = 360.


class AbstractAxisPlugin(AbstractPlugin):
    """ Abstract plugin for axis.

    Common implementation of axis.
    """
    def establishConnection(self):
        pass

    def shutdownConnection(self):
        pass

    def _init(self):
        #self._config['HIGH_LIMIT'] = 9999.9
        #self._config['LOW_LIMIT'] = -9999.9
        self._manualSpeed = 'normal'
        self._offset = 0.

    def _defineConfig(self):
        """ Add high/low limits
        """
        self._addConfigKey('_lowLimit', 'LOW_LIMIT', default=DEFAULT_LOW_LIMIT)
        self._addConfigKey('_highLimit', 'HIGH_LIMIT', default=DEFAULT_HIGH_LIMIT)

    def _checkLimits(self, position):
        """ Check if position is in axis limits.

        @param position: position to check
        @type position: float
        """
        if not self._config['LOW_LIMIT'] <= position <= self._config['HIGH_LIMIT']:
            raise HardwareError("Axis limit reached: %.1f not in [%.1f-%.1f]" % \
                                 (position, self._config['LOW_LIMIT'], self._config['HIGH_LIMIT']))

    def isPositionValid(self, position):
        """ Check if position is in axis limits.

        Public method to allow the model to check all positions
        *before* starting the shooting process.

        @param position: position to check
        @type position: float
        """
        try:
            self._checkLimits()
            return True
        except HardwareError:
            return False

    def setReference(self):
        """ Set current axis positions as reference.
        """
        self._offset += self.read()

    #def setLimit(self, dir_, limit):
        #""" Set the minus limit.

        #@param dir_: direction to limit ('+', '-')
        #@type dir_: char

        #@param limit: minus limit to set
        #@type limit: float
        #"""
        #if dir_ == '+':
            #self._config['HIGH_LIMIT'] = limit
        #elif dir_ == '-':
            #self._config['LOW_LIMIT'] = limit
        #else:
            #raise ValueError("dir must be in ('+', '-')")

    #def clearLimits(self):
        #""" Clear all limits.
        #"""
        #self._config['HIGH_LIMIT'] = 9999.9
        #self._config['LOW_LIMIT'] = -9999.9

    def read(self):
        """ Return the current position of axis.

        @return: position, in °
        @rtype: float
        """
        raise NotImplementedError("AbstractAxisPlugin.read() must be overloaded")

    def drive(self, pos, inc=False, useOffset=True, wait=True):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float

        @param inc: if True, pos is an increment
        @type inc: bool

        @param useOffset: flag to use offset or not
        @type useOffset: bool

        @param wait: if True, wait for end of movement,
                     returns immediatly otherwise.
        @type wait: boot
        """
        raise NotImplementedError("AbstractAxisPlugin.drive() must be overloaded")

    def waitEndOfDrive(self):
        """ Wait for end of drive.
        """
        raise NotImplementedError("AbstractAxisPlugin.waitEndOfDrive() must be overloaded")

    def startJog(self, dir_):
        """ Start axis in specified direction.

        @param dir_: direction ('+', '-')
        @type dir_: char
        """
        raise NotImplementedError("AbstractAxisPlugin.startJog() must be overloaded")

    def stop(self):
        """ stop drive axis.
        """
        raise NotImplementedError("AbstractAxisPlugin.stop() must be overloaded")

    def waitStop(self):
        """ Wait until axis does not move anymore (inertia).
        """
        raise NotImplementedError("AbstractAxisPlugin.waitStop() must be overloaded")

    def isMoving(self):
        """ Check if axis is moving.

        @return: True if moving, False if stopped
        @rtype: bool
        """
        raise NotImplementedError("AbstractAxisPlugin.isMoving() must be overloaded")

    def setManualSpeed(self, speed):
        """ Set manual speed.

        @param speed: new manual speed, in ('slow', 'normal', 'fast')
        @type speed: str
        """
        raise NotImplementedError("AbstractAxisPlugin.setManualSpeed() must be overloaded")
