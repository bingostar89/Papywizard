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
from papywizard.plugins.shutterPluginController import AbstractPluginController
from papywizard.view.pluginFields import LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField

NAME = "Generic Tethered"

DEFAULT_MIRROR_LOCKUP = False
DEFAULT_MIRROR_LOCKUP_COMMAND = "gphoto2 --capture-image"
DEFAULT_SHOOT_COMMAND = "gphoto2 --capture-image"
DEFAULT_TIME_VALUE = 0.
DEFAULT_PARAM_0 = ""
DEFAULT_PARAM_1 = ""
DEFAULT_PARAM_2 = ""
DEFAULT_PARAM_3 = ""
DEFAULT_PARAM_4 = ""

LABEL_MIRROR_LOCKUP = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Mirror lockup"))
LABEL_MIRROR_LOCKUP_COMMAND = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Mirror lockup command"))
LABEL_SHOOT_COMMAND = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Shoot command"))
LABEL_TIME_VALUE = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Time value"))

TAB_PARAMS = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Params"))
LABEL_PARAM_0 = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Parameter 'p0'"))
LABEL_PARAM_1 = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Parameter 'p1'"))
LABEL_PARAM_2 = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Parameter 'p2'"))
LABEL_PARAM_3 = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Parameter 'p3'"))
LABEL_PARAM_4 = unicode(QtGui.QApplication.translate("genericTetheredPlugins", "Parameter 'p4'"))


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
        return 1

    def _defineConfig(self):
        Logger().trace("GenericTetheredShutter._defineConfig()")
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_mirrorLockupCommand', 'MIRROR_LOCKUP_COMMAND', default=DEFAULT_MIRROR_LOCKUP_COMMAND)
        self._addConfigKey('_shootCommand', 'SHOOT_COMMAND', default=DEFAULT_SHOOT_COMMAND)
        self._addConfigKey('_timeValue', 'TIME_VALUE', default=DEFAULT_TIME_VALUE)
        self._addConfigKey('_parameter0', 'PARAM_0', default=DEFAULT_PARAM_0)
        self._addConfigKey('_parameter1', 'PARAM_1', default=DEFAULT_PARAM_1)
        self._addConfigKey('_parameter2', 'PARAM_2', default=DEFAULT_PARAM_2)
        self._addConfigKey('_parameter3', 'PARAM_3', default=DEFAULT_PARAM_3)
        self._addConfigKey('_parameter4', 'PARAM_4', default=DEFAULT_PARAM_4)

    def lockupMirror(self):
        Logger().debug("GenericTetheredShutter.lockupMirror(): execute command '%s'..." % self._config['MIRROR_LOCKUP_COMMAND'])

        # Launch external command
        args = self._config['MIRROR_LOCKUP_COMMAND'].split()
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if stderr:
            Logger().error("GenericTetheredShutter.lockupMirror(): stderr:\n%s" % stderr.strip())
        Logger().debug("GenericTetheredShutter.lockupMirror(): stdout:\n%s" % stdout.strip())

        return p.returncode

    def shoot(self, bracketNumber):
        Logger().debug("GenericTetheredShutter.shoot(): bracketNumber=%d" % bracketNumber)

        # Get custom params
        parameters = {'p0': self._config['PARAM_0'],
                      'p1': self._config['PARAM_1'],
                      'p2': self._config['PARAM_2'],
                      'p3': self._config['PARAM_3'],
                      'p4': self._config['PARAM_4']}

        # Launch external command
        startShootingTime = time.time()
        cmd = self._config['SHOOT_COMMAND'] + " %(p0)s %(p1)s %(p2)s %(p3)s %(p4)s"
        cmd = cmd % parameters
        args = cmd.split()
        Logger().debug("GenericTetheredShutter.shoot(): execute command '%s'..." % cmd)
        args = cmd.split()
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait end of execution
        stdout, stderr = p.communicate()
        if stderr:
            Logger().error("GenericTetheredShutter.shoot(): stderr:\n%s" % stderr.strip())
        Logger().debug("GenericTetheredShutter.shoot(): stdout:\n%s" % stdout.strip())

        # Ensure time value delay elapsed
        if p.returncode == 0:
            delay = time.time() - startShootingTime
            if delay > 0:
                Logger().debug("GenericTetheredPlugin.shoot(): wait %.1fs additionnal delay" % delay)
                time.sleep(delay)

        return p.returncode


class GenericTetheredShutterController(AbstractPluginController):
    def _defineGui(self):
        Logger().trace("GenericTetheredShutterController._defineGui()")
        #AbstractPluginController._defineGui(self)
        self._addWidget('Main', LABEL_MIRROR_LOCKUP, CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', LABEL_MIRROR_LOCKUP_COMMAND, LineEditField, (), 'MIRROR_LOCKUP_COMMAND')
        self._addWidget('Main', LABEL_SHOOT_COMMAND, LineEditField, (), 'SHOOT_COMMAND')
        self._addWidget('Main', LABEL_TIME_VALUE, DoubleSpinBoxField, (0.1, 99.9, 1, .1, "", u" s"), 'TIME_VALUE')
        self._addTab('Params', TAB_PARAMS)
        self._addWidget('Params', LABEL_PARAM_0, LineEditField, (), 'PARAM_0')
        self._addWidget('Params', LABEL_PARAM_1, LineEditField, (), 'PARAM_1')
        self._addWidget('Params', LABEL_PARAM_2, LineEditField, (), 'PARAM_2')
        self._addWidget('Params', LABEL_PARAM_3, LineEditField, (), 'PARAM_3')
        self._addWidget('Params', LABEL_PARAM_4, LineEditField, (), 'PARAM_4')


def register():
    """ Register plugins.
    """
    PluginsManager().register(GenericTetheredShutter, GenericTetheredShutterController, capacity='shutter', name=NAME)
