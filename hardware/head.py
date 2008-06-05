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
        self.driver = DriverFactory().create(ConfigManager().get('Hardware', 'DRIVER'))
        num = ConfigManager().getInt('Hardware', 'AXIS_NUM_YAW')
        self.yawAxis = Axis(ConfigManager().getInt('Hardware', 'AXIS_NUM_YAW'), self.driver)
        self.pitchAxis = Axis(ConfigManager().getInt('Hardware', 'AXIS_NUM_PITCH'), self.driver)

    def init(self):
        """ Init the head.

        This must be done when turning on the head.
        Note that the manual remote already does that if it is pluged-in when
        the head is switched on.
        Also note that it does not set axis to zero.
        """
        Logger().debug("Head.init(): initializing driver...")
        self.driver.init()
        Logger().debug("Head.init(): driver initialized; waiting for connection...")
        time.sleep(ConfigManager().getFloat('Hardware', 'BLUETOOTH_DRIVER_CONNECT_DELAY'))
        Logger().debug("Head.init(): initializing axis...")
        self.yawAxis.init()
        self.pitchAxis.init()
        Logger().debug("Head.init(): axis initialized")

    def reset(self):
        """ Reseting hardware.
        """
        #Logger().debug("Head.init(): shutdown driver...")
        #self.driver.shutdown()
        #Logger().debug("Head.init(): driver shut down")
        #self.init()
        self.yawAxis.reset()
        self.pitchAxis.reset()

    def shutdown(self):
        """ Shut down the hardware.
        """
        self.driver.shutdown()

    def setOrigin(self):
        """ Set current axis positions as origin.
        """
        self.yawAxis.setOrigin()
        self.pitchAxis.setOrigin()

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
        time.sleep(ConfigManager().getFloat('Hardware', 'SHOOT_PULSE'))
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
        self.yawAxis = AxisSimulation(ConfigManager().getInt('Hardware', 'AXIS_NUM_YAW'))
        self.pitchAxis = AxisSimulation(ConfigManager().getInt('Hardware', 'AXIS_NUM_PITCH'))
        self.yawAxis.start()
        self.pitchAxis.start()

    def init(self):
        """ Init the head.
        """
        self.yawAxis.init()
        self.pitchAxis.init()

    def reset(self):
        """ reset the head.
        """
        self.yawAxis.reset()
        self.pitchAxis.reset()

    def shutdown(self):
        self.yawAxis.stop()
        self.yawAxis.join()
        self.pitchAxis.stop()
        self.pitchAxis.join()

    #def stopGoto(self):
        #""" Stop axis threads.
        #"""
        #self.yawAxis.stop()
        #self.pitchAxis.stop()
        #self.yawAxis.join()
        #self.pitchAxis.join()
