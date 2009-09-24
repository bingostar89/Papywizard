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

 - DslrRemoteProShutter
 - DslrRemoteProShutterController

Notes
=====

 - Get the config (tables for -x param)
 -

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
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
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, \
                                         DoubleSpinBoxField, CheckBoxField, SliderField, DirSelectorField

NAME = "DSLR Remote Pro"

DEFAULT_MIRROR_LOCKUP = False
DEFAULT_USER_EXPOSURE_COMPENSATION_LIST = "-2, 0, +2"
DEFAULT_DRY_RUN = False
DEFAULT_OUTPUT_DIR = config.HOME_DIR
DEFAULT_FILENAME_PREFIX = ""
DEFAULT_CAMERA_EXPOSURE_COMPENSATION_LIST = u"±2@1/2"

PROGRAM_PATH = "C:\\Program Files\\BreezeSys\\DSLR Remote Pro\\DSLRRemoteTest\\DSLRRemoteTest.exe"
MIRROR_LOCKUP_PARAMS = ""
OUTPUT_DIR_PARAM = "-o %(dir)s"
FILENAME_PREFIX_PARAM = "-p %(prefix)s"
EXPOSURE_COMPENSATION_PARAM = "-x %(index)d"
CAMERA_EXPOSURE_COMPENSATION_LIST_1_3 = ["+5", "+4 2/3", "+4 1/3", "+4", "+3 2/3", "+3 1/3", "+3", "+2 2/3",
                                         "+2 1/3", "+2", "+1 2/3", "+1 1/3", "+1", "+2/3", "+1/3",
                                         "0",
                                         "-1/3", "-2/3", "-1", "-1 1/3", "-1 2/3", "-2", "-2 1/3",
                                         "-2 2/3", "-3", "-3 1/3", "-3 2/3", "-4", "-4 1/3", "-4 2/3", "-5"]
CAMERA_EXPOSURE_COMPENSATION_LIST_1_2 = ["+5", "+4 1/2", "+4", "+3 1/2", "+3", "+2 1/2", "+2", "+1 1/2", "+1", "+1/2",
                                         "0",
                                         "-1/2", "-1", "-1 1/2", "-2", "-2 1/2", "-3", "-3 1/2", "-4", "-4 1/2", "-5"]


