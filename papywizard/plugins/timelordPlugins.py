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

- TimelordShutter
- TimelordShutterController

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
                                         CheckBoxField, SliderField, FileSelectorField

NAME = "Timelord"

DEFAULT_PROGRAM_PATH = "C:\\Program Files\\OxfordEye\\Timelord\\Timelord.exe"
DEFAULT_LRD_FILE = "C:\\Documents and Settings\\win2k\\My Documents\\timelord.lrd"

LABEL_PROGRAM_PATH = unicode(QtGui.QApplication.translate("timelordPlugins", "Program path"))
TEXT_CHOOSE_PROGRAM_PATH = unicode(QtGui.QApplication.translate("timelordPlugins", "Choose program path..."))
TEXT_CHOOSE_PROGRAM_PATH_FILTER = unicode(QtGui.QApplication.translate("timelordPlugins", "EXE files (*.exe);;All files (*)"))
LABEL_LRD_FILE = unicode(QtGui.QApplication.translate("timelordPlugins", "LRD file"))
TEXT_CHOOSE_LRD_FILE = unicode(QtGui.QApplication.translate("timelordPlugins", "Choose LRD file..."))
TEXT_CHOOSE_LRD_FILE_FILTER = unicode(QtGui.QApplication.translate("timelordPlugins", "LRD files (*.lrd);;All files (*)"))


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
        Logger().trace("TimelordShutter._defineConfig()")
        #AbstractShutterPlugin._defineConfig(self)
        self._addConfigKey('_programPath', 'PROGRAM_PATH', default=DEFAULT_PROGRAM_PATH)
        self._addConfigKey('_lrdFilePath', 'LRD_FILE', default=DEFAULT_LRD_FILE)

    def lockupMirror(self):
        Logger().warning("TimelordShutter.lockupMirror(): Not possible with TimeLord")
        return 0

    def shoot(self, bracketNumber):
        Logger().debug("TimelordShutter.shoot(): bracketNumber=%d" % bracketNumber)
        Logger().debug("TimelordShutter.shoot(): execute command '%s %s'..." % (self._config['PROGRAM_PATH'], self._config['LRD_FILE']))

        # Launch external command
        args = [self._config['PROGRAM_PATH'], self._config['LRD_FILE']]
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


class TimelordShutterController(AbstractPluginController):
    def _defineGui(self):
        Logger().trace("TimelordShutterController._defineGui()")
        #AbstractPluginController._defineGui(self)
        self._addWidget('Main', LABEL_PROGRAM_PATH,
                        FileSelectorField, (TEXT_CHOOSE_PROGRAM_PATH, TEXT_CHOOSE_PROGRAM_PATH_FILTER),
                        'PROGRAM_PATH')
        self._addWidget('Main', LABEL_LRD_FILE,
                        FileSelectorField, (TEXT_CHOOSE_LRD_FILE, TEXT_CHOOSE_LRD_FILE_FILTER),
                        'LRD_FILE')


def register():
    """ Register plugins.
    """
    PluginsManager().register(TimelordShutter, TimelordShutterController, capacity='shutter', name=NAME)
