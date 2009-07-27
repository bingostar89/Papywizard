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

- TimelordShutter
- TimelordShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import subprocess

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

NAME = "Timelord"

DEFAULT_PROGRAM_PATH = "C:\\Program Files\\OxfordEye\\Timelord\\Timelord.exe"
DEFAULT_LRD_FILE_PATH = "C:\\Documents and Settings\\win2k\\My Documents\\timelord.lrd"


class TimelordShutter(AbstractShutterPlugin):
    """
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
        return None

    def _defineConfig(self):
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('Program path', 'PROGRAM_PATH', default=DEFAULT_PROGRAM_PATH)
        self._addConfigKey('LRD file path', 'LRD_FILE_PATH', default=DEFAULT_LRD_FILE_PATH)

    def activate(self):
        Logger().trace("TimelordShutter.activate()")

    def deactivate(self):
        Logger().trace("TimelordShutter.deactivate()")

    def establishConnection(self):
        Logger().trace("TimelordShutter.establishConnection()")

    def stopConnection(self):
        Logger().trace("TimelordShutter.stopConnection()")

    def init(self):
        Logger().trace("TimelordShutter.init()")

    def shutdown(self):
        Logger().trace("TimelordShutter.shutdown()")

    def shoot(self, bracketNumber):
        Logger().debug("TimelordShutter.shoot(): execute command '%s %s'..." % (self._config['PROGRAM_PATH'], self._config['LRD_FILE_PATH']))

        # Launch external command
        args = [self._config['PROGRAM_PATH'], self._config['LRD_FILE_PATH']]
        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            Logger().exception("TimelordShutter.shoot()")
            return 1

        # Wait end of execution
        stdout, stderr = p.communicate()
        if stderr:
            Logger().debug("TimelordShutter.shoot(): stderr:\n%s" % stderr)
        Logger().debug("TimelordShutter.shoot(): stdout:\n%s" % stdout)

        return p.returncode


class TimelordShutterController(ShutterPluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        self._addWidget('Main', "Program path", LineEditField, (), 'PROGRAM_PATH')
        self._addWidget('Main', "LRD file path", LineEditField, (), 'LRD_FILE_PATH')


def register():
    """ Register plugins.
    """
    PluginsManager().register(TimelordShutter, TimelordShutterController, capacity='shutter', name=NAME)
