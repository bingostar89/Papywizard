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

from PyQt4 import QtCore, QtGui

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

DEFAULT_SPEED_TABLE_INDEX = 9
DEFAULT_AXIS_WITH_BREAK = False

ENCODER_FULL_CIRCLE = 1000000  # steps per turn
AXIS_TABLE = {'yawAxis': 'B',
              'pitchAxis': 'C',
              'shutter': 'B'
              }
BREAK_TABLE = {'yawAxis': 'A',
               'pitchAxis': 'C'
               }
SPEED_TABLE = { 1: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider': 160},  #  1 rev/day
                2: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider':  80},  #  2 rev/day
                3: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider':  40},  #  6 rev/day
                4: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':  20},  #  1 rev/h
                5: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':  10},  #  2 rev/h
                6: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':   6},  #  5 rev/h
                7: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   5},  #  1 °/s
                8: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   4},  #  3 °/s
                9: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   3},  #  6 °/s
               10: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   1}   # 12 °/s
               }
MANUAL_SPEED_TABLE = {'slow': 7,  # normal / 5
                      'normal': 9,
                      'fast': 10  # normal * 2
                      }


class AbstractPixOrbHardware(AbstractHardwarePlugin):
    __initSIN11 = False

    def establishConnection(self):
        """ Establish the connection.

        The SIN-11 device used to control the Pixorb axis needs to be
        initialised before any command can be sent to the axis controllers.
        """
        AbstractHardwarePlugin.establishConnection(self)
        Logger().trace("AbstractPixOrbHardware.establishConnection()")
        if not AbstractPixOrbHardware.__initSIN11:
            answer = ""
            self._driver.empty()
            self._driver.write('&\n')
            c = ''
            while c != '\n':
                c = self._driver.read(1)
                if c == '?':
                    self._driver.read(1)  # Read last CR. Or is it CRLF?
                    raise HardwareError("Can't init SIN-11")
                else:
                    answer += c
            answer = answer.strip()  # remove final CR
            Logger().debug("AbstractPixOrbHardware.establishConnection(): SIN-11 '&' answer=%s" % answer)
            AbstractPixOrbHardware.__initSIN11 = True