class DslrRemoteProShutter(AbstractShutterPlugin):
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
        Logger().debug("DslrRemoteProShutter._defineConfig()")
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_userExposureCompensationList', 'USER_EXPOSURE_COMPENSATION_LIST',
                           default=DEFAULT_USER_EXPOSURE_COMPENSATION_LIST)
        self._addConfigKey('_dryRun', 'DRY_RUN', default=DEFAULT_DRY_RUN)
        self._addConfigKey('_outputDir', 'OUTPUT_DIR', default=DEFAULT_OUTPUT_DIR)
        self._addConfigKey('_filenamePrefix', 'FILENAME_PREFIX', default=DEFAULT_FILENAME_PREFIX)
        self._addConfigKey('_cameraExposureCompensationList', 'CAMERA_EXPOSURE_COMPENSATION_LIST',
                           default=DEFAULT_CAMERA_EXPOSURE_COMPENSATION_LIST)

    def init(self):
        Logger().trace("DslrRemoteProShutter.init()")
        AbstractShutterPlugin.init(self)
        self.configure()

    def configure(self):
        AbstractShutterPlugin.configure(self)

        # Build camera exposure compensation list
        if self._config['CAMERA_EXPOSURE_COMPENSATION_LIST'] == u"±5@1/3":
            self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_3
        elif self._config['CAMERA_EXPOSURE_COMPENSATION_LIST'] == u"±5@1/2":
            self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_2
        elif self._config['CAMERA_EXPOSURE_COMPENSATION_LIST'] == u"±3@1/3":
            self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_3[4:-4]
        elif self._config['CAMERA_EXPOSURE_COMPENSATION_LIST'] == u"±3@1/2":
            self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_2[4:-4]
        elif self._config['CAMERA_EXPOSURE_COMPENSATION_LIST'] == u"±2@1/3":
            self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_3[6:-6]
        elif self._config['CAMERA_EXPOSURE_COMPENSATION_LIST'] == u"±2@1/2":
            self.__cameraExposureCompensationList = CAMERA_EXPOSURE_COMPENSATION_LIST_1_2[6:-6]
        Logger().debug("DslrRemoteProShutter.configure(): camera exposure compensation table=%s" % \
                       self.__cameraExposureCompensationList)

        # Build user exposure compensation list
        self.__userExposureCompensationList = self._config['USER_EXPOSURE_COMPENSATION_LIST'].split(',')
        Logger().debug("DslrRemoteProShutter.configure(): user exposure compensation list=%s" % \
                       self.__userExposureCompensationList)

    def lockupMirror(self):
        # @todo: implement mirror lockup command
        cmd = "%s %s" %( PROGRAM_PATH, MIRROR_LOCKUP_PARAMS)
        Logger().debug("DslrRemoteProShutter.lockupMirror(): command '%s'..." % cmd)
        time.sleep(1)
        Logger().debug("DslrRemoteProShutter.lockupMirror(): command over")
        return 0

    def shoot(self, bracketNumber):
        Logger().debug("DslrRemoteProShutter.shoot(): bracketNumber=%d" % bracketNumber)

        # Retreive index in exposure table
        exposureCompensation = self.__userExposureCompensationList[bracketNumber - 1].strip()
        Logger().debug("DslrRemoteProShutter.shoot(): exposure compensation=%s" % exposureCompensation)
        index = self.__cameraExposureCompensationList.index(exposureCompensation)

        # Build command
        cmd = PROGRAM_PATH
        cmd += " %s" % EXPOSURE_COMPENSATION_PARAM % {'index': index}
        if self._config['DRY_RUN']:
            cmd += " -n"
        if self._config['OUTPUT_DIR']:
            cmd += " %s" % OUTPUT_DIR_PARAM % {'dir': self._config['OUTPUT_DIR']}
        if self._config['FILENAME_PREFIX']:
            cmd += " %s" % FILENAME_PREFIX_PARAM % {'prefix': self._config['FILENAME_PREFIX']}
        Logger().debug("DslrRemoteProShutter.shoot(): shoot command '%s'..." % cmd)

        # Launch external command
        args = cmd.split()
        for nbTry in xrange(3):
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait end of execution
            stdout, stderr = p.communicate()

            # Check result
            if stderr:
                Logger().error("DslrRemoteProShutter.shoot(): stderr:\n%s" % stderr.strip())
            if p.returncode == 0:
                break
            Logger().warning("DslrRemoteProShutter.shoot(): shoot command failed (retcode=%d). Retrying..." % p.returncode)

        Logger().debug("DslrRemoteProShutter.shoot(): stdout:\n%s" % stdout.strip())

        return p.returncode


class DslrRemoteProShutterController(ShutterPluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        self._addWidget('Main', QtGui.QApplication.translate("dslrRemoteProPlugins", "Mirror lockup"),
                        CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', QtGui.QApplication.translate("dslrRemoteProPlugins", "User exposure\ncompensation list"),
                        LineEditField, (), 'USER_EXPOSURE_COMPENSATION_LIST')
        self._addWidget('Main', QtGui.QApplication.translate("dslrRemoteProPlugins", "Dry run"),
                        CheckBoxField, (), 'DRY_RUN')
        self._addTab('Camera', QtGui.QApplication.translate("dslrRemoteProPlugins", 'Camera'))
        self._addWidget('Camera', QtGui.QApplication.translate("dslrRemoteProPlugins", "Output directory"),
                        DirSelectorField,
                        (QtGui.QApplication.translate("dslrRemoteProPlugins", "Choose output directory..."),),
                        'OUTPUT_DIR')
        self._addWidget('Camera', QtGui.QApplication.translate("dslrRemoteProPlugins", "File name prefix"),
                        LineEditField, (), 'FILENAME_PREFIX')
        self._addWidget('Camera', QtGui.QApplication.translate("dslrRemoteProPlugins", "Camera exposure\ncompensation list"),
                        ComboBoxField, ((u"±5@1/3", u"±5@1/2", u"±3@1/3", u"±3@1/2", u"±2@1/3", u"±2@1/2"),),
                        'CAMERA_EXPOSURE_COMPENSATION_LIST')


def register():
    """ Register plugins.
    """
    PluginsManager().register(DslrRemoteProShutter, DslrRemoteProShutterController, capacity='shutter', name=NAME)
