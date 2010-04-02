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

- GenericTetheredShutter
- GenericTetheredShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL

@todo: add support of var in commands, like %(bracketNumber)d or so...
"""

__revision__ = "$Id$"

import time
import subprocess

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, \
                                         CheckBoxField, SliderField, FileSelectorField

NAME = "Generic Tethered"

DEFAULT_MIRROR_LOCKUP = False
DEFAULT_MIRROR_LOCKUP_COMMAND = "gphoto2 --capture-image"
DEFAULT_SHOOT_COMMAND = "gphoto2 --capture-image"
DEFAULT_BRACKETING_NBPICTS = 1

LABEL_MIRROR_LOCKUP = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Mirror lockup"))
LABEL_MIRROR_LOCKUP_COMMAND = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Mirror lockup command"))
#TEXT_CHOOSE_MIRROR_LOCKUP_COMMAND = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Choose mirror lockup command..."))
#TEXT_CHOOSE_MIRROR_LOCKUP_COMMAND_FILTER = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "All files (*)"))
LABEL_SHOOT_COMMAND = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Shoot command"))
#TEXT_CHOOSE_SHOOT_COMMAND = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Choose shoot command..."))
#TEXT_CHOOSE_SHOOT_COMMAND_FILTER = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "All files (*)"))
LABEL_BRACKETING_NB_PICTS = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Bracketing nb picts"))


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
        self._addWidget('Main', LABEL_MIRROR_LOCKUP, CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', LABEL_MIRROR_LOCKUP_COMMAND, LineEditField, (), 'MIRROR_LOCKUP_COMMAND')
        #self._addWidget('Main', LABEL_MIRROR_LOCKUP_COMMAND,
                        #FileSelectorField, (TEXT_CHOOSE_MIRROR_LOCKUP_COMMAND, TEXT_CHOOSE_MIRROR_LOCKUP_COMMAND_FILTER),
                        #'MIRROR_LOCKUP_COMMAND')
        self._addWidget('Main', LABEL_SHOOT_COMMAND, LineEditField, (), 'SHOOT_COMMAND')
        #self._addWidget('Main', LABEL_SHOOT_COMMAND,
                        #FileSelectorField, (TEXT_CHOOSE_SHOOT_COMMAND, TEXT_CHOOSE_SHOOT_COMMAND_FILTER),
                        #'SHOOT_COMMAND')
        self._addWidget('Main', LABEL_BRACKETING_NB_PICTS, SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')


def register():
    """ Register plugins.
    """
    PluginsManager().register(GenericTetheredShutter, GenericTetheredShutterController, capacity='shutter', name=NAME)
