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
from papywizard.hardware.pololuServoHardware import PololuMicroMaestroHardware
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.abstractStandardShutterPlugin import AbstractStandardShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.standardShutterPluginController import StandardShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, SpinBoxField, DoubleSpinBoxField

NAME = "Panoduino"

DEFAULT_SPEED = {'yawAxis': 5,   # µs/period
                 'pitchAxis': 5  # µs/period
             }
DEFAULT_ACCEL = {'yawAxis': 1,   # µs/period²
                 'pitchAxis': 1  # µs/period²
             }
DEFAULT_CHANNEL = {'yawAxis': 0,
                   'pitchAxis': 1,
                   'shutter': 2
                }
DEFAULT_DIRECTION = {'yawAxis': unicode(QtGui.QApplication.translate("panoduinoPlugins", 'forward')),
                     'pitchAxis': unicode(QtGui.QApplication.translate("panoduinoPlugins", 'reverse'))
                 }
DEFAULT_ANGLE_1MS = {'yawAxis': 315.,  # °
                     'pitchAxis': 330.  # °
                 }
DEFAULT_NEUTRAL_POSITION = {'yawAxis': 1000,  # µs
                            'pitchAxis': 1500  # µs
                        }
DEFAULT_SHUTTER_ON = 2000  # µs
DEFAULT_SHUTTER_OFF = 1000  # µs
DEFAULT_ADDITIONAL_DELAY = 1.5  # s

VALUE_MIN = PololuMicroMaestroHardware.SERVO_MIN
VALUE_MAX = PololuMicroMaestroHardware.SERVO_MAX

LABEL_SPEED = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Speed"))
LABEL_ACCEL = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Acceleration"))

TAB_SERVO = unicode(QtGui.QApplication.translate("panoduinoPlugins", 'Servo'))
LABEL_CHANNEL = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Channel"))
LABEL_DIRECTION = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Direction"))
LABEL_ANGLE_1MS = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Angle for 1ms"))
LABEL_NEUTRAL_POSITION = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Neutral position"))
LABEL_ADDITIONAL_DELAY = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Additional delay"))

LABEL_SHUTTER_ON = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Shutter on"))
LABEL_SHUTTER_OFF = unicode(QtGui.QApplication.translate("panoduinoPlugins", "Shutter off"))

DIRECTION_INDEX = {'forward': 1,
                   'reverse': -1
                   }
DIRECTION_TABLE = {'forward': unicode(QtGui.QApplication.translate("panoduinoPlugins", 'forward')),
                   'reverse': unicode(QtGui.QApplication.translate("panoduinoPlugins", 'reverse')),
                   unicode(QtGui.QApplication.translate("panoduinoPlugins", 'forward')): 'forward',
                   unicode(QtGui.QApplication.translate("panoduinoPlugins", 'reverse')): 'reverse'
                   }
MANUAL_SPEED_TABLE = {'slow': 1,  # angle (in °) for each key press
                      'normal': 4.,
                      'fast': 10.
                      }


class PanoduinoAxis(AbstractHardwarePlugin, AbstractAxisPlugin):
    def _init(self):
        Logger().trace("PanoduinoAxis._init()")
        AbstractHardwarePlugin._init(self)
        AbstractAxisPlugin._init(self)
        self._hardware = PololuMicroMaestroHardware()

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_speed', 'SPEED', default=DEFAULT_SPEED[self.capacity])
        self._addConfigKey('_acceleration', 'ACCEL', default=DEFAULT_ACCEL[self.capacity])
        self._addConfigKey('_channel', 'CHANNEL', default=DEFAULT_CHANNEL[self.capacity])
        self._addConfigKey('_direction', 'DIRECTION', default=DEFAULT_DIRECTION[self.capacity])
        self._addConfigKey('_angle1ms', 'ANGLE_1MS', default=DEFAULT_ANGLE_1MS[self.capacity])
        self._addConfigKey('_neutralPos', 'NEUTRAL_POSITION', default=DEFAULT_NEUTRAL_POSITION[self.capacity])
        self._addConfigKey('_additionalDelay', 'ADDITIONAL_DELAY', default=DEFAULT_ADDITIONAL_DELAY)

    def _checkLimits(self, position):
        """ Check if the position can be reached.

        First check if the position in degres is in the user limits
        (done in parent class), then check if the servo can mechanically
        reach the position.
        """
        AbstractAxisPlugin._checkLimits(self, position)
        value = self.__angleToServo(position)
        if not VALUE_MIN <= value <= VALUE_MAX:
            raise HardwareError("Servo limit reached: %.2f not in [%d-%d]" % (value, VALUE_MIN, VALUE_MAX))

    def init(self):
        Logger().trace("PanoduinoAxis.init()")
        AbstractHardwarePlugin.init(self)
        self.configure()
        self._hardware.setTarget(self._config['NEUTRAL_POSITION'])

    def shutdown(self):
        Logger().trace("PanoduinoAxis.shutdown()")
        self.stop()
        self._hardware.shutdown()
        AbstractHardwarePlugin.shutdown(self)
        AbstractAxisPlugin.shutdown(self)

    def configure(self):
        Logger().trace("PanoduinoAxis.configure()")
        AbstractAxisPlugin.configure(self)
        self._hardware.setAxis(self._config['CHANNEL'])
        self._hardware.configure(self._config['SPEED'], self._config['ACCEL'])

    def __angleToServo(self, position):
        """ Compute controller servo value from position.

        @param position: position, in °
        @type position: float

        @return: value to send to servo controller
        @rtype: int
        """
        direction = DIRECTION_TABLE[self._config['DIRECTION']]
        dir_ = DIRECTION_INDEX[direction]
        servoValue = int(round(self._config['NEUTRAL_POSITION'] + dir_ * position * 1000. / self._config['ANGLE_1MS']))

        return servoValue

    def __servoToAngle(self, value):
        """ Compute position from controller servo value.

        @param value: servo value
        @type value: int

        @return: position, in °
        @rtype: float
        """
        direction = DIRECTION_TABLE[self._config['DIRECTION']]
        dir_ = DIRECTION_INDEX[direction]
        position = (value - self._config['NEUTRAL_POSITION']) * self._config['ANGLE_1MS'] / dir_ / 1000.

        return position

    def read(self):
        position = self.__servoToAngle(self._hardware.getPosition())
        return position - self._offset

    def drive(self, position, useOffset=True, wait=True):
        Logger().debug("PanoduinoAxis.drive(): '%s' drive to %.1f" % (self.capacity, position))

        self._checkLimits(position)
        if useOffset:
            position += self._offset
        value = self.__angleToServo(position)
        self._hardware.setTarget(value)
        if wait:
            self.waitEndOfDrive()

    def waitEndOfDrive(self):
        while self.isMoving():
            time.sleep(0.2)
        time.sleep(self._config['ADDITIONAL_DELAY'])  # internal servo decelaration
        self.waitStop()

    def startJog(self, dir_):
        Logger().debug("PanoduinoAxis.startJog(): dir_=%s" % repr(dir_))
        currentPos = self.read()
        position = currentPos #+ self._offset ???
        if dir_ == '+':
            position += MANUAL_SPEED_TABLE[self._manualSpeed]
        else:
            position -= MANUAL_SPEED_TABLE[self._manualSpeed]

        self._checkLimits(position)
        position += self._offset
        value = self.__angleToServo(position)
        self._hardware.setTarget(value)

    def stop(self):
        self.waitStop()

    def waitStop(self):
        pass

    def isMoving(self):
        return self._hardware.getMovingState()


class PanoduinoAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', LABEL_SPEED, SpinBoxField, (0, 255, "", u" µs/period"), 'SPEED')  # Check unit
        self._addWidget('Main', LABEL_ACCEL, SpinBoxField, (0, 255, "", u" µs/period²"), 'ACCEL')
        self._addTab('Servo', TAB_SERVO)
        self._addWidget('Servo', "Channel", SpinBoxField, (0, 5), 'CHANNEL')
        directions = [DIRECTION_TABLE['forward'], DIRECTION_TABLE['reverse']]
        self._addWidget('Servo', LABEL_DIRECTION, ComboBoxField, (directions,), 'DIRECTION')
        self._addWidget('Servo', LABEL_ANGLE_1MS, DoubleSpinBoxField, (0.1, 9999.9, 1, 1., "", u" °"), 'ANGLE_1MS')
        self._addWidget('Servo', LABEL_NEUTRAL_POSITION, SpinBoxField, (VALUE_MIN, VALUE_MAX, "", u" µs"), 'NEUTRAL_POSITION')
        self._addWidget('Servo', LABEL_ADDITIONAL_DELAY, DoubleSpinBoxField, (0.1, 9.9, 1, 0.1, "", u" s"), 'ADDITIONAL_DELAY')


class PanoduinoShutter(AbstractHardwarePlugin, AbstractStandardShutterPlugin):
    def _init(self):
        Logger().trace("PanoduinoShutter._init()")
        AbstractHardwarePlugin._init(self)
        AbstractStandardShutterPlugin._init(self)
        self._hardware = PololuMicroMaestroHardware()

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)
        self._addConfigKey('_channel', 'CHANNEL', default=DEFAULT_CHANNEL[self.capacity])
        self._addConfigKey('_shutterOn', 'SHUTTER_ON', default=DEFAULT_SHUTTER_ON)
        self._addConfigKey('_shutterOff', 'SHUTTER_OFF', default=DEFAULT_SHUTTER_OFF)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._driver.acquireBus()
        try:
            self._hardware.setTarget(self._config['SHUTTER_ON'])
        finally:
            self._driver.releaseBus()

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._driver.acquireBus()
        try:
            self._hardware.setTarget(self._config['SHUTTER_OFF'])
        finally:
            self._driver.releaseBus()

    #def activate(self):
        #Logger().trace("PanoduinoShutter.activate()")

    def init(self):
        Logger().trace("PanoduinoShutter.init()")
        self._hardware.setAxis(self._config['CHANNEL']),
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
        self._addWidget('Servo', LABEL_CHANNEL, SpinBoxField, (0, 5, "", ""), 'CHANNEL')
        self._addWidget('Servo', LABEL_SHUTTER_ON, SpinBoxField, (VALUE_MIN, VALUE_MAX, "", u" µs"), 'SHUTTER_ON')
        self._addWidget('Servo', LABEL_SHUTTER_OFF, SpinBoxField, (VALUE_MIN, VALUE_MAX, "", u" µs"), 'SHUTTER_OFF')


def register():
    """ Register plugins.
    """
    PluginsManager().register(PanoduinoAxis, PanoduinoAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(PanoduinoAxis, PanoduinoAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(PanoduinoShutter, PanoduinoShutterController, capacity='shutter', name=NAME)
