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

__revision__ = "$Id$"

import time
import os.path
import os
import subprocess

from PyQt4 import QtCore, QtGui

from papywizard.common.exception import HardwareError
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
TEXT_CHOOSE_GPHOTO_COMMAND = QtGui.QApplication.translate("gphotoBracketPlugins", "Choose gphoto2 command...")
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

LABEL_DOWNLOAD_TAB = QtGui.QApplication.translate("gphotoBracketPlugins", "Download")
LABEL_DOWNLOAD_ENABLED = QtGui.QApplication.translate("gphotoBracketPlugins", "Enable download")
LABEL_DOWNLOAD_DIR = QtGui.QApplication.translate("gphotoBracketPlugins", "Download directory")
TEXT_CHOOSE_DOWNLOAD_DIR = QtGui.QApplication.translate("gphotoBracketPlugins", "Choose download directory...")
#LABEL_DOWNLOAD_FILENAME = QtGui.QApplication.translate("gphotoBracketPlugins", "File name")
#DEFAULT_DOWNLOAD_FILENAME = QtGui.QApplication.translate("gphotoBracketPlugins", "Use camera default")
LABEL_DOWNLOAD_WHEN = QtGui.QApplication.translate("gphotoBracketPlugins", "Download when")
TEXT_AFTER_EACH_SHOT = QtGui.QApplication.translate("gphotoBracketPlugins", "After each shot")
TEXT_AFTER_BRACKETING = QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing is finished")
LABEL_DOWNLOAD_THEN_DELETE = QtGui.QApplication.translate("gphotoBracketPlugins", "Delete picts on camera")

PREFIX_PROMPT = 'gphoto2: '  # gphoto2 shell prompt
PREFIX_ERROR = '*** Error '  # Error message


