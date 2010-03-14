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

from papywizard.common import config
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
DEFAULT_PROGRAM_PATH = "gphoto2"
DEFAULT_BRACKETING_NB_PICTS = 1
DEFAULT_BRACKETING_STEP = 1
DEFAULT_BRACKETING_EV_BIAS = 0
DEFAULT_BRACKETING_ADVANCED = False
DEFAULT_DOWNLOAD_ENABLE = False
DEFAULT_DOWNLOAD_DIR = config.HOME_DIR
DEFAULT_DOWNLOAD_THEN_DELETE = False
#DEFAULT_DOWNLOAD_FILENAME = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Use camera default"))

#LABEL_MIRROR_LOCKUP = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Mirror lockup"))
#LABEL_MIRROR_LOCKUP_COMMAND = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Mirror lockup command"))
#TEXT_CHOOSE_MIRROR_LOCKUP_COMMAND = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Choose mirror lockup command..."))
#TEXT_CHOOSE_MIRROR_LOCKUP_COMMAND_FILTER = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "All files (*)"))
LABEL_PROGRAM_PATH = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Program path"))
TEXT_CHOOSE_PROGRAM_PATH = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Choose program path..."))
TEXT_CHOOSE_PROGRAM_PATH_FILTER = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "gphoto2 (gphoto2);;All files (*)"))
LABEL_NB_PICTS = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing nb picts"))
LABEL_EV_STEP = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing step"))
LABEL_EV_BIAS = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Exposure bias"))
LABEL_EV_LIST = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Resulting Ev list"))
LABEL_ADVANCED = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Advanced"))

TAB_CAMERA = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", 'Advanced'))
LABEL_PLUS_NB_PICTS = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing nb picts (+)"))
LABEL_PLUS_STEP = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing step (+)"))
LABEL_MINUS_NB_PICTS = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing nb picts (-)"))
LABEL_MINUS_STEP = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing step (-)"))

LABEL_DOWNLOAD_TAB = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Download"))
LABEL_DOWNLOAD_ENABLE = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Enable"))
LABEL_DOWNLOAD_DIR = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Download directory"))
TEXT_CHOOSE_DOWNLOAD_DIR = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Choose download directory..."))
#LABEL_DOWNLOAD_FILENAME = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "File name"))
LABEL_DOWNLOAD_AFTER = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Download after"))
TEXT_AFTER_EACH_SHOT = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Each shot"))
TEXT_AFTER_BRACKETING = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Bracketing sequence"))
LABEL_DOWNLOAD_THEN_DELETE = unicode(QtGui.QApplication.translate("gphotoBracketPlugins", "Delete camera picts"))

PREFIX_PROMPT = 'gphoto2: '  # gphoto2 shell prompt
PREFIX_ERROR = '*** Error '  # Error message


