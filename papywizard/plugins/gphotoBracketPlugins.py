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
"""

__revision__ = ""

import time
import subprocess
import os.path

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import LineEditField, SpinBoxField, DirSelectorField, \
                                         CheckBoxField, FileSelectorField, ComboBoxField

NAME = "Gphoto Bracket"

DEFAULT_MIRROR_LOCKUP = False
DEFAULT_MIRROR_LOCKUP_COMMAND = "gphoto2 --capture-image"
DEFAULT_GPHOTO_COMMAND = "gphoto2"
DEFAULT_BRACKETING_NBPICTS = 1
DEFAULT_BRACKETING_STEP = 1.

LABEL_GPHOTO_COMMAND = QtGui.QApplication.translate("gphotoBracketPlugins", "gPhoto command")
TEXT_CHOOSE_GPHOTO_COMMAND = QtGui.QApplication.translate("gphotoBracketPlugins", "Choose gphoto2 command...")  # or "Select gphoto2 path"?
TEXT_CHOOSE_GPHOTO_COMMAND_FILTER = QtGui.QApplication.translate("gphotoBracketPlugins", "gphoto2 (gphoto2);;All files (*)")
LABEL_NB_PICTS = QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing nb picts")
LABEL_EV_STEP = QtGui.QApplication.translate("gphotoBracketPlugins", "Ev step")
LABEL_EV_BIAS = QtGui.QApplication.translate("gphotoBracketPlugins", "Exposure bias")
LABEL_EV_LIST = QtGui.QApplication.translate("gphotoBracketPlugins", "Resulting Ev list")
LABEL_ADVANCED = QtGui.QApplication.translate("gphotoBracketPlugins", "Advanced")

LABEL_ADVANCED_TAB = QtGui.QApplication.translate("gphotoBracketPlugins", 'Advanced')
LABEL_PLUS_NB_PICTS = QtGui.QApplication.translate("gphotoBracketPlugins", "+ bracketing nb picts")
LABEL_PLUS_STEP = QtGui.QApplication.translate("gphotoBracketPlugins", "+ step")
LABEL_MINUS_NB_PICTS = QtGui.QApplication.translate("gphotoBracketPlugins", "- bracketing nb picts")
LABEL_MINUS_STEP = QtGui.QApplication.translate("gphotoBracketPlugins", "- step")

LABEL_DOWNLOAD_TAB = QtGui.QApplication.translate("gphotoBracketPlugins", 'Download')
LABEL_DOWNLOAD_ENABLED = QtGui.QApplication.translate("gphotoBracketPlugins", 'Download')
LABEL_DOWNLOAD_DIR = QtGui.QApplication.translate("gphotoBracketPlugins", "Download directory")
#LABEL_DOWNLOAD_FILENAME = QtGui.QApplication.translate("gphotoBracketPlugins", "File name")
#DEFAULT_DOWNLOAD_FILENAME = QtGui.QApplication.translate("gphotoBracketPlugins", "Use camera default")
LABEL_DOWNLOAD_WHEN = QtGui.QApplication.translate("gphotoBracketPlugins", "Download when")
TEXT_AFTER_EACH_SHOT = QtGui.QApplication.translate("gphotoBracketPlugins", "After each shot")
TEXT_AFTER_BRACKETING = QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing is finished")
LABEL_DOWNLOAD_THEN_DELETE = QtGui.QApplication.translate("gphotoBracketPlugins", "Delete downloaded picts from camera")

class GphotoBracketShutter(AbstractShutterPlugin):
    """ Tethered shooting plugin based on gphoto2.
    """
    def _init(self):
        self.__speedConfig = None
        self.__speedOrder = None
        self.__availableSpeeds = None
        self.__baseSpeedIndex = None
        self.__evSteps = None
        self.__lastPictIndex = None

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
        self._addConfigKey('_gphotoCommand', 'GPHOTO_COMMAND', default=DEFAULT_GPHOTO_COMMAND)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NBPICTS)
        self._addConfigKey('_bracketingEvStep', 'BRACKETING_EV_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingEvBias', 'BRACKETING_EV_BIAS', default=0.0)
        self._addConfigKey('_bracketingPlusNbPicts', 'BRACKETING_PLUS_NB_PICTS', default=int(DEFAULT_BRACKETING_NBPICTS / 2))
        self._addConfigKey('_bracketingMinusNbPicts', 'BRACKETING_MINUS_NB_PICTS', default=int(DEFAULT_BRACKETING_NBPICTS / 2))
        self._addConfigKey('_bracketingPlusStep', 'BRACKETING_PLUS_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingMinusStep', 'BRACKETING_MINUS_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingEvList', 'BRACKETING_EV_LIST', default="0")
        self._addConfigKey('_bracketingAdvanced', 'BRACKETING_ADVANCED', default=False)
        self._addConfigKey('_downloadEnabled', 'DOWNLOAD_ENABLED', default=False)
        self._addConfigKey('_downloadDir', 'DOWNLOAD_DIR', default="")
        #self._addConfigKey('_downloadFilename', 'DOWNLOAD_FILENAME', default=DEFAULT_DOWNLOAD_FILENAME)
        self._addConfigKey('_downloadWhen', 'DOWNLOAD_WHEN', default='')
        self._addConfigKey('_downloadThenDelete', 'DOWNLOAD_THEN_DELETE', default=False)

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
        args = [self._config['GPHOTO_COMMAND']]
        args.append("--list-config")
        Logger().debug("GphotoBracketShutter.init(): execute command '%s'..." % ' '.join(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={ "LANG": "C" })

        # Wait end of execution
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            Logger().error("GphotoBracketShutter.init(): stderr:\n%s" % stderr.strip())
        else:
            Logger().info("GphotoBracketShutter.init(): stderr:\n%s" % stderr.strip())
        Logger().debug("GphotoBracketShutter.init(): stdout:\n%s" % stdout.strip())

        for line in stdout.splitlines():
            if line.endswith('/shutterspeed'):  # or line.endswith('/exptime'):
                self.__speedConfig = line
            elif line.endswith('/exptime'):
                self.__speedConfig = line

        # Get config
        args = [self._config['GPHOTO_COMMAND']]
        args.append("--get-config")
        args.append(self.__speedConfig)
        Logger().debug("GphotoBracketShutter.init(): execute command '%s'..." % ' '.join(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={ "LANG": "C" })

        # Wait end of execution
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            Logger().error("GphotoBracketShutter.init(): stderr:\n%s" % stderr.strip())
        else:
            Logger().info("GphotoBracketShutter.init(): stderr:\n%s" % stderr.strip())
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
            self.__speedOrder = 1 # slower speed first
        else:
            self.__speedOrder = -1 # faster speed first

        # Guess EV step (1/2, or 1/3)
        if float(self.__availableSpeeds[1]) / float(self.__availableSpeeds[3]) < 1.9:
            self.__evSteps = 3
        else:
            self.__evSteps = 2

        Logger().info("GphotoBracketShutter.init(): basespeed=%s config=%s order=%+d steps=1/%d" % \
                      (self.__baseSpeed, self.__speedConfig, self.__speedOrder, self.__evSteps))

    def shoot(self, bracketNumber):
        Logger().debug("GphotoBracketShutter.shoot(): bracketNumber=%d" % bracketNumber)

        evOffset = self._config['BRACKETING_EV_LIST'].split(",")[bracketNumber - 1].strip()

        speedIndex = self.__baseSpeedIndex - int(float(evOffset) * self.__evSteps * self.__speedOrder)

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
        Logger().info("GphotoBracketShutter.shoot(): EV=%s shutter speed=%s" % \
                      (evOffset, self.__availableSpeeds[speedIndex]))

        downloadEnabled = self._config['DOWNLOAD_ENABLED']
        downloadThenDelete = self._config['DOWNLOAD_THEN_DELETE']
        downloadAfterEachShot = (self._config['DOWNLOAD_WHEN'] == TEXT_AFTER_EACH_SHOT)
        downloadAfterBracketing = (self._config['DOWNLOAD_WHEN'] == TEXT_AFTER_BRACKETING)
        bracketingNbPicts = self._config['BRACKETING_NB_PICTS']

        # Whether to use --capture-image-and-download, or not
        useCaptureImageAndDownload = downloadEnabled and downloadThenDelete and (downloadAfterEachShot or (bracketingNbPicts == 1))

        # List files in the camera
        if (bracketNumber == 1) and downloadEnabled and not useCaptureImageAndDownload:
            args = [self._config['GPHOTO_COMMAND']]
            args.append("--list-files")
            Logger().debug("GphotoBracketShutter.shoot(): execute command '%s'..." % ' '.join(args))
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={ "LANG": "C" })

            # Wait end of execution
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                Logger().error("GphotoBracketShutter.shoot(): stderr:\n%s" % stderr.strip())
                return p.returncode
            else:
                Logger().info("GphotoBracketShutter.shoot(): stderr:\n%s" % stderr.strip())
            Logger().debug("GphotoBracketShutter.shoot(): stdout:\n%s" % stdout.strip())

            poundIndex = stdout.rfind('#')
            if poundIndex == -1:
                self.__lastPictIndex = 0
            else:
                self.__lastPictIndex = int(stdout[poundIndex + 1 : stdout.find(' ', poundIndex)])

            Logger().info("GphotoBracketShutter.shoot(): last file # in the camera is #%d" % self.__lastPictIndex)

        # Capture image
        args = [self._config['GPHOTO_COMMAND']]
        args.append("--set-config")
        args.append("%s=%s" % (self.__speedConfig, self.__availableSpeeds[speedIndex]))

        if useCaptureImageAndDownload:
            args.append("--capture-image-and-download")
            args.append("--filename")
            args.append(os.path.join(self._config['DOWNLOAD_DIR'], "%f.%C"))
            args.append("--force-overwrite")
        else:
            args.append("--capture-image")

        args.append("--set-config")
        args.append("%s=%s" % (self.__speedConfig, self.__baseSpeed))

        Logger().debug("GphotoBracketShutter.shoot(): execute command '%s'..." % ' '.join(args))

        if True:  # Set to False for tests
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={ "LANG": "C" })

            # Wait end of execution
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                Logger().error("GphotoBracketShutter.shoot(): stderr:\n%s" % stderr.strip())
                return p.returncode
            else:
                Logger().info("GphotoBracketShutter.shoot(): stderr:\n%s" % stderr.strip())
            Logger().debug("GphotoBracketShutter.shoot(): stdout:\n%s" % stdout.strip())

            # Download files
            if downloadEnabled and not useCaptureImageAndDownload and not (downloadAfterBracketing and (bracketNumber < bracketingNbPicts)):
                args = [self._config['GPHOTO_COMMAND']]
                args.append("--get-file")
                if downloadAfterEachShot:
                    if downloadThenDelete:
                        args.append("%d" % (self.__lastPictIndex + 1))
                    else:
                        args.append("%d" % (self.__lastPictIndex + bracketNumber))
                else:
                    args.append("%d-%d" % (self.__lastPictIndex + 1, self.__lastPictIndex + bracketNumber))
                args.append("--filename")
                args.append(os.path.join(self._config['DOWNLOAD_DIR'], "%f.%C"))
                args.append("--force-overwrite")
                if downloadThenDelete:
                    args.append("--delete-file")
                    if downloadAfterEachShot:
                        args.append("%d" % (self.__lastPictIndex + 1))
                    else:
                        args.append("%d-%d" % (self.__lastPictIndex + 1, self.__lastPictIndex + bracketNumber))
                args.append("--recurse")
                Logger().debug("GphotoBracketShutter.shoot(): execute command '%s'..." % ' '.join(args))
                p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={ "LANG": "C" })

                # Wait end of execution
                stdout, stderr = p.communicate()
                if p.returncode != 0:
                    Logger().error("GphotoBracketShutter.shoot(): stderr:\n%s" % stderr.strip())
                    return p.returncode
                else:
                    Logger().info("GphotoBracketShutter.shoot(): stderr:\n%s" % stderr.strip())
                Logger().debug("GphotoBracketShutter.shoot(): stdout:\n%s" % stdout.strip())

        return 0


class GphotoBracketShutterController(ShutterPluginController):
    def __formatEv(self, ev):
        ev = round(ev, 1)
        if ev == 0:
            return "0"
        else:
            return "%+g" % ev

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
        evBias = int(self._getWidget('Main', LABEL_EV_BIAS).value())
        self._getWidget('Main', LABEL_NB_PICTS).setValue(1 + plusNbPicts + minusNbPicts)

        evList = []
        if minusNbPicts > 0:
            for i in range(-minusNbPicts, 0):
                evList.append("%s" % self.__formatEv(i * minusStep + evBias))
        evList.append("%s" % self.__formatEv(evBias))
        if plusNbPicts > 0:
            for i in range(1, plusNbPicts+1):
                evList.append("%s" % self.__formatEv(i * plusStep + evBias))

        self._getWidget('Main', LABEL_EV_LIST).setValue(", ".join(evList))
        self._getWidget('Advanced', LABEL_EV_LIST).setValue(", ".join(evList))

        self.refreshView()

    def _defineGui(self):
        Logger().trace("GphotoBracketShutterController._defineGui()")
        ShutterPluginController._defineGui(self)

        self._view.tabWidget.setUsesScrollButtons(False)

        # Main tab
        #self._addWidget('Main', QtGui.QApplication.translate("gphotoBracketPlugins", "Mirror lockup"),
                        #CheckBoxField, (), 'MIRROR_LOCKUP')
        #self._addWidget('Main', QtGui.QApplication.translate("gphotoBracketPlugins", "Mirror lockup command"),
                        #FileSelectorField,
                        #(QtGui.QApplication.translate("gphotoBracketPlugins", "Choose mirror lockup command..."),
                         #QtGui.QApplication.translate("gphotoBracketPlugins", "All files (*)")),
                        #'MIRROR_LOCKUP_COMMAND')
        self._addWidget('Main', LABEL_GPHOTO_COMMAND,
                        FileSelectorField, (TEXT_CHOOSE_GPHOTO_COMMAND, TEXT_CHOOSE_GPHOTO_COMMAND_FILTER),
                        'GPHOTO_COMMAND')
        self._addWidget('Main', LABEL_NB_PICTS, SpinBoxField, (1, 11), 'BRACKETING_NB_PICTS')
        self._getWidget('Main', LABEL_NB_PICTS).setSingleStep(2)
        self._addWidget('Main', LABEL_EV_STEP, SpinBoxField, (1, 5, "", " ev"), 'BRACKETING_EV_STEP')
        self._addWidget('Main', LABEL_EV_LIST, LineEditField, (), 'BRACKETING_EV_LIST')
        self._getWidget('Main', LABEL_EV_LIST).setReadOnly(True)
        self._addWidget('Main', LABEL_EV_BIAS, SpinBoxField, (-5, 5, " ", " ev"), 'BRACKETING_EV_BIAS')
        self._addWidget('Main', LABEL_ADVANCED, CheckBoxField, (), 'BRACKETING_ADVANCED')
        self._addWidget('Main', LABEL_DOWNLOAD_ENABLED, CheckBoxField, (), 'DOWNLOAD_ENABLED')

        # Advanced tab
        self._addTab('Advanced', LABEL_ADVANCED_TAB)
        self._addWidget('Advanced', LABEL_PLUS_NB_PICTS, SpinBoxField, (0, 11), 'BRACKETING_PLUS_NB_PICTS')
        self._addWidget('Advanced', LABEL_PLUS_STEP, SpinBoxField, (0, 5, "", " ev"), 'BRACKETING_PLUS_STEP')
        self._addWidget('Advanced', LABEL_MINUS_NB_PICTS, SpinBoxField, (0, 11), 'BRACKETING_MINUS_NB_PICTS')
        self._addWidget('Advanced', LABEL_MINUS_STEP, SpinBoxField, (0, 5, "", " ev"), 'BRACKETING_MINUS_STEP')
        self._addWidget('Advanced', LABEL_EV_LIST, LineEditField, (), 'BRACKETING_EV_LIST')
        self._getWidget('Advanced', LABEL_EV_LIST).setReadOnly(True)
        self._addWidget('Advanced', LABEL_EV_BIAS, SpinBoxField, (-5, 5, " ", " ev"), 'BRACKETING_EV_BIAS')

        # Download tab
        self._addTab('Download', LABEL_DOWNLOAD_TAB)
        self._addWidget('Download', LABEL_DOWNLOAD_DIR,
                        DirSelectorField,
                        (QtGui.QApplication.translate("gphotoBracketPlugins", "Choose download directory..."),),
                        'DOWNLOAD_DIR')
        #filenamePatterns = [ DEFAULT_DOWNLOAD_FILENAME, "%Y-%m-%d_%Hh%Mm%Ss" ]
        #self._addWidget('Download', LABEL_DOWNLOAD_FILENAME, ComboBoxField, (filenamePatterns, ), 'DOWNLOAD_FILENAME')
        downloadWhen = [ TEXT_AFTER_EACH_SHOT, TEXT_AFTER_BRACKETING ]
        self._addWidget('Download', LABEL_DOWNLOAD_WHEN, ComboBoxField, (downloadWhen, ), 'DOWNLOAD_WHEN')
        self._addWidget('Download', LABEL_DOWNLOAD_THEN_DELETE, CheckBoxField, (), 'DOWNLOAD_THEN_DELETE')

    def refreshView(self):
        advanced = self._getWidget('Main', LABEL_ADVANCED).value()
        self._getWidget('Main', LABEL_NB_PICTS).setDisabled(advanced)
        self._getWidget('Main', LABEL_EV_STEP).setDisabled(advanced)
        self._setTabEnabled('Advanced', advanced)

        self._getWidget('Main', LABEL_EV_STEP).setDisabled(advanced or (self._getWidget('Main', LABEL_NB_PICTS).value() <= 1))

        # refresh Ev Bias
        self._getWidget('Main', LABEL_EV_BIAS).setDisabled(advanced)
        self._getWidget('Advanced', LABEL_EV_BIAS).setDisabled(not advanced)
        if advanced:
            evBias = self._getWidget('Advanced', LABEL_EV_BIAS).value()
            self._getWidget('Main', LABEL_EV_BIAS).setValue(evBias)
        else:
            evBias = self._getWidget('Main', LABEL_EV_BIAS).value()
            self._getWidget('Advanced', LABEL_EV_BIAS).setValue(evBias)
        if evBias > 0:
            self._getWidget('Main', LABEL_EV_BIAS).setPrefix("+")
            self._getWidget('Advanced', LABEL_EV_BIAS).setPrefix("+")
        else:
            self._getWidget('Main', LABEL_EV_BIAS).setPrefix(" ")
            self._getWidget('Advanced', LABEL_EV_BIAS).setPrefix(" ")

        download = self._getWidget('Main', LABEL_DOWNLOAD_ENABLED).value()
        self._setTabEnabled('Download', download)


def register():
    """ Register plugins.
    """
    PluginsManager().register(GphotoBracketShutter, GphotoBracketShutterController, capacity='shutter', name=NAME)
