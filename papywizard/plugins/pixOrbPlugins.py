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

DEFAULT_SPEED = 30.   # deg/s

ENCODER_FULL_CIRCLE = 1000000  # steps per turn
INITIAL_VELOCITY = 100  # in SPS
ACCELERATION = 100  # in steps
DECCELERATION =  100  # in steps
AXIS_NAME = {'yawAxis': 'B',
             'pitchAxis': 'C',
             'shutter': 'B'}
SPEED_INDEX = {'slow': 100,  # normal / 5
               'normal': 500,
               'fast': 1000}  # normal * 2


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
        return codPos * 360. / ENCODER_FULL_CIRCLE

    def _angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: int
        """
        return int(pos /360. * ENCODER_FULL_CIRCLE)

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
                while c  != '\r':
                    c = self._driver.read(1)
                    if c in ('#', '!', '$'):
                        raise IOError("Timeout on command '%s'" % cmd)
                    #elif c == '???':
                        #raise IOError("Unknown command '%s' (err=%s)" % (cmd, c))
                    answer += c

            except IOError:
                Logger().exception("PixOrbHardware._sendCmd")
                Logger().warning("PixOrbHardware._sendCmd(): %s axis %s failed to send command '%s'. Retrying..." % (NAME, AXIS_NAME[self.capacity], cmd))
            else:
                answer = answer.strip()  # remove final CRLF
                break
        else:
            raise HardwareError("%s axis %s can't send command '%s'" % (NAME, AXIS_NAME[self.capacity], cmd))
        #Logger().debug("PixOrbHardware._sendCmd(): axis %s, cmd=%s, ans=%s" % (AXIS_NAME[self.capacity], cmd, answer))

        return answer

    def _initPixOrb(self)  #, initVelocity, accel, decel):
        """ Init the PixOrb hardware.

        #@param initVelocity: initial velocity, in SPS
        #@type initVelocity: int

        #@param accel: acceleration, in steps
        #@type accel: int

        #@param decel: deceleration, in steps
        #@type decel: int

        Done only once per axis when connection is established.
        """
        self._driver.acquireBus()
        try:

            # Stop axis
            self._sendCmd("@")

            # Set initialVelocity
            self.sendCmd("I%d" % INITIAL_VELOCITY)

            # Set accel/decel
            self._sendCmd("K%d %d" % (ACCELERATION, DECELERATION))
        finally:
            self._driver.releaseBus()

    def _read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            answer = self._sendCmd("Z")
        finally:
            self._driver.releaseBus()
        axis, value = answer.split()
        pos = self._encoderToAngle(int(value))
        return pos

    def _drive(self, pos, speed):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float

        @param speed: speed, in °/s
        @type speed: float
        """
        strValue = self._angleToEncoder(pos)
        self._driver.acquireBus()
        try:
            self._sendCmd("V%d" % self._angleToEncoder(speed))
            self._sendCmd("R%+d" % self._angleToEncoder(pos))
        finally:
            self._driver.releaseBus()

    def _wait(self):
        """ Wait until motion is complete.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("W")
        finally:
            self._driver.releaseBus()

    def _stop(self):
        """ Stop the axis.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("@")
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
            if dir not in ('+', '-'):
                raise ValueError("Axis %d dir. must be in ('+', '-')" % AXIS_NAME[self.capacity])
            else:
                self._sendCmd("M%s%d" % (dir, speed))
        finally:
            self._driver.releaseBus()

    def _getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self._driver.acquireBus()
        try:
            return self._sendCmd("^")
        finally:
            self._driver.releaseBus()


class PixOrbAxis(PixOrbHardware, AbstractAxisPlugin):
    def __init__(self, *args, **kwargs):
        PixOrbHardware.__init__(self, *args, **kwargs)
        AbstractAxisPlugin.__init__(self, *args, **kwargs)

    def _init(self):
        Logger().trace("PixOrbAxis._init()")
        PixOrbHardware._init(self)
        AbstractAxisPlugin._init(self)

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_speed', 'SPEED', default=DEFAULT_SPEED)

    def activate(self):
        Logger().trace("PixOrbHardware.activate()")

    def deactivate(self):
        Logger().trace("PixOrbHardware.deactivate()")

    def init(self):
        Logger().trace("PixOrbAxis.init()")
        self._initPixOrb()  # initVelocity=, accel=, decel=)

    def shutdown(self):
        Logger().trace("PixOrbAxis.shutdown()")
        self.stop()

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
        self._drive(pos, self._config['SPEED'])

        # Wait end of movement
        if wait:
            self.waitEndOfDrive()

    def waitEndOfDrive(self):
        self._wait()
        #while self.isMoving():
            #time.sleep(0.1)
        self.waitStop()

    def startJog(self, dir_):
        self._startJog(dir_, SPEED_INDEX[self._manualSpeed])

    def stop(self):
        self.__driveFlag = False
        self._stop()
        self.waitStop()  # Really needed?

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
        axis, value = status.split()
        if value != '0':
            return True
        else:
            return False


class PixOrbAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', "Speed", SpinBoxField, (1, 99, "", " deg/s"), 'SPEED')


class PixOrbShutter(PixOrbHardware, AbstractStandardShutterPlugin):
    def _init(self):
        Logger().trace("PixOrbShutter._init()")
        PixOrbHardware._init(self)
        AbstractStandardShutterPlugin._init(self)

    def _defineConfig(self):
        PixOrbHardware._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._sendCmd("A8")

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._sendCmd("A0")

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
