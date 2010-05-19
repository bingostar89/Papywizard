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

 - NkRemoteShutter
 - NkRemoteShutterController

Notes
=====

 - Get the config (tables for -x param)
 -

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import subprocess

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.plugins.abstractPluginController import AbstractPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, \
                                         CheckBoxField, SliderField, DirSelectorField, FileSelectorField

NAME = "NK Remote"

DEFAULT_PROGRAM_PATH = "C:\\Program Files\\BreezeSys\\NKRemote\\NKRemoteLibTest.exe"
DEFAULT_MIRROR_LOCKUP = False
DEFAULT_USER_EXPOSURE_COMPENSATION_LIST = "-2, 0, +2"
DEFAULT_DRY_RUN = False
DEFAULT_OUTPUT_DIR = config.HOME_DIR
DEFAULT_FILENAME_PREFIX = ""
DEFAULT_CAMERA_EXPOSURE_COMPENSATION_LIST = u"±5@1/2"

LABEL_PROGRAM_PATH = unicode(QtGui.QApplication.translate("nkRemotePlugins", "Program path"))
TEXT_CHOOSE_PROGRAM_PATH = unicode(QtGui.QApplication.translate("nkRemotePlugins", "Choose program path..."))
TEXT_CHOOSE_PROGRAM_PATH_FILTER = unicode(QtGui.QApplication.translate("nkRemotePlugins", "EXE files (*.exe);;All files (*)"))
LABEL_MIRROR_LOCKUP = unicode(QtGui.QApplication.translate("nkRemotePlugins", "Mirror lockup"))
LABEL_USER_EXPOSURE_COMPENSATION_LIST = unicode(QtGui.QApplication.translate("nkRemotePlugins", "User exposure\ncompensation list"))
LABEL_DRY_RUN = unicode(QtGui.QApplication.translate("nkRemotePlugins", "Dry run"))

TAB_CAMERA = unicode(QtGui.QApplication.translate("nkRemotePlugins", 'Camera'))
TEXT_CHOOSE_OUTPUT_DIR = unicode(QtGui.QApplication.translate("nkRemotePlugins", "Choose output directory..."))
LABEL_FILENAME_PREFIX = unicode(QtGui.QApplication.translate("nkRemotePlugins", "File name prefix"))
LABEL_CAMERA_EXPOSURE_COMPENSATION_LIST = unicode(QtGui.QApplication.translate("nkRemotePlugins", "Camera exposure\ncompensation list"))

MIRROR_LOCKUP_PARAMS = ""
OUTPUT_DIR_PARAM = "-o"
FILENAME_PREFIX_PARAM = "-p"
EXPOSURE_COMPENSATION_PARAM = "-x"
DRY_RUN_PARAM = "-n"
CAMERA_EXPOSURE_COMPENSATION_LIST_1_3 = ["+5", "+4 2/3", "+4 1/3",
                                         "+4", "+3 2/3", "+3 1/3",
                                         "+3", "+2 2/3", "+2 1/3",
                                         "+2", "+1 2/3", "+1 1/3",
                                         "+1", "+2/3", "+1/3",
                                         "0",
                                         "-1/3", "-2/3", "-1",
                                         "-1 1/3", "-1 2/3", "-2",
                                         "-2 1/3", "-2 2/3", "-3",
                                         "-3 1/3", "-3 2/3", "-4",
                                         "-4 1/3", "-4 2/3", "-5"]
CAMERA_EXPOSURE_COMPENSATION_LIST_1_2 = ["+5", "+4 1/2",
                                         "+4", "+3 1/2",
                                         "+3", "+2 1/2",
                                         "+2", "+1 1/2",
                                         "+1", "+1/2",
                                         "0",
                                         "-1/2", "-1",
                                         "-1 1/2", "-2",
                                         "-2 1/2",  "-3",
                                         "-3 1/2", "-4",
                                         "-4 1/2", "-5"]


