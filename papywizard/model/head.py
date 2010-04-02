# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2010 Frédéric Mantegazza

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

Hardware

Implements
==========

- Head
- HeadSimulation

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.plugins.pluginsManager  import PluginsManager


class Head(QtCore.QObject):
    """ Class for panohead hardware.
    """
    def __init__(self):
        """ Init the object.
        """
        QtCore.QObject.__init__(self)

    def __getYawAxis(self):
        """
        """
        yawAxisPlugin = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        return PluginsManager ().get('yawAxis', yawAxisPlugin)[0] # Use getModel()?

    yawAxis = property(__getYawAxis)

    def __getPitchAxis(self):
        """
        """
        pitchAxisPlugin = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        return PluginsManager ().get('pitchAxis', pitchAxisPlugin)[0]

    pitchAxis = property(__getPitchAxis)

    def __getPitchArmSide(self):
        """
        """
        return ConfigManager().get('Configuration/SHOOTING_PITCH_ARM_SIDE')

    def __setPitchArmSide(self, pitchArmSide):
        """
        """
        ConfigManager().set('Configuration/SHOOTING_PITCH_ARM_SIDE', pitchArmSide)

    pitchArmSide = property(__getPitchArmSide, __setPitchArmSide)

    def isPositionValid(self, yaw, pitch):
        """ Check if position is in axis limits.

        Public method to allow the model to check all positions
        *before* starting the shooting process.

        @param yaw: yaw position to check
        @type yaw: float

        @param pitch: pitch position to check
        @type pitch: float
        """
        return self.yawAxis.isPositionValid(yaw) and \
               self.pitchAxis.isPositionValid(pitch)

    def setReference(self):
        """ Set current axis positions as reference.
        """
        self.yawAxis.setReference()
        self.pitchAxis.setReference()

    def setLimit(self, axis, dir_, limit):
        """ Set a limit.

        @param axis: axis to limit ('yaw', 'pitch')
        @type axis: str

        @param dir_: direction to limit ('+', '-')
        @type dir_: char

        @param limit: limit value
        @type limit:float
        """
        if axis == 'yaw':
            self.yawAxis.setLimit(dir_, limit)
        elif axis == 'pitch':
            self.pitchAxis.setLimit(dir_, limit)
        else:
            raise ValueError("axis must be in ('yaw', 'pitch')")

    def clearLimits(self):
        """ Clear all limits.
        """
        self.yawAxis.clearLimits()
        self.pitchAxis.clearLimits()

    def readPosition(self):
        """ Read current head position.

        @return: position of yaw and pitch axis
        @rtype: tuple
        """
        yaw = self.yawAxis.read()
        pitch = self.pitchAxis.read()

        # Revert pitch direction if the arm is on the left
        if self.pitchArmSide == 'left':
            pitch *= -1
        return yaw, pitch

    def gotoPosition(self, yaw, pitch, useOffset=True, wait=True):
        """ Goto given position.
        """
        self.yawAxis.drive(yaw, useOffset, wait=False)

        # Revert pitch direction if the arm is on the left
        if self.pitchArmSide == 'left':
            pitch *= -1
        self.pitchAxis.drive(pitch, useOffset, wait=False)
        if wait:
            self.waitEndOfDrive()

    def waitEndOfDrive(self):
        """ Wait all axis to end the drive.
        """
        self.yawAxis.waitEndOfDrive()
        self.pitchAxis.waitEndOfDrive()

    def startAxis(self, axis, dir_):
        """ Start an axis in the selected direction.

        @param axis: axis to jog ('yaw', 'pitch')
        @type axis: str

        @param dir_: direction ('+', '-')
        @type dir_: char
        """
        if axis == 'yaw':
            self.yawAxis.startJog(dir_)
        elif axis == 'pitch':

            # Revert pitch direction if the arm is on the left
            if self.pitchArmSide == 'left':
                if dir_ == '+':
                    dir_ = '-'
                else:
                    dir_ = '+'
            self.pitchAxis.startJog(dir_)
        else:
            raise ValueError("axis must be in ('yaw', 'pitch')")

    def stopAxis(self, axis='all'):
        """ Stop the selected axis.

        @param axis: axis to stop ('yaw', 'pitch', 'all')
        @type axis: str
        """
        if axis not in ('yaw', 'pitch', 'all'):
            raise ValueError("axis must be in ('yaw', 'pitch', 'all')")
        if axis in ('yaw', 'all') :
            self.yawAxis.stop()
        if axis in ('pitch', 'all'):
            self.pitchAxis.stop()

    def waitStopAxis(self, axis='all'):
        """ Wait until axis does not move anymore.

        @param axis: axis to stop ('yaw', 'pitch', 'all')
        @type axis: str
        """
        if axis not in ('yaw', 'pitch', 'all'):
            raise ValueError("axis must be in ('yaw', 'pitch', 'all')")
        if axis in ('yaw', 'all') :
            self.yawAxis.waitStop()
        if axis in ('pitch', 'all'):
            self.pitchAxis.waitStop()

    def isAxisMoving(self, axis='all'):
        """ Check if axis is moving.

        @param axis: axis to stop ('yaw', 'pitch', 'all')
        @type axis: str
        """
        if axis not in ('yaw', 'pitch', 'all'):
            raise ValueError("axis must be in ('yaw', 'pitch', 'all')")
        flag = False
        if axis in ('yaw', 'all') :
            flag = self.yawAxis.isMoving()
        if axis in ('pitch', 'all'):
            flag = flag or self.pitchAxis.isMoving()

        return flag

    def setManualSpeed(self, speed):
        """ Set manual speed.

        @param speed: new speed, in ('slow', 'normal', 'fast')
        @type speed: str
        """
        if speed not in ('slow', 'normal', 'fast'):
            raise ValueError("speed value must be in ('slow', 'normal', 'fast'")
        self.yawAxis.setManualSpeed(speed)
        self.pitchAxis.setManualSpeed(speed)
