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

Plugins

Implements
==========

 - GphotoBracketShutter
 - GphotoBracketShutterController

@author: Jeongyun Lee
@author: Frédéric Mantegazza
@copyright: (C) 2010 Jeongyun Lee
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL

@todo: use a exposure bias instead of advanced params
"""

__revision__ = ""

import time
import subprocess

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import LineEditField, SpinBoxField, DoubleSpinBoxField, \
                                         CheckBoxField, FileSelectorField

NAME = "Gphoto Bracket"

DEFAULT_MIRROR_LOCKUP = False
DEFAULT_MIRROR_LOCKUP_COMMAND = "gphoto2 --capture-image"
DEFAULT_SHOOT_COMMAND = "gphoto2"
DEFAULT_BRACKETING_NBPICTS = 1
DEFAULT_BRACKETING_STEP = 1.

LABEL_SHOOT_COMMAND = QtGui.QApplication.translate("gphotoBracketPlugins", "Shoot command")
LABEL_CHOOSE_SHOOT_COMMAND = QtGui.QApplication.translate("gphotoBracketPlugins", "Choose shoot command...")  # or "Select gphoto2 path"?
LABEL_CHOOSE_SHOOT_COMMAND_FILTER = QtGui.QApplication.translate("gphotoBracketPlugins", "All files (*)")
LABEL_NB_PICTS = QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing nb picts")
LABEL_EV_STEP = QtGui.QApplication.translate("gphotoBracketPlugins", "Ev step")
LABEL_EV_LIST = QtGui.QApplication.translate("gphotoBracketPlugins", "Resulting Ev list")
LABEL_ADVANCED = QtGui.QApplication.translate("gphotoBracketPlugins", "Advanced")
LABEL_ADVANCED_TAB = QtGui.QApplication.translate("gphotoBracketPlugins", 'Advanced')
LABEL_PLUS_NB_PICTS = QtGui.QApplication.translate("gphotoBracketPlugins", "+ bracketing nb picts")
LABEL_PLUS_STEP = QtGui.QApplication.translate("gphotoBracketPlugins", "+ step")
LABEL_MINUS_NB_PICTS = QtGui.QApplication.translate("gphotoBracketPlugins", "- bracketing nb picts")
LABEL_MINUS_STEP = QtGui.QApplication.translate("gphotoBracketPlugins", "- step")


class GphotoBracketShutter(AbstractShutterPlugin):
    """ Tethered shooting plugin based on gphoto2.
    """
    def _init(self):
        self.__speedConfig = None
        self.__speedOrder = None
        self.__availableSpeeds = None
        self.__baseSpeedIndex = None
        self.__evSteps = None

    def _getTimeValue(self):
        return -1

    def _getMirrorLockup(self):
        return self._config['MIRROR_LOCKUP']

    def _getBracketingNbPicts(self):
        return self._config['BRACKETING_NB_PICTS']

    def _defineConfig(self):
        Logger().trace("GphotoBracketShutter._defineConfig()")
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_mirrorLockupCommand', 'MIRROR_LOCKUP_COMMAND', default=DEFAULT_MIRROR_LOCKUP_COMMAND)
        self._addConfigKey('_shootCommand', 'SHOOT_COMMAND', default=DEFAULT_SHOOT_COMMAND)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NBPICTS)
        self._addConfigKey('_bracketingEvStep', 'BRACKETING_EV_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingPlusNbPicts', 'BRACKETING_PLUS_NB_PICTS', default=int(DEFAULT_BRACKETING_NBPICTS / 2))
        self._addConfigKey('_bracketingMinusNbPicts', 'BRACKETING_MINUS_NB_PICTS', default=int(DEFAULT_BRACKETING_NBPICTS / 2))
        self._addConfigKey('_bracketingPlusStep', 'BRACKETING_PLUS_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingMinusStep', 'BRACKETING_MINUS_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingEvList', 'BRACKETING_EV_LIST', default="0")
        self._addConfigKey('_bracketingAdvanced', 'BRACKETING_ADVANCED', default=False)

    def __getEvOffset(self, bracketNumber):

        # bracketNumber out of self._config['BRACKETING_NB_PICTS']
        plusNbPicts = int(self._config['BRACKETING_PLUS_NB_PICTS'])
        minusNbPicts = int(self._config['BRACKETING_MINUS_NB_PICTS'])
        plusStep = self._config['BRACKETING_PLUS_STEP']
        minusStep = self._config['BRACKETING_MINUS_STEP']

        if bracketNumber <= minusNbPicts: # 1,2...minusNbPicts
            return (bracketNumber - minusNbPicts - 1) * minusStep
        elif bracketNumber >= (minusNbPicts + 2): # minusNbPicts + 2, +3... (minusNbPicts+plusNbPicts+1)
            return (bracketNumber - minusNbPicts - 1) * plusStep
        else:
            return 0

    def lockupMirror(self):
        """ @todo: implement mirror lockup command
        """
        Logger().debug("GphotoBracketShutter.lockupMirror(): execute command '%s'..." % self._config['MIRROR_LOCKUP_COMMAND'])
        time.sleep(1)
        Logger().debug("GphotoBracketShutter.lockupMirror(): command over")
        return 0

    def init(self):
        """ @todo: Move all this in futur start() callback?
        """

        # List config
        args = [self._config['SHOOT_COMMAND']]
        args.append("--list-config")
        Logger().debug("GphotoBracketShutter.init(): execute command '%s'..." % ' '.join(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if p.returncode != 0 and stderr:
            Logger().error("GphotoBracketShutter.init(): stderr:\n%s" % stderr.strip())
        Logger().debug("GphotoBracketShutter.init(): stdout:\n%s" % stdout.strip())

        for line in stdout.splitlines():
            if line.endswith('/shutterspeed'):  # or line.endswith('/exptime'):
                self.__speedConfig = line
            elif line.endswith('/exptime'):
                self.__speedConfig = line

        # Get config
        args = [self._config['SHOOT_COMMAND']]
        args.append("--get-config")
        args.append(self.__speedConfig)
        Logger().debug("GphotoBracketShutter.init(): execute command '%s'..." % ' '.join(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if p.returncode != 0 and stderr:
            Logger().error("GphotoBracketShutter.init(): stderr:\n%s" % stderr.strip())
        Logger().debug("GphotoBracketShutter.init(): stdout:\n%s" % stdout.strip())

        # Load all available speeds and the current speed
        self.__availableSpeeds = []
        for line in stdout.splitlines():
            tokens = line.split()
            if tokens[0] == 'Current:':
                self.__baseSpeed = tokens[1]
            elif tokens[0] == 'Choice:':
                self.__availableSpeeds.insert(int(tokens[1]), tokens[2])
                if self.__baseSpeed == tokens[2]:
                    self.__baseSpeedIndex = int(tokens[1])

        if float(self.__availableSpeeds[1]) > float(self.__availableSpeeds[2]):
            self.__speedOrder = 1.0 # slower speed first
        else:
            self.__speedOrder = -1.0 # faster speed first

        # Guess EV step (1/2, or 1/3)
        if float(self.__availableSpeeds[1]) / float(self.__availableSpeeds[3]) < 1.9:
            self.__evSteps = 3
        else:
            self.__evSteps = 2

        Logger().info("GphotoBracketShutter.init(): basespeed=%s config=%s order=%+g steps=1/%d" % \
                      (self.__baseSpeed, self.__speedConfig, self.__speedOrder, self.__evSteps))

    def shoot(self, bracketNumber):
        Logger().debug("GphotoBracketShutter.shoot(): bracketNumber=%d" % bracketNumber)

        evOffset = self.__getEvOffset(bracketNumber)

        speedIndex = self.__baseSpeedIndex - int(evOffset * self.__evSteps * self.__speedOrder)

        # see if shutter speed is out of range
        if self.__speedOrder > 0: # slow speed first
            if speedIndex < 1:
                speedIndex = 1
            elif speedIndex >= len(self.__availableSpeeds):
                speedIndex = len(self.__availableSpeeds) - 1
        elif self.__speedOrder < 0: # fast speed first
            if speedIndex < 0:
                speedIndex = 0
            elif speedIndex >= (len(self.__availableSpeeds) - 1):
                speedIndex = len(self.__availableSpeeds) - 2
        Logger().info("GphotoBracketShutter.shoot(): EV=%+d shutter speed=%s (1/%d steps)" % \
                      (int(evOffset), self.__availableSpeeds[speedIndex], self.__evSteps))

        # Capture image
        args = [self._config['SHOOT_COMMAND']]
        args.append("--set-config")
        args.append("%s=%s" % (self.__speedConfig, self.__availableSpeeds[speedIndex]))
        args.append("--capture-image")
        args.append("--set-config")
        args.append("%s=%s" % (self.__speedConfig, self.__baseSpeed))

        Logger().debug("GphotoBracketShutter.shoot(): execute command '%s'..." % ' '.join(args))

        if True:  # Set to False for tests
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait end of execution
            stdout, stderr = p.communicate()
            if p.returncode != 0 and stderr:
                Logger().error("GphotoBracketShutter.shoot(): stderr:\n%s" % stderr.strip())
            Logger().debug("GphotoBracketShutter.shoot(): stdout:\n%s" % stdout.strip())

            return p.returncode
        else:
            return 0


class GphotoBracketShutterController(ShutterPluginController):
    def _valueChanged(self, value=None):
        ShutterPluginController._valueChanged(self, value)

        advanced = self._getWidget('Main', LABEL_ADVANCED).value()
        if not advanced:
            halfNbPicts = (self._getWidget('Main', LABEL_NB_PICTS).value() - 1) / 2
            evStep = self._getWidget('Main', LABEL_EV_STEP).value()
            self._getWidget('Advanced', LABEL_PLUS_NB_PICTS).setValue(halfNbPicts)
            self._getWidget('Advanced', LABEL_MINUS_NB_PICTS).setValue(halfNbPicts)
            self._getWidget('Advanced', LABEL_PLUS_STEP).setValue(evStep)
            self._getWidget('Advanced', LABEL_MINUS_STEP).setValue(evStep)

        plusNbPicts = int(self._getWidget('Advanced', LABEL_PLUS_NB_PICTS).value())
        minusNbPicts = int(self._getWidget('Advanced', LABEL_MINUS_NB_PICTS).value())
        plusStep = int(self._getWidget('Advanced', LABEL_PLUS_STEP).value())
        minusStep = int(self._getWidget('Advanced', LABEL_MINUS_STEP).value())
        self._getWidget('Main', LABEL_NB_PICTS).setValue(1 + plusNbPicts + minusNbPicts)

        evList = []
        if minusNbPicts > 0:
            for i in range(-minusNbPicts, 0):
                evList.append("%+g" % (i * minusStep))
        evList.append("0")
        if plusNbPicts > 0:
            for i in range(1, plusNbPicts + 1):
                evList.append("%+g" % (i * plusStep))

        self._getWidget('Main', LABEL_EV_LIST).setValue(", ".join(evList))
        self._getWidget('Advanced', LABEL_EV_LIST).setValue(", ".join(evList))

        self.refreshView()

    def _defineGui(self):
        Logger().trace("GphotoBracketShutterController._defineGui()")
        ShutterPluginController._defineGui(self)

        # Main tab
        #self._addWidget('Main', QtGui.QApplication.translate("gphotoBracketPlugins", "Mirror lockup"),
                        #CheckBoxField, (), 'MIRROR_LOCKUP')
        #self._addWidget('Main', QtGui.QApplication.translate("gphotoBracketPlugins", "Mirror lockup command"),
                        #FileSelectorField,
                        #(QtGui.QApplication.translate("gphotoBracketPlugins", "Choose mirror lockup command..."),
                         #QtGui.QApplication.translate("gphotoBracketPlugins", "All files (*)")),
                        #'MIRROR_LOCKUP_COMMAND')
        self._addWidget('Main', LABEL_SHOOT_COMMAND,
                        FileSelectorField, (LABEL_CHOOSE_SHOOT_COMMAND, LABEL_CHOOSE_SHOOT_COMMAND_FILTER),
                        'SHOOT_COMMAND')
        self._addWidget('Main', LABEL_NB_PICTS, SpinBoxField, (1, 11), 'BRACKETING_NB_PICTS')
        self._getWidget('Main', LABEL_NB_PICTS).setSingleStep(2)
        self._addWidget('Main', LABEL_EV_STEP, DoubleSpinBoxField, (1.0, 5.0, 1, 1., "", " ev"), 'BRACKETING_EV_STEP')
        self._addWidget('Main', LABEL_EV_LIST, LineEditField, (), 'BRACKETING_EV_LIST')
        self._getWidget('Main', LABEL_EV_LIST).setReadOnly(True)
        self._addWidget('Main', LABEL_ADVANCED, CheckBoxField, (), 'BRACKETING_ADVANCED')

        # Advanced tab
        self._addTab('Advanced', LABEL_ADVANCED_TAB)
        self._addWidget('Advanced', LABEL_PLUS_NB_PICTS, SpinBoxField, (0, 11), 'BRACKETING_PLUS_NB_PICTS')
        self._addWidget('Advanced', LABEL_PLUS_STEP, DoubleSpinBoxField, (1.0, 5.0, 1, 1., "", " ev"), 'BRACKETING_PLUS_STEP')
        self._addWidget('Advanced', LABEL_MINUS_NB_PICTS, SpinBoxField, (0, 11), 'BRACKETING_MINUS_NB_PICTS')
        self._addWidget('Advanced', LABEL_MINUS_STEP, DoubleSpinBoxField, (1.0, 5.0, 1, 1., "", " ev"), 'BRACKETING_MINUS_STEP')
        self._addWidget('Advanced', LABEL_EV_LIST, LineEditField, (), 'BRACKETING_EV_LIST')
        self._getWidget('Advanced', LABEL_EV_LIST).setReadOnly(True)

    def refreshView(self):
        advanced = self._getWidget('Main', LABEL_ADVANCED).value()
        self._getWidget('Main', LABEL_NB_PICTS).setDisabled(advanced)
        self._getWidget('Main', LABEL_EV_STEP).setDisabled(advanced)
        self._setTabEnabled('Advanced', advanced)


def register():
    """ Register plugins.
    """
    PluginsManager().register(GphotoBracketShutter, GphotoBracketShutterController, capacity='shutter', name=NAME)
