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

- PixOrbHardware
- PixOrbAxis
- PixOrbAxisController
- PixOrbShutter
- PixOrbShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import sys
import threading

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.abstractStandardShutterPlugin import AbstractStandardShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.standardShutterPluginController import StandardShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

NAME = "PixOrb"

DEFAULT_ALTERNATE_DRIVE = True
DEFAULT_INERTIA_ANGLE = 1. # °

AXIS_NAME = {'yawAxis': 'A',
             'pitchAxis': 'B',
             'shutter': 'C'}
SPEED_INDEX = {'slow': 170,  # "AA0000"  / 5
               'alternate': 80, # "500000"
               'normal': 34, # "220000" nominal
               'fast': 17}   # "110000"  * 2


class PixOrbHardware(AbstractHardwarePlugin):
    """
    """
    def _init(self):
        Logger().trace("PixOrbHardware._init()")
        AbstractHardwarePlugin._init(self)

    def _encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        return (codPos - ENCODER_ZERO) * 360. / ENCODER_FULL_CIRCLE

    def _angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: int
        """
        return int(pos * ENCODER_FULL_CIRCLE / 360. + ENCODER_ZERO)

    def _sendCmd(self, cmd):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @return: answer
        @rtype: str
        """
        cmd = "%d%s" % (AXIS_NAME[self.capacity], cmd)
        for nbTry in xrange(3):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write("%s\n" % cmd)
                c = ''
                while c not in ('=', '!'):
                    c = self._driver.read(1)
                if c == '!':
                    c = self._driver.read(1) # Get error code
                    raise IOError("%s didn't understand the command '%s' (err=%s)" % (NAME, cmd, c))
                answer = ""
                while True:
                    c = self._driver.read(1)
                    if c == '\r':
                        break
                    answer += c

            except IOError:
                Logger().exception("PixOrbHardware._sendCmd")
                Logger().warning("PixOrbHardware._sendCmd(): axis %d can't sent command '%s'. Retrying..." % (NUM_AXIS[self.capacity], cmd))
            else:
                break
        else:
            raise HardwareError("PixOrb axis %d can't send command '%s'" % (NUM_AXIS[self.capacity], cmd))
        #Logger().debug("PixOrbHardware._sendCmd(): axis %d cmd=%s, ans=%s" % (NUM_AXIS[self.capacity], cmd, answer))

        return answer

    def _initPixOrb(self):
        """ Init the PixOrb hardware.

        Done only once per axis.
        """
        self._driver.acquireBus()
        try:

            # Stop axis
            self._sendCmd("@")
        finally:
            self._driver.releaseBus()

    def _read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            value = self._sendCmd("j")
        finally:
            self._driver.releaseBus()
        pos = self._encoderToAngle(value)
        return pos

    def _drive(self, pos):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float
        """
        strValue = self._angleToEncoder(pos)
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            self._sendCmd("G", "00")
            self._sendCmd("S", strValue)
            #self._sendCmd("I", self._encodeAxisValue(SPEED_INDEX[self._manualSpeed]))
            self._sendCmd("J")
        finally:
            self._driver.releaseBus()

    def _stop(self):
        """ Stop the axis.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
        finally:
            self._driver.releaseBus()

    def _startJog(self, dir_, speed):
        """ Start the axis.

        @param dir_: direction ('+', '-')
        @type dir_: str

        @param speed: speed
        @type speed: int
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            if dir_ == '+':
                self._sendCmd("G", "30")
            elif dir_ == '-':
                self._sendCmd("G", "31")
            else:
                raise ValueError("Axis %d dir. must be in ('+', '-')" % NUM_AXIS[self.capacity])
            self._sendCmd("I", self._encodeAxisValue(speed))
            self._sendCmd("J")
        finally:
            self._driver.releaseBus()

    def _getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self._driver.acquireBus()
        try:
            return self._sendCmd("f")
        finally:
            self._driver.releaseBus()


class PixOrbAxis(PixOrbHardware, AbstractAxisPlugin, QtCore.QThread):
    def __init__(self, *args, **kwargs):
        PixOrbHardware.__init__(self, *args, **kwargs)
        AbstractAxisPlugin.__init__(self, *args, **kwargs)
        QtCore.QThread.__init__(self)

    def _init(self):
        Logger().trace("PixOrbAxis._init()")
        PixOrbHardware._init(self)
        AbstractAxisPlugin._init(self)
        self.__run = False
        self.__driveFlag = False
        self.__setPoint = None

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_alternateDrive', 'ALTERNATE_DRIVE', default=DEFAULT_ALTERNATE_DRIVE)
        self._addConfigKey('_inertiaAngle', 'INERTIA_ANGLE', default=DEFAULT_INERTIA_ANGLE)

    def activate(self):
        Logger().trace("PixOrbHardware.activate()")

        # Start the thread
        self.start()

    def deactivate(self):
        Logger().trace("PixOrbHardware.deactivate()")

        # Stop the thread
        self._stopThread()
        self.wait()

    def init(self):
        Logger().trace("PixOrbAxis.init()")
        self._initPixOrb()

    def shutdown(self):
        Logger().trace("PixOrbAxis.shutdown()")
        self.stop()

    def run(self):
        """ Main entry of the thread.
        """
        threadName = "%s_%s" % (self.name, self.capacity)
        threading.currentThread().setName(threadName)
        Logger().debug("PixOrbAxis.run(): start thread")
        self.__run = True
        while self.__run:
            if self.__driveFlag:

                # Choose alternate drive if needed
                currentPos = self.read()
                if self._config['ALTERNATE_DRIVE'] and \
                   1.1 * self._config['INERTIA_ANGLE'] < abs(self.__setPoint - currentPos) < ALTERNATE_DRIVE_ANGLE:
                    self._alternateDrive(self.__setPoint)
                else:
                    self._directDrive(self.__setPoint)
                self.__driveFlag = False
                self.waitEndOfDrive()

            self.msleep(config.SPY_REFRESH_DELAY)

        Logger().debug("PixOrbAxis.run(): thread terminated")

    def _stopThread(self):
        """ Stop the thread.
        """
        self.__run = False

    def read(self):
        pos = self._read() - self._offset
        return pos

    def drive(self, pos, inc=False, useOffset=True, wait=True):
        currentPos = self.read()

        # Compute absolute position from increment if needed
        if inc:
            pos += currentPos
        else:
            if useOffset:
                pos += self._offset

        self._checkLimits(pos)

        # Only move if needed
        if abs(pos - currentPos) > AXIS_ACCURACY:
            self.__setPoint = pos
            self.__driveFlag = True # Start thread action

            # Wait end of movement
            if wait:
                self.waitEndOfDrive()

    def _directDrive(self, pos):
        """ Default (hardware) drive.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("PixOrbAxis._directDrive()")
        self._drive(pos)

    def _alternateDrive(self, pos):
        """ Alternate drive.

        This method implements an external closed-loop regulation.
        It is faster for angles < 6-7°, because in this case, the
        head does not accelerate to full speed, but rather stays at
        very low speed.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("PixOrbAxis._alternateDrive()")

        # Compute initial direction
        currentPos = self.read()
        if pos > currentPos:
            dir_ = '+'
        else:
            dir_ = '-'
        stopRequest = False

        # Alternate speed move
        Logger().debug("PixOrbAxis._alternateDrive(): alternate speed move")
        self._startJog(dir_, SPEED_INDEX['alternate'])

        # Check when stop
        while abs(pos - self.read()) > self._config['INERTIA_ANGLE']: # adjust inertia while moving?

            # Test if a stop request has been sent
            if not self.isMoving():
                stopRequest = True
                break
            time.sleep(0.1)
        self._stop()

        # Final move
        if abs(pos - self.read()) > AXIS_ACCURACY and not stopRequest:
            Logger().debug("PixOrbAxis._alternateDrive(): final move")
            self._drive(pos)

    def waitEndOfDrive(self):
        while True:
            if not self.isMoving():
                break
            time.sleep(0.1)
        self.waitStop()

    def startJog(self, dir_):
        self._startJog(dir_, SPEED_INDEX[self._manualSpeed])

    def stop(self):
        self.__driveFlag = False
        self._stop()
        self.waitStop()

    def waitStop(self):
        pos = self.read()
        time.sleep(0.05)
        while True:
            if round(abs(pos - self.read()), 1) == 0:
                break
            pos = self.read()
            time.sleep(0.05)

    def isMoving(self):
        status = self._getStatus()
        if status[1] != '0' or self.__driveFlag:
            return True
        else:
            return False


class PixOrbAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Controller')
        self._addWidget('Controller', "Axis name", LineEditField, (), 'AXIS_NAME')


class PixOrbShutter(PixOrbHardware, AbstractStandardShutterPlugin):
    def _init(self):
        Logger().trace("PixOrbShutter._init()")
        PixOrbHardware._init(self)
        AbstractStandardShutterPlugin._init(self)
        self._numAxis = 1 # shutter contact is connected on axis

    def _defineConfig(self):
        PixOrbHardware._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._sendCmd("O", "1")

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._sendCmd("O", "0")

    def activate(self):
        Logger().trace("PixOrbShutter.activate()")

    def deactivate(self):
        Logger().trace("PixOrbShutter.deactivate()")

    def init(self):
        Logger().trace("PixOrbShutter.init()")
        self._initPixOrb()

    def shutdown(self):
        Logger().trace("PixOrbShutter.shutdown()")
        self._triggerOffShutter()


class PixOrbShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


def register():
    """ Register plugins.
    """
    PluginsManager().register(PixOrbAxis, PixOrbAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(PixOrbAxis, PixOrbAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(PixOrbShutter, PixOrbShutterController, capacity='shutter', name=NAME)
