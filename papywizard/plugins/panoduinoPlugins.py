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

- PanoduinoAxis
- PanoduinoAxisController
- PanoduinoShutter
- PanoduinoShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.pololuServoHardware import PololuServoHardware
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.abstractStandardShutterPlugin import AbstractStandardShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.standardShutterPluginController import StandardShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, SpinBoxField, DoubleSpinBoxField

NAME = "Panoduino"

DEFAULT_SPEED = 64
DEFAULT_DIRECTION = unicode(QtGui.QApplication.translate("panoduinoPlugins", 'forward'))
DEFAULT_NEUTRAL_POSITION = 3000 # controller value for neutral position
DEFAULT_VALUE_OFF = 0
DEFAULT_VALUE_ON = 127

LABEL_SPEED = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Speed"))

TAB_SERVO = unicode(QtGui.QApplication.translate("panoduinoPlugins", 'Servo'))
LABEL_DIRECTION = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Direction"))
LABEL_NEUTRAL_POSITION = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Neutral position"))
LABEL_VALUE_OFF = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Value off"))
LABEL_VALUE_ON = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Value on"))

AXIS_TABLE = {'yawAxis': 1,
              'pitchAxis': 2,
              'shutter': 0
              }
DIRECTION_INDEX = {'forward': 1,
                   'reverse': -1
                   }
DIRECTION_TABLE = {'forward': unicode(QtGui.QApplication.translate("panoduinoPlugins", 'forward')),
                   'reverse': unicode(QtGui.QApplication.translate("panoduinoPlugins", 'reverse')),
                   unicode(QtGui.QApplication.translate("panoduinoPlugins", 'forward')): 'forward',
                   unicode(QtGui.QApplication.translate("panoduinoPlugins", 'reverse')): 'reverse'
                   }
SPEED_TABLE = {'yawAxis': 64,
               'pitchAxis': 64
               }
ANGLE_1MS_TABLE = {'yawAxis': 525.,  # angle (in °) for a 1ms pulse change
                   'pitchAxis': 315.
                   }
MANUAL_SPEED_TABLE = {'slow': .5,  # angle (in °) for each key press
                      'normal': 2.,
                      'fast': 5.
                      }


class PanoduinoAxis(AbstractHardwarePlugin, AbstractAxisPlugin):
    def _init(self):
        Logger().trace("PanoduinoAxis._init()")
        AbstractHardwarePlugin._init(self)
        AbstractAxisPlugin._init(self)
        self._hardware = PololuServoHardware()
        self.__position = None
        self.__endDrive = None

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_speed', 'SPEED', default=DEFAULT_SPEED)
        self._addConfigKey('_direction', 'DIRECTION', default=DEFAULT_DIRECTION)
        self._addConfigKey('_neutralPos', 'NEUTRAL_POSITION', default=DEFAULT_NEUTRAL_POSITION)

    def _checkLimits(self, position):
        """ Check if the position can be reached.

        First check if the position in degres is in the user limits
        (done in parent class), then check if the servo can mechanically
        reach the position.
        """
        AbstractAxisPlugin._checkLimits(self, position)
        value = self.__computeServoPosition(position)
        if not 500 <= value <= 5500:
            raise HardwareError("Servo limit reached: %d not in [500-5500]" % value)

    def init(self):
        Logger().trace("PanoduinoAxis.init()")
        self._hardware.setAxis(AXIS_TABLE[self.capacity]),
        AbstractHardwarePlugin.init(self)
        self.configure()
        self._hardware.setPositionAbsolute(self._config['NEUTRAL_POSITION'])
        self.__position = 0.
        self.__endDrive = 0

    def shutdown(self):
        Logger().trace("PanoduinoAxis.shutdown()")
        self.stop()
        self._hardware.shutdown()
        AbstractHardwarePlugin.shutdown(self)
        AbstractAxisPlugin.shutdown(self)

    def configure(self):
        Logger().trace("PanoduinoAxis.configure()")
        AbstractAxisPlugin.configure(self)
        speed = self.__computeServoSpeed(self._config['SPEED'])
        direction = DIRECTION_TABLE[self._config['DIRECTION']]
        self._hardware.configure(speed, direction)
        #self._hardware.setNeutral(self._config['NEUTRAL_POSITION'])

    def read(self):
        return self.__position - self._offset

    def __computeServoSpeed(self, speed):
        """ Compute controller servo value from position.

        @param speed: speed, in °/s
        @type speed: float

        @return: value to send to servo controller
        @rtype: int
        """
        return speed

        servoSpeed = int(speed * 1000 / ANGLE_1MS_TABLE[self.capacity] / 50)
        if servoSpeed < 1:
            servoSpeed = 1
        elif servoSpeed > 127:
            servoSpeed = 127
        return servoSpeed

    def __computeServoPosition(self, position):
        """ Compute controller servo value from position.

        @param position: position, in °
        @type position: float

        @return: value to send to servo controller
        @rtype: int
        """
        direction = DIRECTION_TABLE[self._config['DIRECTION']]
        dir_ = DIRECTION_INDEX[direction]
        servoPosition = int(self._config['NEUTRAL_POSITION'] + dir_ * position / ANGLE_1MS_TABLE[self.capacity] * 2000)
        return servoPosition

    def drive(self, position, useOffset=True, wait=True):
        Logger().debug("PanoduinoAxis.drive(): '%s' drive to %.1f" % (self.capacity, position))

        currentPos = self.read()
        self._checkLimits(position)
        if useOffset:
            position += self._offset
        value = self.__computeServoPosition(position)
        self._hardware.setPositionAbsolute(value)
        self._endDrive = time.time() + abs(position - self.__position) / self._config['SPEED']
        if wait:
            self.waitEndOfDrive()
        self.__position = position

        # TODO: use a setpoint, and compute position in read according to timing/speed/...
        # This avoid using a thread

    def waitEndOfDrive(self):
        remaingTimeToWait = self._endDrive - time.time()
        Logger().debug("PanoduinoAxis.waitEndOfDrive(): remaing time to wait %.1f" % remaingTimeToWait)
        if remaingTimeToWait > 0:
            time.sleep(remaingTimeToWait)
        self.waitStop()

    def startJog(self, dir_):
        """ Need to be run in a thread.
        """
        position = self.__position + self._offset
        if dir_ == '+':
            position += MANUAL_SPEED_TABLE[self._manualSpeed]
        else:
            position -= MANUAL_SPEED_TABLE[self._manualSpeed]

        # Call self.drive() ???

        self._checkLimits(position)
        value = self.__computeServoPosition(position)
        self._hardware.setPositionAbsolute(value)
        self.__position = position

    def stop(self):
        self.waitStop()

    def waitStop(self):
        pass

    def isMoving(self):
        if self._endDrive < time.time():
            return False
        else:
            return True


class PanoduinoAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', LABEL_SPEED, SpinBoxField, (0, 127), 'SPEED')
        self._addTab('Servo', TAB_SERVO)
        directions = [DIRECTION_TABLE['forward'], DIRECTION_TABLE['reverse']]
        self._addWidget('Servo', LABEL_DIRECTION, ComboBoxField, (directions,), 'DIRECTION')
        self._addWidget('Servo', LABEL_NEUTRAL_POSITION, SpinBoxField, (500, 5500), 'NEUTRAL_POSITION')


class PanoduinoShutter(AbstractHardwarePlugin, AbstractStandardShutterPlugin):
    def _init(self):
        Logger().trace("PanoduinoShutter._init()")
        AbstractHardwarePlugin._init(self)
        AbstractStandardShutterPlugin._init(self)
        self._hardware = PololuServoHardware()

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)
        self._addConfigKey('_valueOff', 'VALUE_OFF', default=DEFAULT_VALUE_OFF)
        self._addConfigKey('_valueOn', 'VALUE_ON', default=DEFAULT_VALUE_ON)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._driver.acquireBus()
        try:
            self._hardware.setPosition7bits(self._config['VALUE_ON'])
        finally:
            self._driver.releaseBus()

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._driver.acquireBus()
        try:
            self._hardware.setPosition7bits(self._config['VALUE_OFF'])
        finally:
            self._driver.releaseBus()

    def activate(self):
        Logger().trace("PanoduinoShutter.activate()")
        self._initialPosition = self._config['VALUE_OFF']

    def init(self):
        Logger().trace("PanoduinoShutter.init()")
        self._hardware.setAxis(AXIS_TABLE[self.capacity]),
        AbstractHardwarePlugin.init(self)

    def shutdown(self):
        Logger().trace("PanoduinoShutter.shutdown()")
        self._triggerOffShutter()
        self._hardware.shutdown()
        AbstractHardwarePlugin.shutdown(self)
        AbstractStandardShutterPlugin.shutdown(self)


class PanoduinoShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        Logger().trace("PanoduinoShutterController._defineGui()")
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Servo', TAB_SERVO)
        self._addWidget('Servo', LABEL_VALUE_OFF, SpinBoxField, (0, 127), 'VALUE_OFF')
        self._addWidget('Servo', LABEL_VALUE_ON, SpinBoxField, (0, 127), 'VALUE_ON')


def register():
    """ Register plugins.
    """
    PluginsManager().register(PanoduinoAxis, PanoduinoAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(PanoduinoAxis, PanoduinoAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(PanoduinoShutter, PanoduinoShutterController, capacity='shutter', name=NAME)
