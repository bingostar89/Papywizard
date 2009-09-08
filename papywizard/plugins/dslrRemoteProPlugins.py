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

from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

NAME = "DSLR Remote Pro"

DEFAULT_MIRROR_LOCKUP = False
DEFAULT_BRACKETING_NBPICTS = 1
DEFAULT_BRACKETING_STEP = 1.

PROGRAM_PATH = "C:\\Program Files\\breezesys\\DSLrRemotePro\\DSLrRemote.exe"
GET_CONFIG_PARAMS = ""
SHOOT_PARAMS = "-x %(index)d"


class DslrRemoteProShutter(AbstractShutterPlugin):
    """ DSLR Remote Pro plugin class.
    """
    def _init(self):
        self.__biasTable = {}

    def _getTimeValue(self):
        return -1

    def _getMirrorLockup(self):
        return self._config['MIRROR_LOCKUP']

    def _getBracketingNbPicts(self):
        return self._config['BRACKETING_NB_PICTS']

    def _defineConfig(self):
        Logger().debug("DslrRemoteProShutter._defineConfig()")
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NBPICTS)
        self._addConfigKey('_bracketingStep', 'BRACKETING_STEP', default=DEFAULT_BRACKETING_STEP)

    def lockupMirror(self):
        # @todo: implement mirror lockup command
        Logger().debug("DslrRemoteProShutter.lockupMirror(): execute command '%s'..." % MIRROR_LOCKUP_COMMAND)
        time.sleep(1)
        Logger().debug("DslrRemoteProShutter.lockupMirror(): command over")
        return 0

    def shoot(self, bracketNumber):
        Logger().debug("DslrRemoteProShutter.shoot(): bracketNumber=%d" % bracketNumber)

        # Get exposure bias list (only once)
        if not self.__biasTable:

            # Launch external command
            cmd = "%s %s" %( PROGRAM_PATH, GET_CONFIG_PARAMS)
            Logger().debug("DslrRemoteProShutter.shoot(): get config. command '%s'" % cmd)
            args = cmd.split()
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait end of execution
            stdout, stderr = p.communicate()
            if stderr:
                Logger().error("DslrRemoteProShutter.shoot(): stderr:\n%s" % stderr.strip())
            Logger().debug("DslrRemoteProShutter.shoot(): stdout:\n%s" % stdout.strip())

            if not p.returncode:
                for line in stdout.split('\n'):
                    self.__biasTable.append(float(line))
                Logger().debug("DslrRemoteProShutter.shoot(): __biasTable=%s" % self.__biasTable)
            else:
                return p.returncode

        # Compute exposure bias according to bracketNumber
        bias = (bracketNumber - 1 - int(self._config['BRACKETING_NB_PICTS'] / 2)) * self._config['BRACKETING_STEP']
        Logger().debug("DslrRemoteProShutter.shoot(): bias=%f" % bias)

        # Retreive index in exposure table
        index = self.__biasTable.index(bias)

        # Launch external command
        cmd = "%s %s" %( PROGRAM_PATH, SHOOT_PARAMS) % {'index': index}
        Logger().debug("DslrRemoteProShutter.shoot(): shoot command '%s'..." % cmd)
        args = cmd.split()
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if stderr:
            Logger().error("DslrRemoteProShutter.shoot(): stderr:\n%s" % stderr.strip())
        Logger().debug("DslrRemoteProShutter.shoot(): stdout:\n%s" % stdout.strip())

        return p.returncode


class DslrRemoteProShutterController(ShutterPluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        self._addWidget('Main', QtGui.QApplication.translate("DslrRemoteProShutterController", "Mirror lockup"),
                        CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', QtGui.QApplication.translate("DslrRemoteProShutterController", "Bracketing nb picts"),
                        SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')
        self._addWidget('Main', QtGui.QApplication.translate("DslrRemoteProShutterController", "Bracketing step"),
                        DoubleSpinBoxField, (0.5, 5., 1, 0.5, "", " ev"), 'BRACKETING_STEP')


def register():
    """ Register plugins.
    """
    PluginsManager().register(DslrRemoteProShutter, DslrRemoteProShutterController, capacity='shutter', name=NAME)
