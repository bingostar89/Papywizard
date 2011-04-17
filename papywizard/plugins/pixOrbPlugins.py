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

 - AbstractPixOrbHardware
 - PixOrbAxis
 - PixOrbAxisController
 - PixOrbShutter
 - PixOrbShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.pixOrbHardware import PixOrbHardware
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.shutterPlugin import ShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import SpinBoxField, DoubleSpinBoxField, CheckBoxField

NAME = "PixOrb"

DEFAULT_SPEED_INDEX = 9
DEFAULT_AXIS_WITH_BREAK = False
DEFAULT_AXIS_ACCURACY = 0.1  # °

LABEL_SPEED_INDEX = unicode(QtGui.QApplication.translate("pixOrbPlugins", "Speed index"))

TAB_HARD = unicode(QtGui.QApplication.translate("pixOrbPlugins", 'Hard'))
LABEL_AXIS_WITH_BREAK = unicode(QtGui.QApplication.translate("pixOrbPlugins", "Axis with break"))
LABEL_AXIS_ACCURACY = unicode(QtGui.QApplication.translate("pixOrbPlugins", "Axis accuracy"))

SIN11_INIT_TIMEOUT = 10.
AXIS_TABLE = {'yawAxis': 'B',
              'pitchAxis': 'C',
              'shutter': 'B'
              }
BREAK_TABLE = {'yawAxis': 'A',
               'pitchAxis': 'C'
               }
MANUAL_SPEED_TABLE = {'slow': 7,  # normal / 6
                      'normal': 9,
                      'fast': 10  # normal * 2
                      }


class AbstractPixOrbHardware(AbstractHardwarePlugin):
    __initSIN11 = False

    def establishConnection(self):  # Move to hardware?
        """ Establish the connection.

        The SIN-11 device used to control the Pixorb axis needs to be
        initialised before any command can be sent to the axis controllers.
        """
        AbstractHardwarePlugin.establishConnection(self)
        Logger().trace("AbstractPixOrbHardware.establishConnection()")
        if not AbstractPixOrbHardware.__initSIN11:
            try:
                answer = ""
                self._driver.empty()

                # Ask the SIN-11 to scan online controllers
                self._driver.write('&')  # Add '\n' if ethernet driver?
                self._driver.setTimeout(SIN11_INIT_TIMEOUT)  # Sin-11 takes several seconds to answer
                c = ''
                while c != '\r':
                    c = self._driver.read(1)
                    if c in ('#', '?'):
                        self._driver.read(2)  # Read last CRLF
                        Logger().debug("AbstractPixOrbHardware.establishConnection(): SIN-11 '&' answer=%s" % answer)
                        raise HardwareError("Can't init SIN-11")
                    else:
                        answer += c
                answer = answer.strip()  # Remove final CRLF
                Logger().debug("AbstractPixOrbHardware.establishConnection(): SIN-11 '&' answer=%s" % answer)
                AbstractPixOrbHardware.__initSIN11 = True
                self._driver.setTimeout(ConfigManager().getFloat('Plugins/HARDWARE_COM_TIMEOUT'))
            except:
                self._connected = False
                raise


