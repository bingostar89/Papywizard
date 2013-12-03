# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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

 - MerlinOrionAxis
 - MerlinOrionAxisController
 - MerlinOrionShutter
 - MerlinOrionShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
@todo: add private methods to MerlinOrionHardware for sending commands to MerlinOrion
"""

__revision__ = "$Id$"

import time
import threading

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.controller.spy import Spy
from papywizard.hardware.merlinOrionHardware import MerlinOrionHardware
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.shutterPlugin import ShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import SpinBoxField, DoubleSpinBoxField, CheckBoxField

NAME = "Merlin-Orion"

DEFAULT_ALTERNATE_DRIVE = True
DEFAULT_ALTERNATE_DRIVE_ANGLE = 7. # °
DEFAULT_INERTIA_ANGLE = 1. # °
DEFAULT_OVERWRITE_ENCODER_FULL_CIRCLE = False
DEFAULT_ENCODER_FULL_CIRCLE = 0xe62d3

TAB_HARD = unicode(QtGui.QApplication.translate("merlinOrionPlugins", 'Hard'))
LABEL_ALTERNATE_DRIVE = unicode(QtGui.QApplication.translate("merlinOrionPlugins", "Alternate drive"))
LABEL_ALTERNATE_DRIVE_ANGLE = unicode(QtGui.QApplication.translate("merlinOrionPlugins", "Alternate drive angle"))
LABEL_INERTIA_ANGLE = unicode(QtGui.QApplication.translate("merlinOrionPlugins", "Inertia angle"))
LABEL_OVERWRITE_ENCODER_FULL_CIRCLE = unicode(QtGui.QApplication.translate("merlinOrionPlugins", "Overwrite encoder full circle"))
LABEL_ENCODER_FULL_CIRCLE = unicode(QtGui.QApplication.translate("merlinOrionPlugins", "Encoder full circle"))

AXIS_ACCURACY = 0.1 # °
AXIS_TABLE = {'yawAxis': 1,
              'pitchAxis': 2,
              'shutter': 1
              }
MANUAL_SPEED_TABLE = {'slow': 170,  # "AA0000"  / 5
                      'alternate': 80, # "500000"
                      'normal': 34, # "220000" nominal
                      'fast': 17   # "110000"  * 2
                      }


class MerlinOrionAxis(AbstractHardwarePlugin, AbstractAxisPlugin, QtCore.QThread):
    """
    """
    def __init__(self, *args, **kwargs):
        AbstractHardwarePlugin.__init__(self, *args, **kwargs)  # Only 1?
        AbstractAxisPlugin.__init__(self, *args, **kwargs)
        QtCore.QThread.__init__(self)

    def __onPositionUpdate(self, yaw, pitch):
        """ Refresh position according to new pos.

        @param yaw: yaw axis value
        @type yaw: float

        @param pitch: pitch axix value
        @type pitch: float
        """
        if self.capacity == 'yawAxis':
            self.__currentPos = yaw
        else:
            self.__currentPos = pitch

    def _init(self):
        Logger().trace("MerlinOrionAxis._init()")
        AbstractHardwarePlugin._init(self)
        AbstractAxisPlugin._init(self)
        self._hardware = MerlinOrionHardware()
        self.__run = False
        self.__driveEvent = threading.Event()
        self.__setPoint = None
        self.__currentPos = None

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_alternateDrive', 'ALTERNATE_DRIVE', default=DEFAULT_ALTERNATE_DRIVE)
        self._addConfigKey('_alternateDrive', 'ALTERNATE_DRIVE_ANGLE', default=DEFAULT_ALTERNATE_DRIVE_ANGLE)
        self._addConfigKey('_inertiaAngle', 'INERTIA_ANGLE', default=DEFAULT_INERTIA_ANGLE)
        self._addConfigKey('_overwriteEncoderFullCircle', 'OVERWRITE_ENCODER_FULL_CIRCLE', default=DEFAULT_OVERWRITE_ENCODER_FULL_CIRCLE)
        self._addConfigKey('_encoderFullCircle', 'ENCODER_FULL_CIRCLE', default=DEFAULT_ENCODER_FULL_CIRCLE)

    def activate(self):
        Logger().trace("MerlinOrionPlugin.activate()")
        AbstractAxisPlugin.activate(self)

        # Start the thread
        self.start()

    def deactivate(self):
        Logger().trace("MerlinOrionPlugin.deactivate()")

        # Stop the thread
        self._stopThread()

        AbstractAxisPlugin.deactivate(self)

    def init(self):
        Logger().trace("MerlinOrionAxis.init()")
        self._hardware.setAxis(AXIS_TABLE[self.capacity]),
        AbstractHardwarePlugin.init(self)
        if self._config['OVERWRITE_ENCODER_FULL_CIRCLE']:
            self._hardware.overwriteEncoderFullCircle(self._config['ENCODER_FULL_CIRCLE'])

        # Connect Spy update signal
        self.connect(Spy(), QtCore.SIGNAL("update"), self.__onPositionUpdate, QtCore.Qt.BlockingQueuedConnection)

    def shutdown(self):
        Logger().trace("MerlinOrionAxis.shutdown()")
        self.stop()
        AbstractHardwarePlugin.shutdown(self)
        AbstractAxisPlugin.shutdown(self)

        # Disconnect Spy update signal
        self.disconnect(Spy(), QtCore.SIGNAL("update"), self.__onPositionUpdate)

    def configure(self):
        AbstractAxisPlugin.configure(self)
        AbstractHardwarePlugin.configure(self)
        if self._config['OVERWRITE_ENCODER_FULL_CIRCLE']:
            self._hardware.overwriteEncoderFullCircle(self._config['ENCODER_FULL_CIRCLE'])
        else:
            self._hardware.useFirmwareEncoderFullCircle()

    def run(self):
        """ Main entry of the thread.
        """
        threadName = "%s_%s" % (self.name, self.capacity)
        threading.currentThread().setName(threadName)
        Logger().debug("MerlinOrionAxis.run(): start thread")
        self.__run = True
        while self.__run:
            self.__driveEvent.wait()

            # Check again __run flag to see if _stopThread has been called
            if self.__run:

                # Choose alternate drive if needed
                currentPos = self.read()
                if self._config['ALTERNATE_DRIVE'] and \
                   1.1 * self._config['INERTIA_ANGLE'] < abs(self.__setPoint - currentPos) < self._config['ALTERNATE_DRIVE_ANGLE']:
                    self._alternateDrive(self.__setPoint)

                # Use standard drive to reach the position
                if self.__driveEvent.isSet():
                    self._directDrive(self.__setPoint)

        Logger().debug("MerlinOrionAxis.run(): thread terminated")

    def _stopThread(self):
        """ Stop the thread.
        """
        self.__run = False
        self.__driveEvent.set()
        self.wait()

    def read(self):
        pos = self._hardware.read() - self._offset
        return pos

    def drive(self, pos, useOffset=True, wait=True):
        Logger().debug("MerlinOrionAxis.drive(): '%s' drive to %.1f" % (self.capacity, pos))
        currentPos = self.read()

        self._checkLimits(pos)

        # Only move if needed
        if abs(pos - currentPos) > AXIS_ACCURACY or not useOffset:
            if not useOffset:  # Move before if?
                pos -= self._offset

            self.__setPoint = pos
            self.__driveEvent.set() # Start thread action

            # Wait end of movement
            if wait:
                self.waitEndOfDrive()

    def _directDrive(self, pos):
        """ Direct drive.

        This method uses the Merlin/Orion internal closed loop regulation.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("MerlinOrionAxis._directDrive()")
        pos += self._offset
        self._hardware.drive(pos)
        self.__driveEvent.clear()

    def _alternateDrive(self, pos):
        """ Alternate drive.

        This method implements an external closed-loop regulation.
        It is faster for angles < 6-7°, because in this case, the
        head does not accelerate to full speed, but rather stays at
        very low speed.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("MerlinOrionAxis._alternateDrive()")

        # Compute initial direction
        # BUG!!! Arm side is not taken in account!!!
        if pos > self.__currentPos:
            dir_ = '+'
        else:
            dir_ = '-'
        self._hardware.startJog(dir_, MANUAL_SPEED_TABLE['alternate'])

        # Check when to stop
        #while ((dir_ == '-' and self.__currentPos - pos > self._config['INERTIA_ANGLE']) or \
               #(dir_ == '+' and pos - self.__currentPos > self._config['INERTIA_ANGLE'])) and \
              #self.__driveEvent.isSet():
        while abs(self.__currentPos - pos) > self._config['INERTIA_ANGLE'] and self.__driveEvent.isSet():
            time.sleep(config.SPY_REFRESH_DELAY / 1000.)

        self._hardware.stop()

    def waitEndOfDrive(self):
        while self.isMoving():
            time.sleep(config.SPY_REFRESH_DELAY / 1000.)
        self.waitStop()

    def startJog(self, dir_):
        self._hardware.startJog(dir_, MANUAL_SPEED_TABLE[self._manualSpeed])

    def stop(self):
        self.__driveEvent.clear()
        self._hardware.stop()

    def waitStop(self):
        previousPos = self.__currentPos
        time.sleep(config.SPY_REFRESH_DELAY / 1000.)
        while abs(previousPos - self.__currentPos) > AXIS_ACCURACY:
            previousPos = self.__currentPos
            time.sleep(config.SPY_REFRESH_DELAY / 1000.)

    def isMoving(self):
        status = self._hardware.getStatus()
        if status[1] != '0' or self.__driveEvent.isSet():
            return True
        else:
            return False


class MerlinOrionAxisController(AxisPluginController, HardwarePluginController):
    def _valueChanged(self, value=None):
        self.refreshView()

    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Hard', TAB_HARD)
        self._addWidget('Hard', LABEL_ALTERNATE_DRIVE, CheckBoxField, (), 'ALTERNATE_DRIVE')
        self._addWidget('Hard', LABEL_ALTERNATE_DRIVE_ANGLE, SpinBoxField, (3, 15, "", u" °"), 'ALTERNATE_DRIVE_ANGLE')
        self._addWidget('Hard', LABEL_INERTIA_ANGLE, DoubleSpinBoxField, (0.1, 9.9, 1, .1, "", u" °"), 'INERTIA_ANGLE')
        self._addWidget('Hard', LABEL_OVERWRITE_ENCODER_FULL_CIRCLE, CheckBoxField, (), 'OVERWRITE_ENCODER_FULL_CIRCLE')
        self._addWidget('Hard', LABEL_ENCODER_FULL_CIRCLE, SpinBoxField, (0, 16777216, "", ""), 'ENCODER_FULL_CIRCLE')

    def refreshView(self):
        enable = self._getWidget('Hard', LABEL_ALTERNATE_DRIVE).value()
        self._getWidget('Hard', LABEL_ALTERNATE_DRIVE_ANGLE).setDisabled(not enable)
        self._getWidget('Hard', LABEL_INERTIA_ANGLE).setDisabled(not enable)
        enable = self._getWidget('Hard', LABEL_OVERWRITE_ENCODER_FULL_CIRCLE).value()
        self._getWidget('Hard', LABEL_ENCODER_FULL_CIRCLE).setDisabled(not enable)

class MerlinOrionShutter(AbstractHardwarePlugin, ShutterPlugin):
    def __init__(self, *args, **kwargs):
        """
        """
        AbstractHardwarePlugin.__init__(self, *args, **kwargs)
        ShutterPlugin.__init__(self, *args, **kwargs)

    def _init(self):
        Logger().trace("MerlinOrionShutter._init()")
        AbstractHardwarePlugin._init(self)
        ShutterPlugin._init(self)
        self._hardware = MerlinOrionHardware()

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        ShutterPlugin._defineConfig(self)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._hardware.setOutput(True)

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._hardware.setOutput(False)

    def init(self):
        Logger().trace("MerlinOrionShutter.init()")
        self._hardware.setAxis(AXIS_TABLE[self.capacity]),
        AbstractHardwarePlugin.init(self)
        ShutterPlugin.init(self)

    def shutdown(self):
        Logger().trace("MerlinOrionShutter.shutdown()")
        self._triggerOffShutter()
        AbstractHardwarePlugin.shutdown(self)
        ShutterPlugin.shutdown(self)


class MerlinOrionShutterController(ShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


def register():
    """ Register plugins.
    """
    PluginsManager().register(MerlinOrionAxis, MerlinOrionAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(MerlinOrionAxis, MerlinOrionAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(MerlinOrionShutter, MerlinOrionShutterController, capacity='shutter', name=NAME)
