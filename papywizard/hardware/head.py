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

Hardware

Implements
==========

- Head
- HeadSimulation

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.exception import HardwareError
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.hardware.axis import Axis, AxisSimulation
from papywizard.hardware.driverFactory import DriverFactory


class Head(object):
    """ Class for panohead hardware.
    """
    def __init__(self):
        """ Init the object.
        """
        self.yawAxis = None
        self.pitchAxis = None
        self.driver = None

    def init(self):
        """ Init the head.
        """
        self.driver = DriverFactory().create(ConfigManager().get('Preferences', 'HARDWARE_DRIVER'))
        Logger().debug("Head.init(): initializing driver...")
        self.driver.init()
        Logger().debug("Head.init(): driver initialized")
        if ConfigManager().get('Preferences', 'HARDWARE_DRIVER') == 'bluetooth': # Hugly!!!
            Logger().debug("Head.init(): waiting for bluetooth connection...")
            time.sleep(config.BLUETOOTH_DRIVER_CONNECT_DELAY)
        Logger().debug("Head.init(): initializing axis...")
        self.yawAxis = Axis(config.AXIS_NUM_YAW, self.driver)
        self.pitchAxis = Axis(config.AXIS_NUM_PITCH, self.driver)
        self.yawAxis.init()
        self.pitchAxis.init()
        Logger().debug("Head.init(): axis initialized")

    def reset(self):
        """ Reseting hardware.

        Reset driver connexion?
        """
        self.yawAxis.reset()
        self.pitchAxis.reset()

    def shutdown(self):
        """ Shut down the hardware.
        """
        if self.yawAxis is not None:
            self.yawAxis.stop()
        if self.pitchAxis is not None:
            self.pitchAxis.stop()
        if self.driver is not None:
            self.driver.shutdown()

    def setOrigin(self):
        """ Set current axis positions as origin.
        """
        self.yawAxis.setOrigin()
        self.pitchAxis.setOrigin()

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
        return yaw, pitch

    def gotoPosition(self, yaw, pitch, inc=False, useOffset=True, wait=True):
        """ Goto given position.
        """
        self.yawAxis.drive(yaw, inc, useOffset, wait=False)
        self.pitchAxis.drive(pitch, inc, useOffset, wait=False)
        if wait:
            self.waitEndOfDrive()
            #self.yawAxis.waitEndOfDrive()
            #self.pitchAxis.waitEndOfDrive()

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

    def shoot(self, delay=None):
        """ Take a picture.

        @param delay: optional delay while shutter is keep pressed (s)
        @type delay: float
        """
        Logger().trace("Head.shoot()")
        self.yawAxis.setOutput(1)
        if delay is not None:
            time.sleep(delay)
        else:
            time.sleep(config.SHOOT_PULSE)
        self.yawAxis.setOutput(0)

    def setManualSpeed(self, speed):
        """ Set manual speed.

        @param speed: new speed, in ('slow', 'normal', 'fast')
        @type speed: str
        """
        if speed not in ('slow', 'normal', 'fast'):
            raise ValueError("speed value must be in ('slow', 'normal', 'fast'")
        self.yawAxis.setManualSpeed(speed)
        self.pitchAxis.setManualSpeed(speed)

    def panic(self):
        """ Stop all.
        """
        self.yawAxis.setOutput(0)
        self.yawAxis.stop()
        self.pitchAxis.stop()

class HeadSimulation(Head):
    """ Class for simulated panohead hardware.
    """
    def __init__(self, *args, **kwargs):
        """ Init the object.
        """
        self.yawAxis = AxisSimulation(config.AXIS_NUM_YAW)
        self.pitchAxis = AxisSimulation(config.AXIS_NUM_PITCH)
        self.yawAxis.start()
        self.pitchAxis.start()

    def init(self):
        """ Init the head.
        """
        self.yawAxis.init()
        self.pitchAxis.init()

    def shutdown(self):
        self.yawAxis.stopThread()
        self.yawAxis.join()
        self.pitchAxis.stopThread()
        self.pitchAxis.join()