class PixOrbHardware(AbstractPixOrbHardware):
    """
    """
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
        return int(pos / 360. * ENCODER_FULL_CIRCLE)

    def _sendCmd(self, cmd, table=AXIS_TABLE):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @param table: controller name table to use for this command
        @type table: dict

        @return: answer
        @rtype: str
        """
        cmd = "%s%s" % (table[self.capacity], cmd)
        for nbTry in xrange(3):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write("%s\n" % cmd)
                c = ''
                while c != '\r':
                    c = self._driver.read(1)
                    if c in ('#', '!', '$'):
                        self._driver.read(1)  # Read last CR. Or is it CRLF?
                        raise IOError("Error on command '%s'" % cmd)
                    else:
                        answer += c

            except IOError:
                Logger().exception("PixOrbHardware._sendCmd")
                Logger().warning("PixOrbHardware._sendCmd(): %s axis %s failed to send command '%s'. Retrying..." % (NAME, AXIS_TABLE[self.capacity], cmd))
            else:
                answer = answer.strip()  # remove final CRLF
                break
        else:
            raise HardwareError("%s axis %s can't send command '%s'" % (NAME, AXIS_TABLE[self.capacity], cmd))
        #Logger().debug("PixOrbHardware._sendCmd(): axis %s, cmd=%s, ans=%s" % (AXIS_TABLE[self.capacity], cmd, answer))

        return answer

    def _configurePixOrb(self, speedTableIndex):
        """ Configure the PixOrb hardware.

        @param speedTableIndex: speed params table index
        @type speedTableIndex: int
        """
        self._driver.acquireBus()
        try:

            # Set initial velocity
            self._sendCmd("I%d" % SPEED_TABLE[speedTableIndex]['initVelocity'])

            # Set accel/decel
            self._sendCmd("K%d %d" % (SPEED_TABLE[speedTableIndex]['accel'], SPEED_TABLE[speedTableIndex]['decel']))

            # Set slew speed
            self._sendCmd("V%d" % SPEED_TABLE[speedTableIndex]['slewSpeed'])

            # Set divider
            self._sendCmd("D%d" % SPEED_TABLE[speedTableIndex]['divider'])
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

    def _drive(self, pos):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float
        """
        strValue = self._angleToEncoder(pos)
        self._driver.acquireBus()
        try:
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
            if dir_ not in ('+', '-'):
                raise ValueError("%s axis %d dir. must be in ('+', '-')" % (NAME, AXIS_TABLE[self.capacity]))
            else:
                self._sendCmd("M%s%d" % (dir_, speed))
        finally:
            self._driver.releaseBus()

    def _releaseBreak(self):
        """ Release the (opional) break.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("A8", table=BREAK_TABLE)
        finally:
            self._driver.releaseBus()

    def _activateBreak(self):
        """ Release the (opional) break.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("A0", table=BREAK_TABLE)
        finally:
            self._driver.releaseBus()

    def _getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self._driver.acquireBus()
        try:
            status = self._sendCmd("^")
        finally:
            self._driver.releaseBus()
        axis, value = status.split()
        return value


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
        self._addConfigKey('_speedTableIndex', 'SPEED_TABLE_INDEX', default=DEFAULT_SPEED_TABLE_INDEX)
        self._addConfigKey('_axisWithBreak', 'AXIS_WITH_BREAK', default=DEFAULT_AXIS_WITH_BREAK)

    def init(self):
        Logger().trace("PixOrbAxis.init()")
        AbstractAxisPlugin.init(self)
        self.configure()

    def shutdown(self):
        Logger().trace("PixOrbAxis.shutdown()")
        self.stop()
        AbstractAxisPlugin.shutdown(self)

    def configure(self):
        Logger().trace("PixOrbAxis.configure()")
        AbstractAxisPlugin.configure(self)
        self._configurePixOrb(self._config['SPEED_TABLE_INDEX'])

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
        if self._config['AXIS_WITH_BREAK']:
            self._releaseBreak()
        self._drive(pos)

        # Wait end of movement
        if wait:
            self.waitEndOfDrive()

    def waitEndOfDrive(self):
        #self._wait()
        while self.isMoving():
            time.sleep(0.1)
        self.waitStop()

    def startJog(self, dir_):
        if self._config['AXIS_WITH_BREAK']:
            self._releaseBreak()
        self._startJog(dir_, MANUAL_SPEED_TABLE[self._manualSpeed])

    def stop(self):
        self.__driveFlag = False
        self._stop()
        self.waitStop()

    def waitStop(self):
        if self._config['AXIS_WITH_BREAK']:
            self._activateBreak()

    def isMoving(self):
        status = self._getStatus()
        if status != '0':
            return True
        else:
            return False


class PixOrbAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', QtGui.QApplication.translate("PixOrbAxisController", "Speed table index"),
                        SpinBoxField, (1, 10, "", ""), 'SPEED_TABLE_INDEX')
        self._addTab('Hard', QtGui.QApplication.translate("PixOrbAxisController", 'Hard'))
        self._addWidget('Hard', QtGui.QApplication.translate("PixOrbAxisController", "Axis with break"),
                        CheckBoxField, (), 'AXIS_WITH_BREAK')


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
        self._driver.acquireBus()
        try:
            self._sendCmd("A8")
        finally:
            self._driver.releaseBus()

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("A0")
        finally:
            self._driver.releaseBus()

    def shutdown(self):
        Logger().trace("PixOrbShutter.shutdown()")
        self._triggerOffShutter()
        AbstractStandardShutterPlugin.shutdown(self)


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