class Gphoto2Command(object):
    def __init__(self, command):
        super(Gphoto2Command, self).__init__()

        args = [command, "--shell", "--quiet"]
        self.popen = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={ "LANG": "C" })

    def __sendCommand(self, command):
        Logger().debug("Gphoto2Command.__sendCommand(): command='%s'" % command.strip())
        self.popen.stdin.write("%s\n" % command)
        prompt = self.popen.stdout.readline()  # Consume echo

    def quit(self):
        self.__sendCommand("quit")
        self.__sendCommand("quit")
        #stdout, stderr = self.popen.communicate()
        #if stderr:
            #Logger().warning("Gphoto2Command.quit(): gphoto2.stderr=\"%s\"" % (stderr))

    def listConfig(self):
        self.__sendCommand("list-config\n")
        configs = []
        while True:
            line = self.popen.stdout.readline().rstrip()
            if line.startswith(PREFIX_PROMPT):  # Prompt
                break
            elif line.startswith(PREFIX_ERROR):  # Error
                Logger().error("Gphoto2Command.listConfig(): gphoto2=\"%s\"" % (line))
                break
            elif line[0] == '/':
                configs.append(line)
            else:
                pass
        return configs

    def getConfig(self, config):
        self.__sendCommand("get-config %s\n" % config)
        props = {}
        choices = []
        while True:
            line = self.popen.stdout.readline().rstrip()
            if line.startswith(PREFIX_PROMPT):  # Prompt
                break
            elif line.startswith(PREFIX_ERROR):  # Error
                Logger().error("Gphoto2Command.getConfig(): config=%s gphoto2=\"%s\"" % (config, line))
                return None, None
            else:
                key, sep, value = line.partition(': ')  # 'Key: Value' form
                if key == "Choice":
                    if props['Type'] == 'MENU' or props['Type'] == 'RADIO':
                        idx, sep, value = value.partition(' ')
                    choices.append(value)
                else:
                    props[key] = value
        return props, choices

    def setConfig(self, config, value):
        self.__sendCommand("set-config %s=%s\n" % (config, value))
        prompt = self.popen.stdout.readline()

    def ls(self, dir=None, recurse=False):
        if dir is None:
            self.__sendCommand("ls")
            dir = ""
        else:
            self.__sendCommand("ls %s" % dir)
            if len(dir) > 0 and dir[-1] != '/':
                dir = dir + '/'

        # read directory entries
        line = self.popen.stdout.readline().rstrip()
        if line.startswith(PREFIX_ERROR):  # Error
            Logger().error("Gphoto2Command.ls(): %s recurse=%s gphoto2=\"%s\"" % (dir, str(recurse), line))
            return None, None
        childDirs = []
        numDirs = int(line)
        for i in range(numDirs):
            if recurse:
                childDirs.append(dir + self.popen.stdout.readline().rstrip() + '/')
            else:
                childDirs.append(self.popen.stdout.readline().rstrip() + '/')

        # read file entries
        childFiles = []
        line = self.popen.stdout.readline().rstrip()
        numFiles = int(line)
        for i in range(numFiles):
            if recurse:
                childFiles.append(dir + self.popen.stdout.readline().rstrip())
            else:
                childFiles.append(self.popen.stdout.readline().rstrip())

        if recurse:
            dirs = []
            files = childFiles[:]
            for childDir in childDirs:
                dirs.append(childDir)
                grandChildDirs, grandChildFiles = ls(self.popen, (childDir), recurse)
                if grandChildDirs is not None and len(grandChildDirs) > 0:
                    dirs.extend([d for d in grandChildDirs])  # or just dirs.extend(grandChildDirs)
                if grandChildFiles is not None and len(grandChildFiles) > 0:
                    files.extend([f for f in grandChildFiles])  # or just files.extend(grandChildFiles)
            return dirs, files
        else:
            return childDirs, childFiles

    def cd(self, dir):
        self.__sendCommand("cd %s" % dir)
        msg = self.popen.stdout.readline().rstrip()  # Read message
        cwd = None
        if msg.startswith(PREFIX_ERROR):  # Error
            Logger().error("Gphoto2Command.cd(): %s gphoto2=\"%s\"" % (dir, msg))
        elif msg.endswith("'."):
            fIndex = msg.find("'")
            rIndex = msg.rfind("'")
            if (fIndex != -1) and (rIndex != -1):
                cwd = msg[fIndex + 1 : rIndex]
        return cwd

    def lcd(self, dir):
        self.__sendCommand("lcd %s\n" % dir)
        msg = self.popen.stdout.readline().rstrip()  # Read message
        cwd = None
        if msg.endswith("'."):
            fIndex = msg.find("'")
            rIndex = msg.rfind("'")
            if fIndex != -1 and rIndex != -1:
                cwd = msg[fIndex + 1:rIndex]
            prompt = self.popen.stdout.readline()
        return cwd

    def get(self, file):
        self.__sendCommand("get %s\n" % file)
        msg = self.popen.stdout.readline().rstrip()
        if msg.startswith(PREFIX_ERROR):  # Error
            prompt = self.popen.stdout.readline()
            Logger().error("Gphoto2Command.get(): %s gphoto2=\"%s\"" % (file, msg))
            return False
        else:
            # Downloading 'IMAGE1234.JPG' from folder '/SOME/WHERE'...
            #Logger().debug("Gphoto2Command.get(): gphoto2.stderr=\"%s\"" % self.popen.stderr.readline().rstrip())
            pass
        return True

    def delete(self, file):
        self.__sendCommand("delete %s\n" % file)
        msg = self.popen.stdout.readline().rstrip()
        if msg.startswith(PREFIX_ERROR):  # Error
            prompt = self.popen.stdout.readline()
            Logger().error("Gphoto2Command.delete(): %s gphoto2=\"%s\"" % (file, msg))
            return False
        else:
            # Deleting 'IMAGE1234.JPG' from folder '/SOME/WHERE'...
            #Logger().debug("Gphoto2Command.delete(): gphoto2.stderr=\"%s\"" % self.popen.stderr.readline().rstrip())
            pass
        return True

    def captureImage(self):
        self.__sendCommand('capture-image')
        line = self.popen.stdout.readline().rstrip()
        if line.startswith(PREFIX_ERROR):  # Error
            Logger().error("Gphoto2Command.captureImage(): gphoto2=\"%s\"" % line)
            return None
        else:
            return line # full path


