# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- Head
- HeadSimulation

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time

from common import config
from common.loggingServices import Logger
from axis import Axis, AxisSimulation
from driverFactory import DriverFactory


class Head(object):
    """ Class for panohead hardware.
    """
    def __init__(self):
        """ Init the object.
        """
        driver = DriverFactory().create(config.DRIVER)
        self.yawAxis = Axis(config.AXIS_NUM_YAW, driver)
        self.pitchAxis = Axis(config.AXIS_NUM_PITCH, driver)
    
    def reset(self):
        """ Reset the head.
        
        This must be done when turning on the head.
        Note that the manual remote already does that if it is pluged-in when
        the head is switched on.
        Also note that it does not set axis to zero.
        """
        self.yawAxis.reset()
        self.pitchAxis.reset()

    init = reset

    def readPosition(self):
        """ Read current head position.
        
        @return: position of yaw and pitch axis
        @rtype: tuple
        """
        yaw = self.yawAxis.read()
        pitch = self.pitchAxis.read()
        return yaw, pitch

    def gotoPosition(self, yaw, pitch, wait=True):
        """ Goto given position.
        """
        self.yawAxis.drive(yaw, wait=False)
        self.pitchAxis.drive(pitch, wait=False)
        if wait:
            self.yawAxis.waitEndOfDrive()
            self.pitchAxis.waitEndOfDrive()

    def stopGoto(self):
        """ Stop a previous drivePosition.
        """
        self.yawAxis.stopDrive()
        self.pitchAxis.stopDrive()

    def startAxis(self, axis, dir):
        """ Start an axis in the selected direction.
        
        @param axis: axis to jog ('yaw', 'pitch')
        @type axis: str
        
        @param dir: direction ('+', '-')
        @type dir: char
        """
        if axis == 'yaw':
            self.yawAxis.startJog(dir)
        elif axis == 'pitch':
            self.pitchAxis.startJog(dir)
        else:
            raise ValueError("axis must be in 'yaw', 'pitch'")

    def stopAxis(self, axis):
        """ Stop the selected axis.
        
        @param axis: axis to stop ('yaw', 'pitch')
        @type axis: str
        """
        if axis == 'yaw':
            self.yawAxis.stopJog()
        elif axis == 'pitch':
            self.pitchAxis.stopJog()
        else:
            raise ValueError("axis must be in 'yaw', 'pitch'")
       
    def waitStopAxis(self, axis):
        """ Wait until axis does not move anymore.
        """
        if axis == 'yaw':
            self.yawAxis.waitStop()
        elif axis == 'pitch':
            self.pitchAxis.waitStop()
        else:
            raise ValueError("axis must be in 'yaw', 'pitch'")

    def shoot(self, delay=1):
        """ Take a picture.
        
        @param delay: delay to wait at each shot (s)
        @type delay: float
        """
        Logger().trace("Head.shoot()")
        self.yawAxis.setOutput(1)
        time.sleep(config.SHOOT_PULSE)
        self.yawAxis.setOutput(0)
        time.sleep(delay)

    def panic(self):
        """ Stop all.
        """
        self.yawAxis.setOutput(0)
        self.yawAxis.stopDrive()
        self.pitchAxis.stopDrive()


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

    #def stopGoto(self):
        #""" Stop axis threads.
        #"""
        #self.yawAxis.stop()
        #self.pitchAxis.stop()
        #self.yawAxis.join()
        #self.pitchAxis.join()