class PixOrbAxis(AbstractPixOrbHardware, AbstractAxisPlugin):
    def _init(self):
        Logger().trace("PixOrbAxis._init()")
        AbstractPixOrbHardware._init(self)
        AbstractAxisPlugin._init(self)
        self._hardware = PixOrbHardware()

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_speedIndex', 'SPEED_INDEX', default=DEFAULT_SPEED_INDEX)
        self._addConfigKey('_axisWithBreak', 'AXIS_WITH_BREAK', default=DEFAULT_AXIS_WITH_BREAK)
        self._addConfigKey('_axisAccuracy', 'AXIS_ACCURACY', default=DEFAULT_AXIS_ACCURACY)

    def init(self):
        Logger().trace("PixOrbAxis.init()")
        self._hardware.setAxis(AXIS_TABLE[self.capacity])
        self._hardware.setBreakAxis(BREAK_TABLE[self.capacity])
        AbstractHardwarePlugin.init(self)
        self.configure()

    def shutdown(self):
        Logger().trace("PixOrbAxis.shutdown()")
        self.stop()
        AbstractAxisPlugin.shutdown(self)

    def configure(self):
        Logger().trace("PixOrbAxis.configure()")
        AbstractAxisPlugin.configure(self)
        self._hardware.configure(self._config['SPEED_INDEX'])

    def read(self):
        position = self._hardware.read()

        # Reverse direction on yaw axis
        if self.capacity == 'yawAxis':
            position *= -1

        position -= self._offset

        return position

    def drive(self, position, useOffset=True, wait=True):
        Logger().debug("PixOrbAxis.drive(): '%s' drive to %.1f" % (self.capacity, position))

        currentPos = self.read()
        if abs(position - currentPos) <= self._config['AXIS_ACCURACY'] or not useOffset:
            return

        self._checkLimits(position)

        if useOffset:
            position += self._offset

        # Reverse direction on yaw axis
        if self.capacity == 'yawAxis':
            position *= -1

        if self._config['AXIS_WITH_BREAK']:
            self._hardware.releaseBreak()
        self._hardware.configure(self._config['SPEED_INDEX'])
        self._hardware.drive(position)

        # Wait end of movement
        if wait:
            self.waitEndOfDrive()

    def waitEndOfDrive(self):
        #self._wait()
        while self.isMoving():
            time.sleep(config.SPY_REFRESH_DELAY / 1000.)
        self.waitStop()

    def startJog(self, dir_):

        # Reverse direction on yaw axis
        if self.capacity == 'yawAxis':
            if dir_ == '+':
                dir_ = '-'
            else:
                dir_ = '+'

        if self._config['AXIS_WITH_BREAK']:
            self._hardware.releaseBreak()
        self._hardware.configure(MANUAL_SPEED_TABLE[self._manualSpeed])
        self._hardware.startJog(dir_, MANUAL_SPEED_TABLE[self._manualSpeed])

    def stop(self):
        self._hardware.stop()
        self.waitStop()

    def waitStop(self):
        if self._config['AXIS_WITH_BREAK']:
            self._hardware.activateBreak()

    def isMoving(self):
        status = self._hardware.getStatus()
        if status != '0':
            return True
        else:
            return False


class PixOrbAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', LABEL_SPEED_INDEX, SpinBoxField, (1, 10, "", ""), 'SPEED_INDEX')
        self._addTab('Hard', TAB_HARD)
        self._addWidget('Hard', LABEL_AXIS_WITH_BREAK, CheckBoxField, (), 'AXIS_WITH_BREAK')
        self._addWidget('Hard', LABEL_AXIS_ACCURACY, DoubleSpinBoxField, (0.01, 0.50, 2, 0.01, "", u" °"), 'AXIS_ACCURACY')


class PixOrbShutter(AbstractPixOrbHardware, ShutterPlugin):
    def _init(self):
        Logger().trace("PixOrbShutter._init()")
        AbstractPixOrbHardware._init(self)
        ShutterPlugin._init(self)
        self._hardware = PixOrbHardware()

    def _defineConfig(self):
        AbstractPixOrbHardware._defineConfig(self)
        ShutterPlugin._defineConfig(self)

    def init(self):
        Logger().trace("PixOrbAxis.init()")
        self._hardware.setAxis(AXIS_TABLE[self.capacity])
        #self._hardware.setBreakAxis(BREAK_TABLE[self.capacity])
        AbstractHardwarePlugin.init(self)
        self.configure()

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._hardware.setOutput(True)

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._hardware.setOutput(False)

    def shutdown(self):
        Logger().trace("PixOrbShutter.shutdown()")
        self._triggerOffShutter()
        ShutterPlugin.shutdown(self)


class PixOrbShutterController(ShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


def register():
    """ Register plugins.
    """
    PluginsManager().register(PixOrbAxis, PixOrbAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(PixOrbAxis, PixOrbAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(PixOrbShutter, PixOrbShutterController, capacity='shutter', name=NAME)
