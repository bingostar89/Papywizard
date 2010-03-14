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

- EOSUtilityShutter
- EOSUtilityShutterController

@author: Jones Henry Subbiah
@author: Frédéric Mantegazza
@copyright: (C) 2009 Jones Henry Subbiah
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import subprocess

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager import PluginsManager
from papywizard.plugins.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, CheckBoxField, FileSelectorField

NAME = "EOS Utility"

DEFAULT_PROGRAM_PATH = "C:\\Program Files\\Papywizard\\EOSBracket.exe"
DEFAULT_EOS_UTILITY_VERSION = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "new"))
DEFAULT_BRACKETING_STEP = "1"
DEFAULT_BRACKETING_TYPE = '0-+'
DEFAULT_BRACKETING_NB_PICTS = 1
DEFAULT_DRY_RUN = True
DEFAULT_BULB_ENABLE = False
DEFAULT_BULB_BASE_EXPOSURE = 1
DEFAULT_FOCUS_ENABLE = False
DEFAULT_FOCUS_DIRECTION = unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'far'))
DEFAULT_FOCUS_STEP = unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'medium'))
DEFAULT_FOCUS_STEP_COUNT = 1
DEFAULT_FOCUS_NB_PICTS = 1

LABEL_PROGRAM_PATH = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Program path"))
TEXT_CHOOSE_PROGRAM_PATH = unicode(QtGui.QApplication.translate("TimelordShutterController", "Choose program path..."))
TEXT_CHOOSE_PROGRAM_PATH_FILTER = unicode(QtGui.QApplication.translate("TimelordShutterController", "EXE files (*.exe);;All files (*)"))
LABEL_EOS_UTILITY_VERSION = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "EOS Utility version"))
LABEL_BRACKETING_NB_PICTS = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Bracketing nb picts"))
LABEL_BRACKETING_STEP = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Bracketing step"))
LABEL_BRACKETING_TYPE = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Bracketing type"))
LABEL_DRY_RUN = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Dry run"))

TAB_BULB = unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'Bulb'))
LABEL_BULB_ENABLE = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Enable"))
LABEL_BULB_BASE_EXPOSURE = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Base exposure"))

TAB_FOCUS = unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'Focus'))
LABEL_FOCUS_ENABLE = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Enable"))
LABEL_FOCUS_DIRECTION = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Direction"))
LABEL_FOCUS_STEP = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Step"))
LABEL_FOCUS_STEP_COUNT = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Step count"))
LABEL_FOCUS_NB_PICTS = unicode(QtGui.QApplication.translate("eosUtilityPlugins", "Nb picts"))

BRACKETING_TYPE_INDEX = {'0--': '1',
                         '0++': '2',
                         '0-+': '3'}
EOS_UTILITY_VERSION_TABLE = {'old': unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'old')),
                             'new': unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'new')),
                             unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'old')): 'old',
                             unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'new')): 'new'}
FOCUS_DIRECTION_TABLE = {'far': unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'far')),
                         'near': unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'near')),
                         unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'far')): 'far',
                         unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'near')): 'near'}
FOCUS_STEP_MODE_TABLE = {'small': unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'small')),
                         'medium': unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'medium')),
                         'large': unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'large')),
                         unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'small')): 'small',
                         unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'medium')): 'medium',
                         unicode(QtGui.QApplication.translate("eosUtilityPlugins", 'large')): 'large'}


