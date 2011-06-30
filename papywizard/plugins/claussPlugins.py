# -*- coding: utf-8 -*-

""" Clauss Head remote control.

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

 - ClaussAxis
 - ClaussAxisController
 - ClaussShutter
 - ClaussShutterController

@author: Martin Loyer
@copyright: (C) 2010-2011 Martin Loyer
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.hardware.claussHardware import ClaussHardware
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.shutterPlugin import ShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField


NAME = "Clauss"

AXIS_TABLE = {'yawAxis': 1,
              'pitchAxis': 2,
              'shutter': 0
              }

DEFAULT_FOCUS_ENABLE = False
DEFAULT_FOCUS_TIME = 1.5  # (s)
DEFAULT_DUAL_ENABLE = False
DEFAULT_DUAL_TIME = 2.  # (s)
DEFAULT_PARK_POSITION = "0."  # (°)
DEFAULT_SPEED_SLOW = 10  # (%)
DEFAULT_SPEED_NORMAL = 50  # (%)
DEFAULT_SPEED_FAST = 100  # (%)

TAB_SPECIAL = unicode(QtGui.QApplication.translate("claussPlugins", 'Special'))
LABEL_SPECIAL_FOCUS = unicode(QtGui.QApplication.translate("claussPlugins", "Auto Focus"))
LABEL_SPECIAL_FOCUS_TIME = unicode(QtGui.QApplication.translate("claussPlugins", "Focus time"))
LABEL_SPECIAL_DUAL = unicode(QtGui.QApplication.translate("claussPlugins", "Dual cameras"))
LABEL_SPECIAL_DUAL_TIME = unicode(QtGui.QApplication.translate("claussPlugins", "Time between shots"))
LABEL_SPECIAL_PARK_ENABLE = unicode(QtGui.QApplication.translate("claussPlugins", "Park head"))
LABEL_SPECIAL_PARK_POSITION = unicode(QtGui.QApplication.translate("claussPlugins", "Park position"))
LABEL_SPECIAL_SPEED_SLOW = unicode(QtGui.QApplication.translate("claussPlugins", "Slow speed"))
LABEL_SPECIAL_SPEED_NORMAL = unicode(QtGui.QApplication.translate("claussPlugins", "Normal speed"))
LABEL_SPECIAL_SPEED_FAST = unicode(QtGui.QApplication.translate("claussPlugins", "Fast speed"))


class ClaussAxis(AbstractHardwarePlugin, AbstractAxisPlugin):
    def _init(self):
        Logger().trace("ClaussAxis._init()")
        AbstractHardwarePlugin._init(self)
        AbstractAxisPlugin._init(self)
        self._hardware = ClaussHardware()

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_speedSlow', 'SPEED_SLOW', default=DEFAULT_SPEED_SLOW)
        self._addConfigKey('_speedNormal', 'SPEED_NORMAL', default=DEFAULT_SPEED_NORMAL)
        self._addConfigKey('_speedFast', 'SPEED_FAST', default=DEFAULT_SPEED_FAST)
        self._addConfigKey('_parkPosition', 'PARK_POSITION', default=DEFAULT_PARK_POSITION)
        if self.capacity == 'yawAxis':
            self._addConfigKey('_parkEnable', 'PARK_ENABLE', default=False)
        else:
            self._addConfigKey('_parkEnable', 'PARK_ENABLE', default=True)

    def __getSpeed(self):
        """ Return the speed value according to manual speed setting.

        @return: speed
        @rtype float
        """
        if self._manualSpeed == 'slow':
            speed = self._config['SPEED_SLOW']
        elif self._manualSpeed == 'normal':
            speed = self._config['SPEED_NORMAL']
        elif self._manualSpeed == 'fast':
            speed = self._config['SPEED_FAST']

        return speed

    def init(self):
        Logger().trace("ClaussAxis.init()")
        self._hardware.setAxis(AXIS_TABLE[self.capacity]),
        AbstractHardwarePlugin.init(self)

    def shutdown(self):
        Logger().trace("ClaussAxis.shutdown()")
        self.stop()
        if self._config['PARK_ENABLE']:
            self._hardware.drive(float(self._config['PARK_POSITION']), self.__getSpeed())
        AbstractHardwarePlugin.shutdown(self)
        AbstractAxisPlugin.shutdown(self)

    def read(self):
        pos = self._hardware.read() - self._offset
        return pos

    def drive(self, pos, useOffset=True, wait=True):
        Logger().debug("ClaussAxis.drive(): '%s' drive to %.1f" % (self.capacity, pos))
        currentPos = self.read()
        #Logger().debug("ClaussAxis.drive(): currentPos=%.1f" % currentPos)

        # checkLimits defined in Papywizard user conf (usually +360 - 360°)
        self._checkLimits(pos)

        if useOffset:
            pos += self._offset
            #Logger().debug("ClaussAxis.drive(): useOffset=True, pos=%.1f, offset=%.1f" % (pos, self._offset))

        # Only move if needed
        if abs(pos - currentPos) > 0. or not useOffset:
            #Logger().debug("ClaussAxis.drive(): Do move, pos=%.1f, currentPos=%.1f, useOffset=%s" % (pos, currentPos, useOffset))
            self._hardware.drive(pos, self.__getSpeed())

            # Wait end of movement
            if wait:
                self.waitEndOfDrive()

    def waitEndOfDrive(self):
        while self.isMoving():
            time.sleep(config.SPY_REFRESH_DELAY / 1000.)
        #self.waitStop()

    def startJog(self, dir_):

        # Restrict manual moving to high or low limit (user defined)
        if dir_ == '+':
            maxPos = -float(self._config['HIGH_LIMIT'])
        elif dir_ == '-':
            maxPos = float(self._config['LOW_LIMIT'])
        #Logger().debug("ClaussAxis.startJog(): maxPos=%s" % maxPos)
        self._hardware.startJog(dir_, self.__getSpeed(), maxPos)

    def stop(self):
        self.__driveFlag = False
        self._hardware.stop()
        self.waitStop()

    def waitStop(self):
        pass

    def isMoving(self):
        return self._hardware.isMoving()


class ClaussAxisController(AxisPluginController, HardwarePluginController):
    def _valueChanged(self, value=None):
        self.refreshView()

    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Special', TAB_SPECIAL)
        self._addWidget('Special', LABEL_SPECIAL_SPEED_SLOW, SpinBoxField, (1, 100, "", " %"), 'SPEED_SLOW')
        self._addWidget('Special', LABEL_SPECIAL_SPEED_NORMAL, SpinBoxField, (1, 100, "", " %"), 'SPEED_NORMAL')
        self._addWidget('Special', LABEL_SPECIAL_SPEED_FAST, SpinBoxField, (1, 100, "", " %"), 'SPEED_FAST')
        self._addWidget('Special', LABEL_SPECIAL_PARK_ENABLE, CheckBoxField, (), 'PARK_ENABLE')
        self._addWidget('Special', LABEL_SPECIAL_PARK_POSITION, ComboBoxField, (["-180.", "-90.", "0.", "90.", "180."],), 'PARK_POSITION')

    def refreshView(self):
        enable = self._getWidget('Special', LABEL_SPECIAL_PARK_ENABLE).value()
        self._getWidget('Special', LABEL_SPECIAL_PARK_POSITION).setDisabled(not enable)


class ClaussShutter(AbstractHardwarePlugin, ShutterPlugin):
    def _init(self):
        Logger().trace("ClaussShutter._init()")
        AbstractHardwarePlugin._init(self)
        ShutterPlugin._init(self)
        self._hardware = ClaussHardware()

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        ShutterPlugin._defineConfig(self)
        self._addConfigKey('_focus', 'FOCUS_ENABLE', default=DEFAULT_FOCUS_ENABLE)
        self._addConfigKey('_focus_time', 'FOCUS_TIME', default=DEFAULT_FOCUS_TIME)
        self._addConfigKey('_dual', 'DUAL_ENABLE' , default=DEFAULT_DUAL_ENABLE)
        self._addConfigKey('_dual_time', 'DUAL_TIME', default=DEFAULT_DUAL_TIME)

    def _triggerShutter(self, delay):
        """ Trigger the shutter contact.

        Note that FOCUS_ENABLE and DUAL_ENABLE options are exclusive (done via UI)

        @param delay: delay to wait between on/off, in s
        @type delay: float
        """
        Logger().trace("ClaussShutter._triggerShutter()")

        # Autofocus mode enable
        if self._config['FOCUS_ENABLE']:
            self._triggerAutoFocus()
            time.sleep(self._config['FOCUS_TIME'])

        # Shoot regular camera
        self._triggerOnShutter()
        time.sleep(delay)
        self._triggerOffShutter()

        # Dual camera mode
        if self._config['DUAL_ENABLE']:
            time.sleep(self._config['DUAL_TIME'])
            Logger().info("ClaussShutter._triggerShutter(): dual camera shoot")
            self._triggerAutoFocus()
            time.sleep(delay)
            self._triggerOffShutter()

        self._LastShootTime = time.time()

    def _triggerAutoFocus(self):
        """ Set the autofocus on.
        """
        self._hardware.setShutter("AF")

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._hardware.setShutter("ON")

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._hardware.setShutter("OFF")

    def init(self):
        Logger().trace("ClaussShutter.init()")
        self._hardware.setAxis(AXIS_TABLE[self.capacity]),
        AbstractHardwarePlugin.init(self)

    def shutdown(self):
        Logger().trace("ClaussShutter.shutdown()")
        self._triggerOffShutter()
        AbstractHardwarePlugin.shutdown(self)
        ShutterPlugin.shutdown(self)


class ClaussShutterController(ShutterPluginController, HardwarePluginController):
    def _valueChanged(self, value=None):
        ShutterPluginController._valueChanged(self, value)
        self.refreshView()

    def _defineGui(self):
        Logger().trace("ClaussShutter._defineGui()")
        ShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Special', TAB_SPECIAL)
        self._addWidget('Special', LABEL_SPECIAL_FOCUS, CheckBoxField, (), 'FOCUS_ENABLE')
        self._addWidget('Special', LABEL_SPECIAL_FOCUS_TIME, DoubleSpinBoxField, (0.1, 5., 1, 0.1, "", " s"), 'FOCUS_TIME')
        self._addWidget('Special', LABEL_SPECIAL_DUAL, CheckBoxField, (), 'DUAL_ENABLE')
        self._addWidget('Special', LABEL_SPECIAL_DUAL_TIME, DoubleSpinBoxField, (0.1, 9., 1, 0.1, "", " s"), 'DUAL_TIME')

    def refreshView(self):
        focus = self._getWidget('Special', LABEL_SPECIAL_FOCUS).value()
        dual = self._getWidget('Special', LABEL_SPECIAL_DUAL).value()

        self._getWidget('Special', LABEL_SPECIAL_FOCUS).setDisabled(dual)
        self._getWidget('Special', LABEL_SPECIAL_FOCUS_TIME).setDisabled(not focus)
        self._getWidget('Special', LABEL_SPECIAL_DUAL).setDisabled(focus)
        self._getWidget('Special', LABEL_SPECIAL_DUAL_TIME).setDisabled(not dual)

def register():
    """ Register plugins.
    """
    PluginsManager().register(ClaussAxis, ClaussAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(ClaussAxis, ClaussAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(ClaussShutter, ClaussShutterController, capacity='shutter', name=NAME)