class GphotoBracketShutter(AbstractShutterPlugin):
    """ Tethered shooting plugin based on gphoto2.
    """
    def _init(self):
        self.__availableSpeeds = None
        self.__baseSpeedIndex = None
        self.__baseSpeed = None
        self.__bracketFiles = None
        self.__currentSpeed = None
        self.__evSteps = None
        self.__gphoto2 = None
        self.__lastPictIndex = None
        self.__localCwd = None
        self.__remoteCwd = None
        self.__speedConfig = None
        self.__speedOrder = None

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
        self._addConfigKey('_bracketingEvBias', 'BRACKETING_EV_BIAS', default=0.)
        self._addConfigKey('_bracketingPlusNbPicts', 'BRACKETING_PLUS_NB_PICTS', default=int(DEFAULT_BRACKETING_NBPICTS / 2))
        self._addConfigKey('_bracketingMinusNbPicts', 'BRACKETING_MINUS_NB_PICTS', default=int(DEFAULT_BRACKETING_NBPICTS / 2))
        self._addConfigKey('_bracketingPlusStep', 'BRACKETING_PLUS_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingMinusStep', 'BRACKETING_MINUS_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingEvList', 'BRACKETING_EV_LIST', default="0")
        self._addConfigKey('_bracketingAdvanced', 'BRACKETING_ADVANCED', default=False)
        self._addConfigKey('_downloadEnabled', 'DOWNLOAD_ENABLED', default=False)
        self._addConfigKey('_downloadDir', 'DOWNLOAD_DIR', default="")
        #self._addConfigKey('_downloadFilename', 'DOWNLOAD_FILENAME', default=DEFAULT_DOWNLOAD_FILENAME)
        self._addConfigKey('_downloadWhen', 'DOWNLOAD_WHEN', default="")
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
        self.__availableSpeeds = None
        self.__baseSpeedIndex = None
        self.__baseSpeed = None
        self.__bracketFiles = None
        self.__currentSpeed = None
        self.__evSteps = None
        self.__gphoto2 = None
        self.__lastPictIndex = None
        self.__localCwd = None
        self.__remoteCwd = None
        self.__speedConfig = None
        self.__speedOrder = None

        self.__gphoto2 = Gphoto2Command(self._config['GPHOTO_COMMAND'])

        # List up root directory of the camera
        dirs, files = self.__gphoto2.ls()
        if dirs is None or files is None:
            raise HardwareError("Unable to access camera file system")

        # List config
        configs = self.__gphoto2.listConfig()
        if configs is None or len(configs) == 0:
            raise HardwareError("Unable to retrieve config list from the camera")

        for config in configs:
            if config.endswith("/shutterspeed") or config.endswith("/exptime"):
                self.__speedConfig = config

        # Detected a 'Your Camera Model here'. message
        #Logger().debug("GphotoBracketShutter.init(): gphoto2.stderr=\"%s\"" % self.__gphoto2.popen.stderr.readline().rstrip())

        # Get config
        props, choices = self.__gphoto2.getConfig(self.__speedConfig)
        if props is None or choices is None:
            raise HardwareError("Unable to read shutter speed")

        # Load all available speeds and the current speed
        self.__availableSpeeds = choices
        self.__baseSpeed = props['Current']
        self.__baseSpeedIndex = None
        for choice, index in enumerate(choices):
            if choice == self.__baseSpeed:
                self.__baseSpeedIndex = index

        if float(self.__availableSpeeds[1]) > float(self.__availableSpeeds[2]):
            self.__speedOrder = 1  # Slower speed first
        else:
            self.__speedOrder = -1  # Faster speed first

        # Guess EV step (1/2, or 1/3)
        if float(self.__availableSpeeds[1]) / float(self.__availableSpeeds[3]) < 1.9:
            self.__evSteps = 3
        else:
            self.__evSteps = 2

        self.__remoteCwd = None

        Logger().debug("GphotoBracketShutter.init(): basespeed=%s config=%s order=%+d steps=1/%d" % \
                      (self.__baseSpeed, self.__speedConfig, self.__speedOrder, self.__evSteps))

    def shutdown(self):
        Logger().trace("GphotoBracketShutter.shutdown()")
        if self.__gphoto2 is not None:
            self.__gphoto2.quit()
            self.__gphoto2 = None

    def __downloadFiles(self, paths):
        downloadThenDelete = self._config['DOWNLOAD_THEN_DELETE']

        # Change to local download directory
        downloadDir = self._config['DOWNLOAD_DIR']
        if downloadDir[0] != '/':  # Relative path
            downloadDir = os.path.join(os.getcwd(), downloadDir)
        if downloadDir != self.__localCwd:
            self.__localCwd = self.__gphoto2.lcd(downloadDir)
        if self.__localCwd is None:
            Logger().error("GphotoBracketShutter.downloadFiles(): failed to change local directory to '%s'" % downloadDir)

        for imagePath in paths:
            # Image path in the camera
            imageDir = None
            imageFile = imagePath
            idx = imagePath.rfind('/')
            if idx != -1:
                imageDir = imagePath[0:idx]
                imageFile = imagePath[idx + 1:]

            if imageDir is not None and imageDir != self.__remoteCwd:
                Logger().debug("GphotoBracketShutter.downloadFiles(): changing remote directory to '%s'" % imageDir)
                self.__remoteCwd = self.__gphoto2.cd(imageDir)
                if self.__remoteCwd is None:
                    Logger().error("GphotoBracketShutter.downloadFiles(): failed to change remote directory to '%s'" % imageDir)
            # Download the file
            #Logger().debug("GphotoBracketShutter.downloadFiles(): downloading file '%s'" % imageFile)
            self.__gphoto2.get(imageFile)

            if downloadThenDelete:
                Logger().debug("GphotoBracketShutter.downloadFiles(): deleting remote file '%s'" % imageFile)
                self.__gphoto2.delete(imageFile)

    def shoot(self, bracketNumber):
        Logger().debug("GphotoBracketShutter.shoot(): bracketNumber=%d" % bracketNumber)

        downloadEnabled = self._config['DOWNLOAD_ENABLED']
        downloadAfterEachShot = (self._config['DOWNLOAD_WHEN'] == TEXT_AFTER_EACH_SHOT)
        downloadAfterBracketing = (self._config['DOWNLOAD_WHEN'] == TEXT_AFTER_BRACKETING)
        bracketingNbPicts = self._config['BRACKETING_NB_PICTS']

        # Take Ev offset from Ev list
        evOffset = self._config['BRACKETING_EV_LIST'].split(",")[bracketNumber - 1].strip()

        speedIndex = self.__baseSpeedIndex - int(float(evOffset) * self.__evSteps * self.__speedOrder)

        # see if shutter speed is out of range
        if self.__speedOrder > 0:  # Slow speed first
            if speedIndex < 1:
                speedIndex = 1
            elif speedIndex >= len(self.__availableSpeeds):
                speedIndex = len(self.__availableSpeeds) - 1
        elif self.__speedOrder < 0:  # Fast speed first
            if speedIndex < 0:
                speedIndex = 0
            elif speedIndex >= (len(self.__availableSpeeds) - 1):
                speedIndex = len(self.__availableSpeeds) - 2
        Logger().debug("GphotoBracketShutter.shoot(): EV=%s shutter speed=%s" % \
                      (evOffset, self.__availableSpeeds[speedIndex]))

        # Change shutter speed
        newSpeed = self.__availableSpeeds[speedIndex]
        if self.__currentSpeed != newSpeed:
            self.__gphoto2.setConfig(self.__speedConfig, newSpeed)
            self.__currentSpeed = newSpeed

        # Capture image
        Logger().debug("GphotoBracketShutter.shoot(): capturing image")
        for retry in range(5):
            imagePath = self.__gphoto2.captureImage()
            if imagePath is not None:  # Retry
                break
            Logger().warning("GphotoBracketShutter.shoot(): retrying in 1 second...")
            time.sleep(1)
        Logger().debug("GphotoBracketShutter.shoot(): captured image file='%s'" % imagePath)

        # Change shutter speed back to base speed
        #self.__gphoto2.setConfig(self.__speedConfig, self.__baseSpeed)

        # Download files
        if downloadEnabled:
            if downloadAfterEachShot:
                self.__downloadFiles([imagePath])
            elif downloadAfterBracketing:
                if bracketNumber == 1:
                    self.__bracketFiles = [imagePath]
                else:
                    self.__bracketFiles.append(imagePath)
                if bracketNumber == bracketingNbPicts:  # Last bracketing image
                    self.__downloadFiles(self.__bracketFiles)
                    self.__bracketFiles = []

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
        self._addWidget('Main', LABEL_EV_BIAS, SpinBoxField, (-5, 5, " ", " ev"), 'BRACKETING_EV_BIAS')
        self._addWidget('Main', LABEL_EV_LIST, LineEditField, (), 'BRACKETING_EV_LIST')
        self._getWidget('Main', LABEL_EV_LIST).setReadOnly(True)
        self._addWidget('Main', LABEL_ADVANCED, CheckBoxField, (), 'BRACKETING_ADVANCED')

        # Advanced tab
        self._addTab('Advanced', LABEL_ADVANCED_TAB)
        self._addWidget('Advanced', LABEL_PLUS_NB_PICTS, SpinBoxField, (0, 11), 'BRACKETING_PLUS_NB_PICTS')
        self._addWidget('Advanced', LABEL_PLUS_STEP, SpinBoxField, (0, 5, "", " ev"), 'BRACKETING_PLUS_STEP')
        self._addWidget('Advanced', LABEL_MINUS_NB_PICTS, SpinBoxField, (0, 11), 'BRACKETING_MINUS_NB_PICTS')
        self._addWidget('Advanced', LABEL_MINUS_STEP, SpinBoxField, (0, 5, "", " ev"), 'BRACKETING_MINUS_STEP')
        self._addWidget('Advanced', LABEL_EV_BIAS, SpinBoxField, (-5, 5, " ", " ev"), 'BRACKETING_EV_BIAS')
        self._addWidget('Advanced', LABEL_EV_LIST, LineEditField, (), 'BRACKETING_EV_LIST')
        self._getWidget('Advanced', LABEL_EV_LIST).setReadOnly(True)

        # Download tab
        self._addTab('Download', LABEL_DOWNLOAD_TAB)
        self._addWidget('Download', LABEL_DOWNLOAD_ENABLED, CheckBoxField, (), 'DOWNLOAD_ENABLED')
        self._addWidget('Download', LABEL_DOWNLOAD_DIR,
                        DirSelectorField, (TEXT_CHOOSE_DOWNLOAD_DIR,),
                        'DOWNLOAD_DIR')
        #fileNamePatterns = [DEFAULT_DOWNLOAD_FILENAME, "%Y-%m-%d_%Hh%Mm%Ss"]
        #self._addWidget('Download', LABEL_DOWNLOAD_FILENAME, ComboBoxField, (fileNamePatterns, ), 'DOWNLOAD_FILENAME')
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
            self._getWidget('Main', LABEL_EV_BIAS).setPrefix('+')
            self._getWidget('Advanced', LABEL_EV_BIAS).setPrefix('+')
        else:
            self._getWidget('Main', LABEL_EV_BIAS).setPrefix(' ')  # Does not seem to work...
            self._getWidget('Advanced', LABEL_EV_BIAS).setPrefix(' ')

        downloadEnabled = self._getWidget('Download', LABEL_DOWNLOAD_ENABLED).value()
        self._getWidget('Download', LABEL_DOWNLOAD_DIR).setDisabled(not downloadEnabled)
        self._getWidget('Download', LABEL_DOWNLOAD_WHEN).setDisabled(not downloadEnabled)
        self._getWidget('Download', LABEL_DOWNLOAD_THEN_DELETE).setDisabled(not downloadEnabled)


def register():
    """ Register plugins.
    """
    PluginsManager().register(GphotoBracketShutter, GphotoBracketShutterController, capacity='shutter', name=NAME)