class EOSUtilityShutter(AbstractShutterPlugin):
    """ Plugin for the EOS Utility triggering program.
    """
    def _init(self):
        pass

    def _getTimeValue(self):
        return -1

    def _getMirrorLockup(self):
        return False

    def _getBracketingNbPicts(self):
        return 1

    def _getBracketingIntent(self):
        return 'exposure'

    def _defineConfig(self):
        Logger().trace("EOSUtilityShutter._defineConfig()")
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_programPath', 'PROGRAM_PATH', default=DEFAULT_PROGRAM_PATH)
        self._addConfigKey('_eosUtilityVersion', 'EOS_UTILITY_VERSION', default=DEFAULT_EOS_UTILITY_VERSION)
        self._addConfigKey('_bracketingStep', 'BRACKETING_STEP', default=DEFAULT_BRACKETING_STEP)
        self._addConfigKey('_bracketingType', 'BRACKETING_TYPE', default=DEFAULT_BRACKETING_TYPE)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NB_PICTS)
        self._addConfigKey('_dryRun', 'DRY_RUN', default=DEFAULT_DRY_RUN)
        self._addConfigKey('_bulbEnable', 'BULB_ENABLE', default=DEFAULT_BULB_ENABLE)
        self._addConfigKey('_bulbBseExposure', 'BULB_BASE_EXPOSURE', default=DEFAULT_BULB_BASE_EXPOSURE)
        self._addConfigKey('_focusEnable', 'FOCUS_ENABLE', default=DEFAULT_FOCUS_ENABLE)
        self._addConfigKey('_focusDirection', 'FOCUS_DIRECTION', default=DEFAULT_FOCUS_DIRECTION)
        self._addConfigKey('_focusStep', 'FOCUS_STEP', default=DEFAULT_FOCUS_STEP)
        self._addConfigKey('_focusStepCount', 'FOCUS_STEP_COUNT', default=DEFAULT_FOCUS_STEP_COUNT)
        self._addConfigKey('_focusNbPicts', 'FOCUS_NB_PICTS', default=DEFAULT_FOCUS_NB_PICTS)

    def lockupMirror(self):
        Logger().warning("EOSUtilityShutter.lockupMirror(): Not possible with EOS Utility")
        return 0

    def shoot(self, bracketNumber):
        Logger().debug("EOSUtilityShutter.shoot(): bracketNumber=%d" % bracketNumber)
        Logger().debug("EOSUtilityShutter.shoot(): Program Path=%s" % self._config['PROGRAM_PATH'])
        Logger().debug("EOSUtilityShutter.shoot(): EOS Utility version=%s" % self._config['EOS_UTILITY_VERSION'])
        Logger().debug("EOSUtilityShutter.shoot(): Bracketing step=%s" % self._config['BRACKETING_STEP'])
        Logger().debug("EOSUtilityShutter.shoot(): Bracketing type=%s" % self._config['BRACKETING_TYPE'])
        Logger().debug("EOSUtilityShutter.shoot(): Bracketing nb pict=%d" % self._config['BRACKETING_NB_PICTS'])
        Logger().debug("EOSUtilityShutter.shoot(): Dry run=%s" % self._config['DRY_RUN'])
        Logger().debug("EOSUtilityShutter.shoot(): Bulb enable=%s" % self._config['BULB_ENABLE'])
        Logger().debug("EOSUtilityShutter.shoot(): Bulb base exposure %d s" % self._config['BULB_BASE_EXPOSURE'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus enable=%s" % self._config['FOCUS_ENABLE'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus direction=%s" % self._config['FOCUS_DIRECTION'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus step=%s" % self._config['FOCUS_STEP'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus step count=%d" % self._config['FOCUS_STEP_COUNT'])
        Logger().debug("EOSUtilityShutter.shoot(): Focus nb picts=%d" % self._config['FOCUS_NB_PICTS'])

        args = []
        args.append(self._config['PROGRAM_PATH'])
        args.append("CL")
        args.append(EOS_UTILITY_VERSION_TABLE[self._config['EOS_UTILITY_VERSION']])
        args.append(self._config['BRACKETING_STEP'])
        args.append(BRACKETING_TYPE_INDEX[self._config['BRACKETING_TYPE']])
        args.append(str(self._config['BRACKETING_NB_PICTS']))
        if self._config['DRY_RUN']:
            args.append("n")
        else:
            args.append("y")
        if self._config['BULB_ENABLE']:
            args.append("y")
        else:
            args.append("n")
        args.append(str(self._config['BULB_BASE_EXPOSURE']))
        if self._config['FOCUS_ENABLE']:
            args.append("y")
        else:
            args.append("n")
        args.append(FOCUS_DIRECTION_TABLE[self._config['FOCUS_DIRECTION']])
        args.append(FOCUS_STEP_MODE_TABLE[self._config['FOCUS_STEP']])
        args.append(str(self._config['FOCUS_STEP_COUNT']))
        args.append(str(self._config['FOCUS_NB_PICTS']))
        Logger().debug("EOSUtilityShutter.shoot(): cmdLineArgs '%s'..." % ' '.join(args))

        # Launch external command
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if stderr:
            Logger().debug("EOSUtilityShutter.shoot(): stderr:\n%s" % stderr)
        Logger().debug("EOSUtilityShutter.shoot(): stdout:\n%s" % stdout)

        return p.returncode


class EOSUtilityShutterController(ShutterPluginController):
    def _defineGui(self):
        Logger().trace("EOSUtilityShutterController._defineGui()")
        ShutterPluginController._defineGui(self)
        self._addWidget('Main', LABEL_PROGRAM_PATH,
                        FileSelectorField, (TEXT_CHOOSE_PROGRAM_PATH, TEXT_CHOOSE_PROGRAM_PATH_FILTER),
                        'PROGRAM_PATH')
        types = [EOS_UTILITY_VERSION_TABLE['old'], EOS_UTILITY_VERSION_TABLE['new']]
        self._addWidget('Main', LABEL_EOS_UTILITY_VERSION, ComboBoxField, (types,), 'EOS_UTILITY_VERSION')
        self._addWidget('Main', LABEL_BRACKETING_NB_PICTS, SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')
        steps = ['1/3', '2/3', '1', '1 1/3', '1 2/3', '2', '2 1/3', '2 2/3','3',
                 '3 1/3', '3 2/3', '4', '4 1/3', '4 2/3', '5', '5 1/3', '5 2/3', '6']
        self._addWidget('Main', LABEL_BRACKETING_STEP, ComboBoxField, (steps,), 'BRACKETING_STEP')
        self._addWidget('Main', LABEL_BRACKETING_TYPE, ComboBoxField, (BRACKETING_TYPE_INDEX.keys(),), 'BRACKETING_TYPE')
        self._addWidget('Main', LABEL_DRY_RUN, CheckBoxField, (), 'DRY_RUN')
        self._addTab('Bulb', TAB_BULB)
        self._addWidget('Bulb', LABEL_BULB_ENABLE, CheckBoxField, (), 'BULB_ENABLE')
        self._addWidget('Bulb', LABEL_BULB_BASE_EXPOSURE, SpinBoxField, (1, 99, "", " s"), 'BULB_BASE_EXPOSURE')
        self._addTab('Focus', TAB_FOCUS)
        self._addWidget('Focus',  LABEL_FOCUS_ENABLE, CheckBoxField, (), 'FOCUS_ENABLE')
        focusDir = [FOCUS_DIRECTION_TABLE['far'], FOCUS_DIRECTION_TABLE['near']]
        self._addWidget('Focus', LABEL_FOCUS_DIRECTION, ComboBoxField, (focusDir,), 'FOCUS_DIRECTION')
        stepMode = [FOCUS_STEP_MODE_TABLE['small'], FOCUS_STEP_MODE_TABLE['medium'], FOCUS_STEP_MODE_TABLE['large']]
        self._addWidget('Focus',  LABEL_FOCUS_STEP, ComboBoxField, (stepMode,), 'FOCUS_STEP')
        self._addWidget('Focus', LABEL_FOCUS_STEP_COUNT, SpinBoxField, (1, 99), 'FOCUS_STEP_COUNT')
        self._addWidget('Focus', LABEL_FOCUS_NB_PICTS, SpinBoxField, (1, 99), 'FOCUS_NB_PICTS')

def register():
    """ Register plugins.
    """
    PluginsManager().register(EOSUtilityShutter, EOSUtilityShutterController, capacity='shutter', name=NAME)
