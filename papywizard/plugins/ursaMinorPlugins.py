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

Hardware

Implements
==========

- UrsaMinorUsbShutter
- UrsaMinorUsbShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.abstractStandardShutterPlugin import AbstractStandardShutterPlugin
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.standardShutterPluginController import StandardShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

NAME = "Ursa Minor USB"

DEFAULT_TRIGGER_LINE = 'RTS'
DEFAULT_TRIGGER_LINE_INVERTED = False

lineLevel = {False: {'on': 1, 'off': 0},
             True: {'on': 0, 'off': 1}}


class UrsaMinorUsbShutter(AbstractHardwarePlugin, AbstractStandardShutterPlugin):
    """
    """
    def _init(self):
        Logger().trace("UrsaMinorUsbShutter._init()")
        AbstractHardwarePlugin._init(self)
        AbstractStandardShutterPlugin._init(self)

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)
        self._addConfigKey('_triggerLine', 'TRIGGER_LINE', default=DEFAULT_TRIGGER_LINE)
        self._addConfigKey('_triggerLineInverted', 'TRIGGER_LINE_INVERTED', default=DEFAULT_TRIGGER_LINE_INVERTED)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        method = getattr(self._driver, "set%s" % self._config['TRIGGER_LINE'])
        method(lineLevel[self._config['TRIGGER_LINE_INVERTED']]['on'])

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        method = getattr(self._driver, "set%s" % self._config['TRIGGER_LINE'])
        method(lineLevel[self._config['TRIGGER_LINE_INVERTED']]['off'])

    def activate(self):
        Logger().trace("UrsaMinorUsbShutter.activate()")

    def deactivate(self):
        Logger().trace("UrsaMinorUsbShutter.deactivate()")

    def init(self):
        Logger().trace("UrsaMinorUsbShutter.init()")

    def shutdown(self):
        Logger().trace("UrsaMinorUsbShutter.shutdown()")
        try:
            self._triggerOffShutter()
        except AttributeError:
            Logger().exception("UrsaMinorUsbShutter.shutdown", debug=True)


class UrsaMinorUsbShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Hard', "Trigger line", ComboBoxField, (['RTS', 'DTR'],), 'TRIGGER_LINE')
        self._addWidget('Hard', "Line inverted", CheckBoxField, (), 'TRIGGER_LINE_INVERTED')


def register():
    """ Register plugins.
    """
    PluginsManager ().register(UrsaMinorUsbShutter, UrsaMinorUsbShutterController, capacity='shutter', name=NAME)