class GphotoShell(QtCore.QObject):
    """
    """
    def __init__(self, programPath):
        """ Init object.
        """
        QtCore.QObject.__init__(self)

        args = [programPath, "--shell", "--quiet"]
        self.__popen = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'LANG': "C"})

    def __sendCmd(self, cmd):
        """ Send a command to gphoto2 shell.

        @param command: command to send
        @type command: str
        """
        Logger().debug("GphotoShell.__sendCmd(): command='%s'" % cmd.strip())
        self.__popen.stdin.write("%s\n" % cmd)
        prompt = self.__popen.stdout.readline()  # Consume echo

    def quit(self):
        """ Quit gphoto2 shell.
        """
        self.__sendCmd("quit")
        self.__sendCmd("quit")
        #stdout, stderr = self.__popen.communicate()
        #if stderr:
            #Logger().warning("GphotoShell.quit(): gphoto2.stderr=\"%s\"" % (stderr))

    def listConfig(self):
        """ List all camera configs.
        """
        self.__sendCmd("list-config\n")
        configs = []
        while True:
            line = self.__popen.stdout.readline().rstrip()
            if line.startswith(PREFIX_PROMPT):
                break
            elif line.startswith(PREFIX_ERROR):
                Logger().error("GphotoShell.listConfig(): gphoto2=\"%s\"" % (line))
                break
            elif line[0] == '/':
                configs.append(line)
            else:
                pass
        return configs

    def getConfig(self, config):
        """ Get a specific config from camera.

        @param config: path of the config to get
        @type config: str
        """
        self.__sendCmd("get-config %s\n" % config)
        props = {}
        choices = []
        while True:
            line = self.__popen.stdout.readline().rstrip()
            if line.startswith(PREFIX_PROMPT):
                break
            elif line.startswith(PREFIX_ERROR):
                Logger().error("GphotoShell.getConfig(): config=%s gphoto2=\"%s\"" % (config, line))
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
        """ Set a specific config to camera.

        @param config: path of the config to set
        @type config: str
        """
        self.__sendCmd("set-config %s=%s\n" % (config, value))
        prompt = self.__popen.stdout.readline()

    def ls(self, dir_=None, recurse=False):
        """ List dir.

        @param dir_: directory to list
        @type dir_: str

        @param recurse: if True, list dir recursively
        @type recurse: bool
        """
        if dir_ is None:
            self.__sendCmd("ls")
            dir_ = ""
        else:
            self.__sendCmd("ls %s" % dir_)
            if len(dir_) > 0 and dir_[-1] != '/':
                dir_ += '/'

        # read directory entries
        line = self.__popen.stdout.readline().rstrip()
        if line.startswith(PREFIX_ERROR):
            Logger().error("GphotoShell.ls(): %s recurse=%s gphoto2=\"%s\"" % (dir_, recurse, line))
            return None, None
        childDirs = []
        numDirs = int(line)
        for i in range(numDirs):
            if recurse:
                childDirs.append(dir_ + self.__popen.stdout.readline().rstrip() + '/')
            else:
                childDirs.append(self.__popen.stdout.readline().rstrip() + '/')

        # read file entries
        childFiles = []
        line = self.__popen.stdout.readline().rstrip()
        numFiles = int(line)
        for i in range(numFiles):
            if recurse:
                childFiles.append(dir_ + self.__popen.stdout.readline().rstrip())
            else:
                childFiles.append(self.__popen.stdout.readline().rstrip())

        if recurse:
            dirs = []
            files = childFiles[:]
            for childDir in childDirs:
                dirs.append(childDir)
                grandChildDirs, grandChildFiles = ls(self.__popen, (childDir), recurse)  # ???
                if grandChildDirs is not None and len(grandChildDirs) > 0:
                    dirs.extend([d for d in grandChildDirs])  # or just dirs.extend(grandChildDirs)
                if grandChildFiles is not None and len(grandChildFiles) > 0:
                    files.extend([f for f in grandChildFiles])  # or just files.extend(grandChildFiles)
            return dirs, files
        else:
            return childDirs, childFiles

    def cd(self, dir_):
        """ Change current dir.

        @param dir_: new current dir
        @type dir_: str
        """
        self.__sendCmd("cd %s" % dir_)
        msg = self.__popen.stdout.readline().rstrip()  # Read message
        cwd = None
        if msg.startswith(PREFIX_ERROR):  # Error
            Logger().error("GphotoShell.cd(): %s gphoto2=\"%s\"" % (dir_, msg))
        elif msg.endswith("'."):
            fIndex = msg.find("'")
            rIndex = msg.rfind("'")
            if fIndex != -1 and rIndex != -1:
                cwd = msg[fIndex + 1:rIndex]
        return cwd

    def lcd(self, dir_):
        """ Change local current dir?

        @param dir_: new local current dir
        @type dir_: str
        """
        self.__sendCmd("lcd %s\n" % dir_)
        msg = self.__popen.stdout.readline().rstrip()  # Read message
        cwd = None
        if msg.endswith("'."):
            fIndex = msg.find("'")
            rIndex = msg.rfind("'")
            if fIndex != -1 and rIndex != -1:
                cwd = msg[fIndex + 1:rIndex]
            prompt = self.__popen.stdout.readline()
        return cwd

    def get(self, file_):
        """ Get file.

        @param file_: file to get
        @type file_: str
        """
        self.__sendCmd("get %s\n" % file_)
        msg = self.__popen.stdout.readline().rstrip()
        if msg.startswith(PREFIX_ERROR):  # Error
            prompt = self.__popen.stdout.readline()
            Logger().error("GphotoShell.get(): %s gphoto2=\"%s\"" % (file_, msg))
            return False
        else:
            # Downloading 'IMAGE1234.JPG' from folder '/SOME/WHERE'...
            #Logger().debug("GphotoShell.get(): gphoto2.stderr=\"%s\"" % self.__popen.stderr.readline().rstrip())
            pass
        return True

    def delete(self, file_):
        """ Delete file.

        @param file_: file to delete
        @type file_: str
        """
        self.__sendCmd("delete %s\n" % file_)
        msg = self.__popen.stdout.readline().rstrip()
        if msg.startswith(PREFIX_ERROR):  # Error
            prompt = self.__popen.stdout.readline()
            Logger().error("GphotoShell.delete(): %s gphoto2=\"%s\"" % (file_, msg))
            return False
        else:
            # Deleting 'IMAGE1234.JPG' from folder '/SOME/WHERE'...
            #Logger().debug("GphotoShell.delete(): gphoto2.stderr=\"%s\"" % self.__popen.stderr.readline().rstrip())
            pass
        return True

    def captureImage(self):
        """ Capture image.
        """
        self.__sendCmd('capture-image')
        line = self.__popen.stdout.readline().rstrip()
        if line.startswith(PREFIX_ERROR):  # Error
            Logger().error("GphotoShell.captureImage(): gphoto2=\"%s\"" % line)
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
        self.__gphotoShell = None
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
        self._addConfigKey('_programPath', 'PROGRAM_PATH', default=DEFAULT_PROGRAM_PATH)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NB_PICTS)
        self._addConfigKey('_bracketingEvStep', 'BRACKETING_EV_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingEvBias', 'BRACKETING_EV_BIAS', default=DEFAULT_BRACKETING_EV_BIAS)
        self._addConfigKey('_bracketingPlusNbPicts', 'BRACKETING_PLUS_NB_PICTS', default=int(DEFAULT_BRACKETING_NB_PICTS / 2))
        self._addConfigKey('_bracketingMinusNbPicts', 'BRACKETING_MINUS_NB_PICTS', default=int(DEFAULT_BRACKETING_NB_PICTS / 2))
        self._addConfigKey('_bracketingPlusStep', 'BRACKETING_PLUS_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingMinusStep', 'BRACKETING_MINUS_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingEvList', 'BRACKETING_EV_LIST', default="0")
        self._addConfigKey('_bracketingAdvanced', 'BRACKETING_ADVANCED', default=DEFAULT_BRACKETING_ADVANCED)
        self._addConfigKey('_downloadEnable', 'DOWNLOAD_ENABLE', default=DEFAULT_DOWNLOAD_ENABLE)
        self._addConfigKey('_downloadDir', 'DOWNLOAD_DIR', default=DEFAULT_DOWNLOAD_DIR)
        #self._addConfigKey('_downloadFilename', 'DOWNLOAD_FILENAME', default=DEFAULT_DOWNLOAD_FILENAME)
        self._addConfigKey('_downloadAfter', 'DOWNLOAD_AFTER', default=TEXT_AFTER_EACH_SHOT)
        self._addConfigKey('_downloadThenDelete', 'DOWNLOAD_THEN_DELETE', default=DEFAULT_DOWNLOAD_THEN_DELETE)

    def lockupMirror(self):
        """ @todo: implement mirror lockup command
        """
        Logger().debug("GphotoBracketShutter.lockupMirror(): execute command '%s'..." % self._config['MIRROR_LOCKUP_COMMAND'])
        time.sleep(1)
        Logger().debug("GphotoBracketShutter.lockupMirror(): command over")
        return 0

    def init(self):
        #self.__localCwd = None  # Needed?
        self.__gphotoShell = GphotoShell(self._config['PROGRAM_PATH'])

        # List up root directory of the camera
        dirs, files = self.__gphotoShell.ls()
        if dirs is None or files is None:
            raise HardwareError("Unable to access camera file system")

        # List config
        configs = self.__gphotoShell.listConfig()
        if configs is None or len(configs) == 0:
            raise HardwareError("Unable to retrieve config list from the camera")

        for config in configs:
            if config.endswith("/shutterspeed") or config.endswith("/exptime"):
                self.__speedConfig = config

        # Detected a 'Your Camera Model here' message ???!!!???
        #Logger().debug("GphotoBracketShutter.init(): gphoto2.stderr=\"%s\"" % self.__gphotoShell.popen.stderr.readline().rstrip())

        # Get config
        props, choices = self.__gphotoShell.getConfig(self.__speedConfig)
        if props is None or choices is None:
            raise HardwareError("Unable to read shutter speed")

        # Load all available speeds and the current speed
        self.__availableSpeeds = choices
        self.__baseSpeed = props['Current']
        for index, choice in enumerate(choices):
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

        Logger().debug("GphotoBracketShutter.init(): basespeed=%s config=%s order=%+d steps=1/%d" % \
                      (self.__baseSpeed, self.__speedConfig, self.__speedOrder, self.__evSteps))

    def shutdown(self):
        Logger().trace("GphotoBracketShutter.shutdown()")
        if self.__gphotoShell is not None:
            self.__gphotoShell.quit()
            self.__gphotoShell = None

    def __downloadFiles(self, paths):
        downloadThenDelete = self._config['DOWNLOAD_THEN_DELETE']

        # Change to local download directory
        downloadDir = self._config['DOWNLOAD_DIR']
        if downloadDir[0] != '/':  # Relative path
            downloadDir = os.path.join(os.getcwd(), downloadDir)
        if downloadDir != self.__localCwd:
            self.__localCwd = self.__gphotoShell.lcd(downloadDir)
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
                self.__remoteCwd = self.__gphotoShell.cd(imageDir)
                if self.__remoteCwd is None:
                    Logger().error("GphotoBracketShutter.downloadFiles(): failed to change remote directory to '%s'" % imageDir)

            # Download the file
            #Logger().debug("GphotoBracketShutter.downloadFiles(): downloading file '%s'" % imageFile)
            self.__gphotoShell.get(imageFile)

            if downloadThenDelete:
                Logger().debug("GphotoBracketShutter.downloadFiles(): deleting remote file '%s'" % imageFile)
                self.__gphotoShell.delete(imageFile)

    def shoot(self, bracketNumber):
        Logger().debug("GphotoBracketShutter.shoot(): bracketNumber=%d" % bracketNumber)

        downloadEnable = self._config['DOWNLOAD_ENABLE']
        downloadAfterEachShot = (self._config['DOWNLOAD_AFTER'] == TEXT_AFTER_EACH_SHOT)
        downloadAfterBracketing = (self._config['DOWNLOAD_AFTER'] == TEXT_AFTER_BRACKETING)
        bracketingNbPicts = self._config['BRACKETING_NB_PICTS']

        # Take Ev offset from Ev list
        evOffset = self._config['BRACKETING_EV_LIST'].split(',')[bracketNumber - 1].strip()

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
            self.__gphotoShell.setConfig(self.__speedConfig, newSpeed)
            self.__currentSpeed = newSpeed

        # Capture image
        Logger().debug("GphotoBracketShutter.shoot(): capturing image")
        for retry in range(5):
            imagePath = self.__gphotoShell.captureImage()
            if imagePath is not None:
                break
            Logger().warning("Shoot failed; retrying in 1 second...")
            time.sleep(1)
        #else:
            #Logger().error("Shoot failed")
            #raise Problem...
        Logger().debug("GphotoBracketShutter.shoot(): captured image file='%s'" % imagePath)

        # Change shutter speed back to base speed
        #self.__gphoto2.setConfig(self.__speedConfig, self.__baseSpeed)
        # Why commented?

        # Download files
        if downloadEnable:
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
        """ Format the exposure value.
        """
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
        #self._addWidget('Main', LABEL_MIRROR_LOCKUP, CheckBoxField, (), 'MIRROR_LOCKUP')
        #self._addWidget('Main', LABEL_MIRROR_LOCKUP_COMMAND,
                        #FileSelectorField, (TEXT_CHOOSE_MIRROR_LOCKUP_COMMAND, TEXT_CHOOSE_MIRROR_LOCKUP_COMMAND_FILTER),
                        #'MIRROR_LOCKUP_COMMAND')
        self._addWidget('Main', LABEL_PROGRAM_PATH,
                        FileSelectorField, (TEXT_CHOOSE_PROGRAM_PATH, TEXT_CHOOSE_PROGRAM_PATH_FILTER),
                        'PROGRAM_PATH')
        self._addWidget('Main', LABEL_NB_PICTS, SpinBoxField, (1, 11), 'BRACKETING_NB_PICTS')
        self._getWidget('Main', LABEL_NB_PICTS).setSingleStep(2)
        self._addWidget('Main', LABEL_EV_STEP, SpinBoxField, (1, 5, "", " ev"), 'BRACKETING_EV_STEP')
        self._addWidget('Main', LABEL_EV_BIAS, SpinBoxField, (-5, 5, " ", " ev"), 'BRACKETING_EV_BIAS')
        self._addWidget('Main', LABEL_EV_LIST, LineEditField, (), 'BRACKETING_EV_LIST')
        self._getWidget('Main', LABEL_EV_LIST).setReadOnly(True)
        self._addWidget('Main', LABEL_ADVANCED, CheckBoxField, (), 'BRACKETING_ADVANCED')

        # Advanced tab
        self._addTab('Advanced', TAB_CAMERA)
        self._addWidget('Advanced', LABEL_PLUS_NB_PICTS, SpinBoxField, (0, 11), 'BRACKETING_PLUS_NB_PICTS')
        self._addWidget('Advanced', LABEL_PLUS_STEP, SpinBoxField, (0, 5, "", " ev"), 'BRACKETING_PLUS_STEP')
        self._addWidget('Advanced', LABEL_MINUS_NB_PICTS, SpinBoxField, (0, 11), 'BRACKETING_MINUS_NB_PICTS')
        self._addWidget('Advanced', LABEL_MINUS_STEP, SpinBoxField, (0, 5, "", " ev"), 'BRACKETING_MINUS_STEP')
        self._addWidget('Advanced', LABEL_EV_BIAS, SpinBoxField, (-5, 5, " ", " ev"), 'BRACKETING_EV_BIAS')
        self._addWidget('Advanced', LABEL_EV_LIST, LineEditField, (), 'BRACKETING_EV_LIST')
        self._getWidget('Advanced', LABEL_EV_LIST).setReadOnly(True)

        # Download tab
        self._addTab('Download', LABEL_DOWNLOAD_TAB)
        self._addWidget('Download', LABEL_DOWNLOAD_ENABLE, CheckBoxField, (), 'DOWNLOAD_ENABLE')
        self._addWidget('Download', LABEL_DOWNLOAD_DIR,
                        DirSelectorField, (TEXT_CHOOSE_DOWNLOAD_DIR,),
                        'DOWNLOAD_DIR')
        #fileNamePatterns = [DEFAULT_DOWNLOAD_FILENAME, "%Y-%m-%d_%Hh%Mm%Ss"]
        #self._addWidget('Download', LABEL_DOWNLOAD_FILENAME, ComboBoxField, (fileNamePatterns, ), 'DOWNLOAD_FILENAME')
        downloadWhen = [ TEXT_AFTER_EACH_SHOT, TEXT_AFTER_BRACKETING ]
        self._addWidget('Download', LABEL_DOWNLOAD_AFTER, ComboBoxField, (downloadWhen, ), 'DOWNLOAD_AFTER')
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

        downloadEnable = self._getWidget('Download', LABEL_DOWNLOAD_ENABLE).value()
        self._getWidget('Download', LABEL_DOWNLOAD_DIR).setDisabled(not downloadEnable)
        self._getWidget('Download', LABEL_DOWNLOAD_AFTER).setDisabled(not downloadEnable)
        self._getWidget('Download', LABEL_DOWNLOAD_THEN_DELETE).setDisabled(not downloadEnable)


def register():
    """ Register plugins.
    """
    PluginsManager().register(GphotoBracketShutter, GphotoBracketShutterController, capacity='shutter', name=NAME)
