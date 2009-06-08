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

- UsbTaShutter
- UsbTaShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: merlinOrionPlugins.py 1888 2009-05-30 08:24:37Z fma $"

import time

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.pluginManager import PluginManager
from papywizard.hardware.hardwarePlugin import HardwarePlugin
from papywizard.hardware.abstractStandardShutterPlugin import AbstractStandardShutterPlugin
from papywizard.controller.hardwarePluginController import HardwarePluginController
from papywizard.controller.standardShutterPluginController import StandardShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

DEFAULT_LINE = 'RTS'
DEFAULT_LINE_INVERTED = False

lineMethod = {'RTS': "setRTS",
              'DTR': "setDTR"}
lineLevel = {False: {'on': 1, 'off': 0},
             True: {'on': 0, 'off': 1}}


class UsbTaShutter(HardwarePlugin, AbstractStandardShutterPlugin):
    _name = "USB TA"

    def _init(self):
        Logger().trace("UsbTaShutter._init()")
        HardwarePlugin._init(self)
        AbstractStandardShutterPlugin._init(self)

    def _defineConfig(self):
        HardwarePlugin._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)
        self._addConfigKey('_line', 'LINE', default=DEFAULT_LINE)
        self._addConfigKey('_lineInverted', 'LINE_INVERTED', default=DEFAULT_LINE_INVERTED)

    def _triggerShutter(self):
        """ Trigger the shutter contact.

        @todo: allow usage of DTR
        @todo: allow inverted signal
        """
        try:
            method = getattr(self._driver, lineMethod[self._config['LINE']])
        except AttributeError:
            Logger().exception("UsbTaShutter._triggerShutter", debug=True)
        else:
            method(lineLevel[self._config['LINE_INVERTED']]['on'])
            time.sleep(self._config['PULSE_WIDTH_HIGH'] / 1000.)
            method(lineLevel[self._config['LINE_INVERTED']]['off'])
            self.__LastShootTime = time.time()

    def activate(self):
        Logger().trace("UsbTaShutter.activate()")

    def shutdown(self):
        Logger().trace("UsbTaShutter.shutdown()")

    def lockupMirror(self):
        Logger().trace("UsbTaShutter.lockupMirror()")
        self._ensurePulseWidthLowDelay()
        self._driver.acquireBus()
        try:
            self._triggerShutter()
            return 0
        finally:
            self._driver.releaseBus()

    def shoot(self, bracketNumber):
        Logger().trace("UsbTaShutter.shoot()")
        self._ensurePulseWidthLowDelay()
        self._driver.acquireBus()
        try:
            self._triggerShutter()

            # Wait for the end of shutter cycle
            delay = self._config['TIME_VALUE'] - self._config['PULSE_WIDTH_HIGH'] / 1000.
            if delay > 0:
                time.sleep(delay)

            return 0
        finally:
            self._driver.releaseBus()


class UsbTaShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Hard', "Line", ComboBoxField, (['RTS', 'DTR'],), 'LINE')
        self._addWidget('Hard', "Line inverted", CheckBoxField, (), 'LINE_INVERTED')



def register():
    """ Register plugins.
    """
    PluginManager().register(UsbTaShutter, UsbTaShutterController)
