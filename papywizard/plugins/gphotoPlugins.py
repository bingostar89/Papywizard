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

- GphotoShutter
- GphotoShutterController

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

NAME = "Gphoto"

DEFAULT_MIRROR_LOCKUP = False
DEFAULT_BRACKETING_NBPICTS = 1
DEFAULT_BRACKETING_STEP = 1.

GET_CONFIG_COMMAND = "gphoto2 --set-config evstep=1 --set-config capturetarget=0 --get-config exposurebiascompensation"
#MIRROR_LOCKUP_COMMAND = "gphoto2 --capture-image"
SHOOT_COMMAND = "gphoto2 --get-config time --set-config exposurebiascompensation=%(index)d --capture-image-and-download"


class GphotoShutter(AbstractShutterPlugin):
    """
    """
    def _init(self):
        self.__exposureBiasTable = {'0.3 EV': [],
                                    '0.5 EV': []
                                    }

    def _getTimeValue(self):
        return -1

    def _getMirrorLockup(self):
        return self._config['MIRROR_LOCKUP']

    def _getBracketingNbPicts(self):
        return self._config['BRACKETING_NB_PICTS']

    def _defineConfig(self):
        Logger().debug("GphotoShutter._defineConfig()")
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NBPICTS)
        self._addConfigKey('_bracketingStep', 'BRACKETING_STEP', default=DEFAULT_BRACKETING_STEP)

    def lockupMirror(self):
        # @todo: implement mirror lockup command
        Logger().debug("GphotoShutter.lockupMirror(): execute command '%s'..." % MIRROR_LOCKUP_COMMAND)
        time.sleep(1)
        Logger().debug("GphotoShutter.lockupMirror(): command over")
        return 0

    def shoot(self, bracketNumber):
        Logger().debug("GphotoShutter.shoot(): bracketNumber=%d" % bracketNumber)

        # Get exposure bias list (only once)
        if not self.__exposureBiasTable['0.5 EV']:
            Logger().debug("GphotoShutter.shoot(): get camera configuration")

            # Launch external command
            cmd = GET_CONFIG_COMMAND
            args = cmd.split()
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait end of execution
            stdout, stderr = p.communicate()
            if stderr:
                Logger().error("GphotoShutter.shoot(): stderr:\n%s" % stderr.strip())
            Logger().debug("GphotoShutter.shoot(): stdout:\n%s" % stdout.strip())

            if not p.returncode:
                for line in stdout.split('\n'):
                    if line.startswith("Choice"):
                        bias = line.split()[-1]  # Get last field
                        self.__exposureBiasTable['0.5 EV'].append(float(bias) / 1000.)
            Logger().debug("GphotoShutter.shoot(): __exposureBiasTable=%s" % self.__exposureBiasTable)

        # Compute exposure bias according to bracketNumber
        bias = (bracketNumber - 1 - int(self._config['BRACKETING_NB_PICTS'] / 2)) * self._config['BRACKETING_STEP']
        Logger().debug("GphotoShutter.shoot(): exposure bias=%f" % bias)

        # Retreive index in exposure table
        index = self.__exposureBiasTable["0.5 EV"].index(bias)

        cmd = SHOOT_COMMAND % {'index': index}
        Logger().debug("GphotoShutter.shoot(): execute command '%s'..." % cmd)

        # Launch external command
        args = cmd.split()
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if stderr:
            Logger().error("GphotoShutter.shoot(): stderr:\n%s" % stderr.strip())
        Logger().debug("GphotoShutter.shoot(): stdout:\n%s" % stdout.strip())

        return p.returncode


class GphotoShutterController(ShutterPluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        self._addWidget('Main', QtGui.QApplication.translate("GphotoShutterController", "Mirror lockup"),
                        CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', QtGui.QApplication.translate("GphotoShutterController", "Bracketing nb picts"),
                        SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')
        self._addWidget('Main', QtGui.QApplication.translate("GphotoShutterController", "Bracketing step"),
                        DoubleSpinBoxField, (0.5, 5., 1, 0.5, "", " ev"), 'BRACKETING_STEP')


def register():
    """ Register plugins.
    """
    PluginsManager().register(GphotoShutter, GphotoShutterController, capacity='shutter', name=NAME)