class NkRemoteShutter(AbstractShutterPlugin):
    """ DSLR Remote Pro plugin class.
    """
    def _init(self):
        self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_2
        self.__userExposureCompensationList = DEFAULT_USER_EXPOSURE_COMPENSATION_LIST

    def _getTimeValue(self):
        return -1

    def _getMirrorLockup(self):
        return self._config['MIRROR_LOCKUP']

    def _getBracketingNbPicts(self):
        return len(self.__userExposureCompensationList)

    def _defineConfig(self):
        Logger().debug("NkRemoteShutter._defineConfig()")
        self._addConfigKey('_programPath', 'PROGRAM_PATH', default=DEFAULT_PROGRAM_PATH)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_userExposureCompensationList', 'USER_EXPOSURE_COMPENSATION_LIST',
                           default=DEFAULT_USER_EXPOSURE_COMPENSATION_LIST)
        self._addConfigKey('_dryRun', 'DRY_RUN', default=DEFAULT_DRY_RUN)
        self._addConfigKey('_outputDir', 'OUTPUT_DIR', default=DEFAULT_OUTPUT_DIR)
        self._addConfigKey('_filenamePrefix', 'FILENAME_PREFIX', default=DEFAULT_FILENAME_PREFIX)
        self._addConfigKey('_cameraExposureCompensationList', 'CAMERA_EXPOSURE_COMPENSATION_LIST',
                           default=DEFAULT_CAMERA_EXPOSURE_COMPENSATION_LIST)

    def init(self):
        Logger().trace("NkRemoteShutter.init()")
        AbstractShutterPlugin.init(self)
        self.configure()

    def configure(self):
        AbstractShutterPlugin.configure(self)

        # Build camera exposure compensation list
        if self._config['CAMERA_EXPOSURE_COMPENSATION_LIST'] == u"±5@1/3":
            self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_3
        elif self._config['CAMERA_EXPOSURE_COMPENSATION_LIST'] == u"±5@1/2":
            self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_2
        Logger().debug("NkRemoteShutter.configure(): camera exposure compensation table=%s" % \
                       self.__cameraExposureCompensationList)

        # Build user exposure compensation list
        self.__userExposureCompensationList = self._config['USER_EXPOSURE_COMPENSATION_LIST'].split(',')
        Logger().debug("NkRemoteShutter.configure(): user exposure compensation list=%s" % \
                       self.__userExposureCompensationList)

    def lockupMirror(self):
        # @todo: implement mirror lockup command
        cmd = "%s %s" %(self._config['PROGRAM_PATH'], MIRROR_LOCKUP_PARAMS)
        Logger().debug("NkRemoteShutter.lockupMirror(): command '%s'..." % cmd)
        time.sleep(1)
        Logger().debug("NkRemoteShutter.lockupMirror(): command over")
        return 0

    def shoot(self, bracketNumber):
        Logger().debug("NkRemoteShutter.shoot(): bracketNumber=%d" % bracketNumber)

        # Retreive index in exposure table
        exposureCompensation = self.__userExposureCompensationList[bracketNumber - 1].strip()
        Logger().debug("NkRemoteShutter.shoot(): exposure compensation=%s" % exposureCompensation)
        index = self.__cameraExposureCompensationList.index(exposureCompensation)

        # Build command
        args = [self._config['PROGRAM_PATH']]
        args.append(EXPOSURE_COMPENSATION_PARAM)
        args.append(str(index))
        if self._config['DRY_RUN']:
            args.append(DRY_RUN_PARAM)
        if self._config['OUTPUT_DIR']:
            args.append(OUTPUT_DIR_PARAM)
            args.append(self._config['OUTPUT_DIR'])
        if self._config['FILENAME_PREFIX']:
            args.append(FILENAME_PREFIX_PARAM)
            args.append(self._config['FILENAME_PREFIX'])
        Logger().debug("NkRemoteShutter.shoot(): shoot command '%s'..." % ' '.join(args))

        # Launch external command
        for nbTry in xrange(3):
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait end of execution
            stdout, stderr = p.communicate()

            # Check result
            if stderr:
                Logger().error("NkRemoteShutter.shoot(): stderr:\n%s" % stderr.strip())
            if p.returncode == 0:
                break
            Logger().warning("NkRemoteShutter.shoot(): shoot command failed (retcode=%d). Retrying..." % p.returncode)

        Logger().debug("NkRemoteShutter.shoot(): stdout:\n%s" % stdout.strip())

        return p.returncode


class NkRemoteShutterController(AbstractPluginController):
    def _defineGui(self):
        #AbstractPluginController._defineGui(self)
        self._addWidget('Main', LABEL_PROGRAM_PATH,
                        FileSelectorField, (TEXT_CHOOSE_PROGRAM_PATH, TEXT_CHOOSE_PROGRAM_PATH_FILTER),
                        'PROGRAM_PATH')
        self._addWidget('Main', LABEL_MIRROR_LOCKUP, CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', LABEL_USER_EXPOSURE_COMPENSATION_LIST, LineEditField, (), 'USER_EXPOSURE_COMPENSATION_LIST')
        self._addWidget('Main', LABEL_DRY_RUN, CheckBoxField, (), 'DRY_RUN')
        self._addTab('Camera', TAB_CAMERA)
        self._addWidget('Camera', QtGui.QApplication.translate("nkRemotePlugins", "Output directory"),
                        DirSelectorField, (TEXT_CHOOSE_OUTPUT_DIR,),
                        'OUTPUT_DIR')
        self._addWidget('Camera', LABEL_FILENAME_PREFIX, LineEditField, (), 'FILENAME_PREFIX')
        self._addWidget('Camera', LABEL_CAMERA_EXPOSURE_COMPENSATION_LIST, ComboBoxField, ((u"±5@1/3", u"±5@1/2"),),
                        'CAMERA_EXPOSURE_COMPENSATION_LIST')


def register():
    """ Register plugins.
    """
    PluginsManager().register(NkRemoteShutter, NkRemoteShutterController, capacity='shutter', name=NAME)
