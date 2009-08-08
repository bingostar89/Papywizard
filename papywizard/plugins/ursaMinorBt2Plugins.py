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

- UrsaMinorBt2Shutter
- UrsaMinorBt2ShutterController

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

NAME = "Ursa Minor BT2"

DEFAULT_FOCUS = False
DEFAULT_FOCUS_PULSE = 0.5  # (s)
DEFAULT_MAINTAIN_FOCUS = False


class UrsaMinorBt2Shutter(AbstractHardwarePlugin, AbstractStandardShutterPlugin):  # Use a AbstractEnhancedShutterPlugin
    """
    """
    def _init(self):
        Logger().trace("UrsaMinorBt2Shutter._init()")
        AbstractHardwarePlugin._init(self)
        AbstractStandardShutterPlugin._init(self)

    def _defineConfig(self):
        AbstractHardwarePlugin._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)
        self._addConfigKey('_focus', 'FOCUS', default=DEFAULT_FOCUS)
        self._addConfigKey('_focusPulse', 'FOCUS_PULSE', default=DEFAULT_FOCUS_PULSE)
        self._addConfigKey('_maintainFocus', 'MAINTAIN_FOCUS', default=DEFAULT_MAINTAIN_FOCUS)

    def _sendCmd(self, cmd, param=""):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @return: answer
        @rtype: str
        """
        cmd = "%s1%s" % (cmd, param)
        for nbTry in xrange(3):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write(":%s\r" % cmd)
                c = ''
                while c not in ('=', '!'):
                    c = self._driver.read(1)
                if c == '!':
                    c = self._driver.read(1) # Get error code
                    raise IOError("%s didn't understand the command '%s' (err=%s)" % (NAME, cmd, c))
                answer = ""
                while True:
                    c = self._driver.read(1)
                    if c == '\r':
                        break
                    answer += c

            except IOError:
                Logger().exception("UrsaMinorBt2Shutter._sendCmd")
                Logger().warning("UrsaMinorBt2Shutter._sendCmd(): can't sent command '%s'. Retrying..." % cmd)
            else:
                break
        else:
            raise HardwareError("%s can't send command '%s'" % (NAME, cmd))
        #Logger().debug("UrsaMinorBt2Shutter._sendCmd(): cmd=%s, ans=%s" % (cmd, answer))

        return answer

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._sendCmd("X", "1")

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._sendCmd("X", "0")

    def activate(self):
        Logger().trace("UrsaMinorBt2Shutter.activate()")

    def deactivate(self):
        Logger().trace("UrsaMinorBt2Shutter.deactivate()")

    def init(self):
        Logger().trace("UrsaMinorBt2Shutter.init()")

    def shutdown(self):
        Logger().trace("UrsaMinorBt2Shutter.shutdown()")
        try:
            self._triggerOffShutter()
        except AttributeError:
            Logger().exception("UrsaMinorBt2Shutter.shutdown", debug=True)


class UrsaMinorBt2ShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Hard', "Focus", CheckBoxField, (), 'FOCUS')
        self._addWidget('Hard', "Focus pulse", DoubleSpinBoxField, (0.1, 5., 1, 0.1, "", " s"), 'FOCUS_PULSE')
        self._addWidget('Hard', "Maintain focus", CheckBoxField, (), 'MAINTAIN_FOCUS')


def register():
    """ Register plugins.
    """
    PluginsManager().register(UrsaMinorBt2Shutter, UrsaMinorBt2ShutterController, capacity='shutter', name=NAME)
