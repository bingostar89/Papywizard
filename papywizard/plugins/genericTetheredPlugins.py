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

- GenericTetheredShutter
- GenericTetheredShutterController

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

NAME = "Generic Tethered"

DEFAULT_MIRROR_LOCKUP = False
DEFAULT_MIRROR_LOCKUP_COMMAND = "gphoto2 --capture-image"
DEFAULT_SHOOT_COMMAND = "gphoto2 --capture-image"
DEFAULT_BRACKETING_NBPICTS = 1


class GenericTetheredShutter(AbstractShutterPlugin):
    """
    """
    def _init(self):
        pass

    def _getTimeValue(self):
        return -1

    def _getMirrorLockup(self):
        return self._config['MIRROR_LOCKUP']

    def _getBracketingNbPicts(self):
        return self._config['BRACKETING_NB_PICTS']

    def _defineConfig(self):
        Logger().trace("GenericTetheredShutter._defineConfig()")
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_mirrorLockupCommand', 'MIRROR_LOCKUP_COMMAND', default=DEFAULT_MIRROR_LOCKUP_COMMAND)
        self._addConfigKey('_shootCommand', 'SHOOT_COMMAND', default=DEFAULT_SHOOT_COMMAND)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NBPICTS)

    def lockupMirror(self):
        # @todo: implement mirror lockup command
        Logger().debug("GenericTetheredShutter.lockupMirror(): execute command '%s'..." % self._config['MIRROR_LOCKUP_COMMAND'])
        time.sleep(1)
        Logger().debug("GenericTetheredShutter.lockupMirror(): command over")
        return 0

    def shoot(self, bracketNumber):
        Logger().debug("GenericTetheredShutter.shoot(): bracketNumber=%d" % bracketNumber)
        Logger().debug("GenericTetheredShutter.shoot(): execute command '%s'..." % self._config['SHOOT_COMMAND'])

        # Launch external command
        args = self._config['SHOOT_COMMAND'].split()
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if stderr:
            Logger().error("GenericTetheredShutter.shoot(): stderr:\n%s" % stderr.strip())
        Logger().debug("GenericTetheredShutter.shoot(): stdout:\n%s" % stdout.strip())

        return p.returncode


class GenericTetheredShutterController(ShutterPluginController):
    def _defineGui(self):
        Logger().trace("GenericTetheredShutterController._defineGui()")
        ShutterPluginController._defineGui(self)
        self._addWidget('Main', QtGui.QApplication.translate("GenericTetheredShutterController", "Mirror lockup"),
                        CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', QtGui.QApplication.translate("GenericTetheredShutterController", "Mirror lockup command"),
                        LineEditField, (), 'MIRROR_LOCKUP_COMMAND')
        self._addWidget('Main', QtGui.QApplication.translate("GenericTetheredShutterController", "Shoot command"),
                        LineEditField, (), 'SHOOT_COMMAND')
        self._addWidget('Main', QtGui.QApplication.translate("GenericTetheredShutterController", "Bracketing nb picts"),
                        SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')


def register():
    """ Register plugins.
    """
    PluginsManager().register(GenericTetheredShutter, GenericTetheredShutterController, capacity='shutter', name=NAME)
