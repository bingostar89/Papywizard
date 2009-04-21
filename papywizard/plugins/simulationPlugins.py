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

Plugins

Implements
==========

- SimulationAxis
- SimulationAxisController
- SimulationYawAxis
- SimulationYawAxisController
- SimulationPitchAxis
- SimulationPitchAxisController
- SimulationShutter
- SimulationShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import threading

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.pluginManager import PluginManager
from papywizard.hardware.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.hardware.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.controller.axisPluginController import AxisPluginController
from papywizard.controller.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

DEFAULT_SPEED = 15. # deg/s
DEFAULT_TIME_VALUE = 0.5 # s
DEFAULT_MIRROR_LOCKUP = False
DEFAULT_BRACKETING_NBPICTS = 1
DEFAULT_BRACKETING_INTENT = 'exposure'
MANUAL_SPEED = {'slow': .2,
                'normal': 1.,
                'fast': 2.}


class SimulationAxis(AbstractAxisPlugin, QtCore.QThread):
    """ Simulated hardware axis.
    """
    _name = "Simulation"

    def __init__(self):
        AbstractAxisPlugin.__init__(self)
        QtCore.QThread.__init__(self)

    def _init(self):
        AbstractAxisPlugin._init(self)
        self.__pos = 0.
        self.__jog = False
        self.__drive = False
        self.__setpoint = None
        self.__dir = None
        self.__time = None
        self.__run = False

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        self._addConfigKey('_speed', 'SPEED', default=DEFAULT_SPEED)

    def activate(self):
        Logger().trace("SimulationAxis.activate()")

        # Start the thread
        self.start()

    def shutdown(self):
        Logger().trace("SimulationAxis.shutdown()")

        # Stop the thread
        self._stopThread()

    def run(self):
        """ Main entry of the thread.
        """
        threadName = "%s_%s" % (self.name, self.capacity)
        Logger().debug("SimulationAxis.run(): start '%s' thread" % threadName)
        threading.currentThread().setName(threadName)
        self.__run = True
        while self.__run:

            # Jog command
            if self.__jog:
                if self.__time == None:
                    self.__time = time.time()
                else:
                    if self.__drive:
                        inc = (time.time() - self.__time) * self._config['SPEED']
                    else:
                        inc = (time.time() - self.__time) * self._config['SPEED'] * MANUAL_SPEED[self._manualSpeed]
                    self.__time = time.time()
                    if self.__dir == '+':
                        self.__pos += inc
                    elif self.__dir == '-':
                        self.__pos -= inc
                    #Logger().debug("SimulationAxis.run(): '%s' inc=%.1f, new __pos=%.1f" % (self.capacity, inc, self.__pos))
            else:
                self.__time = None

            # Drive command. Check when stop
            if self.__drive:
                #Logger().trace("SimulationAxis.run(): '%s' driving" % self.capacity)
                if self.__dir == '+':
                    if self.__pos >= self.__setpoint:
                        self.__jog = False
                        self.__drive = False
                        self.__pos = self.__setpoint
                elif self.__dir == '-':
                    if self.__pos <= self.__setpoint:
                        self.__jog = False
                        self.__drive = False
                        self.__pos = self.__setpoint

            self.msleep(config.SPY_REFRESH_DELAY)

        Logger().debug("SimulationAxis.run(): axis simulation thread terminated")

    def _stopThread(self):
        """ Stop the thread.
        """
        self.__run = False

    def read(self):
        return self.__pos - self._offset

    def drive(self, pos, inc=False, useOffset=True, wait=True):
        Logger().debug("SimulationAxis.drive(): '%s' drive to %.1f" % (self.capacity, pos))

        # Compute absolute position from increment if needed
        if inc:
            self.__setpoint = self.__pos + inc
        else:
            if useOffset:
                self.__setpoint = pos + self._offset
            else:
                self.__setpoint = pos

        self._checkLimits(self.__setpoint)

        # Drive to requested position
        if self.__setpoint > self.__pos:
            self.__dir = '+'
        elif self.__setpoint < self.__pos:
            self.__dir = '-'
        else:
            return
        self.__drive = True
        self.__jog = True

        # Wait end of movement
        if wait:
            self.waitEndOfDrive()

    def stop(self):
        self.__jog = False
        self.__drive = False

    def waitEndOfDrive(self):
        while self.__drive:
            time.sleep(0.1)

    def startJog(self, dir_):
        #Logger().debug("SimulationAxis.startJog(): '%s' axis dir_=%s" % (self.capacity, dir_))
        self.__dir = dir_
        self.__jog = True

    def waitStop(self):
        pass

    def isMoving(self):
        return self.__jog

    def setManualSpeed(self, speed):
        self._manualSpeed = speed


class SimulationAxisController(AxisPluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        self._addWidget('Main', "Speed", SpinBoxField, (5, 25, "", " deg/s"), 'SPEED')


class SimulationYawAxis(SimulationAxis):
    _capacity = 'yawAxis'


class SimulationYawAxisController(SimulationAxisController):
    pass


class SimulationPitchAxis(SimulationAxis):
    _capacity = 'pitchAxis'


class SimulationPitchAxisController(SimulationAxisController):
    pass


class SimulationShutter(AbstractShutterPlugin):
    _name = "Simulation"

    def _init(self):
        pass

    def _getTimeValue(self):
        return self._config['TIME_VALUE']

    def _getMirrorLockup(self):
        return self._config['MIRROR_LOCKUP']

    def _getBracketingNbPicts(self):
        return self._config['BRACKETING_NB_PICTS']

    def _getBracketingIntent(self):
        return self._config['BRACKETING_INTENT']

    def _defineConfig(self):
        AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_timeValue', 'TIME_VALUE', default=DEFAULT_TIME_VALUE)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NBPICTS)
        self._addConfigKey('_bracketingIntent', 'BRACKETING_INTENT', default=DEFAULT_BRACKETING_INTENT)

    def activate(self):
        pass

    def shutdown(self):
        pass

    def lockupMirror(self):
        """ Lockup the mirror.
        """
        Logger().trace("SimulationShutter.lockupMirror()")
        time.sleep(.2)
        return 0

    def shoot(self, bracketNumber):
        """ Shoot.
        """
        Logger().trace("SimulationShutter.shoot()")
        time.sleep(self.timeValue)
        return 0


class SimulationShutterController(ShutterPluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        self._addWidget('Main', "Time value", DoubleSpinBoxField, (0.1, 3600, 1, 0.1, "", " s"), 'TIME_VALUE')
        self._addWidget('Main', "Mirror lockup", CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', "Bracketing nb picts", SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')
        self._addWidget('Main', "Bracketing intent", ComboBoxField, (['exposure', 'focus', 'white balance', 'movement'],), 'BRACKETING_INTENT')


def register():
    """ Register plugins.
    """
    PluginManager().register(SimulationYawAxis, SimulationYawAxisController)
    PluginManager().register(SimulationPitchAxis, SimulationPitchAxisController)
    PluginManager().register(SimulationShutter, SimulationShutterController)
