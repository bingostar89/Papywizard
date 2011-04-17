# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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

- UrsaMinorUsbShutter
- UrsaMinorUsbShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.hardware.ursaMinorUsbHardware import UrsaMinorUsbHardware
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.shutterPlugin import ShutterPlugin
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

NAME = "Ursa Minor USB"

DEFAULT_TRIGGER_LINE = 'RTS'
DEFAULT_TRIGGER_LINE_INVERTED = False

LABEL_TRIGGER_LINE = unicode(QtGui.QApplication.translate("ursaMinorUsbPlugins", "Trigger line"))
LABEL_LINE_INVERTED = unicode(QtGui.QApplication.translate("ursaMinorUsbPlugins", "Line inverted"))


class UrsaMinorUsbShutter(AbstractHardwarePlugin, ShutterPlugin):
    """
    """
    def _init(self):
        Logger().trace("UrsaMinorUsbShutter._init()")
        AbstractHardwarePlugin._init(self)
        ShutterPlugin._init(self)
        self._hardware = UrsaMinorUsbHardware()

    def _defineConfig(self):
        Logger().trace("UrsaMinorUsbShutter._defineConfig()")
        AbstractHardwarePlugin._defineConfig(self)
        ShutterPlugin._defineConfig(self)
        self._addConfigKey('_triggerLine', 'TRIGGER_LINE', default=DEFAULT_TRIGGER_LINE)
        self._addConfigKey('_triggerLineInverted', 'TRIGGER_LINE_INVERTED', default=DEFAULT_TRIGGER_LINE_INVERTED)

    def configure(self):
        self._hardware.setTriggerLine(self._config['TRIGGER_LINE'])
        self._hardware.setTriggerLineInverted(self._config['TRIGGER_LINE_INVERTED'])

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._hardware.setOutput(True)

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._hardware.setOutput(False)

    def init(self):
        AbstractHardwarePlugin.init(self)
        self.configure()


class UrsaMinorUsbShutterController(ShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        Logger().trace("UrsaMinorUsbShutterController._defineGui()")
        ShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Hard', LABEL_TRIGGER_LINE, ComboBoxField, (['RTS', 'DTR'],), 'TRIGGER_LINE')
        self._addWidget('Hard', LABEL_LINE_INVERTED, CheckBoxField, (), 'TRIGGER_LINE_INVERTED')


def register():
    """ Register plugins.
    """
    PluginsManager().register(UrsaMinorUsbShutter, UrsaMinorUsbShutterController, capacity='shutter', name=NAME)
