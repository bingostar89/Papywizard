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

Hardware

All of the two contacts of the jack socket are implemented and driven through two optocouplers.
There is a command "X" to drive them. Command format: :X1n  where n can be 0,1,2 or 3.
The two bits represents the two contacts.
The state of the two contact can be read by the ':x1' command.

The Bluetooth interface also has an internal millisecond resolution timer to produce exact timing for shoot or AF trigger.
The internal timer can be programmed in 1ms - 65sec range. Hopefully it is enough for HDR.

The timer can be controlled by this command:
:T1abnnnn

'a' is the state of the two contacts before timer period.
'b' is the state of the two contacts after the timer period expires.
'nnnn' is a hexadecimal value representing range 0000 - ffff in milliseconds.

As you send the T command, the contacts were immediatelly set to 'a'. The timer starts counting, when it expires,
the contats will be set to 'b'.

The operation of the timer is asynchronous.
During the timer period, the unit remains active, it operates noramally, forwards all commands to Merlin.

The state of the timer can be monitored by the ':t1' command.
The format of the response is '=nnnn'.

Implements
==========

- UrsaMinorBt2Shutter
- UrsaMinorBt2ShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger
#from papywizard.hardware.ursaMinorBt2Hardware import UrsaMinorBt2Hardware
from papywizard.hardware.abstractHardware import AbstractHardware
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.shutterPlugin import ShutterPlugin
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField

NAME = "Ursa Minor BT2"

DEFAULT_FOCUS_ENABLE = False
DEFAULT_FOCUS_PULSE_WIDTH = 0.5  # (s)
DEFAULT_FOCUS_MAINTAIN = False

DEFAULT_INTERNAL_TIMER_ENABLE = False

TAB_FOCUS = unicode(QtGui.QApplication.translate("ursaMinorBt2Plugins", 'Focus'))
LABEL_FOCUS_ENABLE = unicode(QtGui.QApplication.translate("ursaMinorBt2Plugins", "Enable"))
LABEL_FOCUS_PULSE_WIDTH = unicode(QtGui.QApplication.translate("ursaMinorBt2Plugins", "Pulse width"))
LABEL_MAINTAIN_FOCUS = unicode(QtGui.QApplication.translate("ursaMinorBt2Plugins", "Maintain with shutter"))


class UrsaMinorBt2Hardware(AbstractHardware):
    """
    """
    def __sendCmd(self, cmd, param=""):
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
                Logger().exception("UrsaMinorBt2Shutter.__sendCmd")
                Logger().warning("UrsaMinorBt2Shutter.__sendCmd(): can't sent command '%s'. Retrying..." % cmd)
            else:
                break
        else:
            raise HardwareError("%s can't send command '%s'" % (NAME, cmd))
        #Logger().debug("UrsaMinorBt2Shutter.__sendCmd(): cmd=%s, ans=%s" % (cmd, answer))

        return answer

    def setOutput(self, focus, shutter):
        """ Set outputs state.

        @param focus: new state of the the AF output
        @type focus: bool

        @param shutter: new state of the shutter output
        @type shutter: bool
        """
        value = int(focus) << 1 + int(shutter)
        self._driver.acquireBus()
        try:
            self.___sendCmd("X", str(value))
        finally:
            self._driver.releaseBus()


class UrsaMinorBt2Shutter(AbstractHardwarePlugin, ShutterPlugin):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        AbstractHardwarePlugin.__init__(self, *args, **kwargs)
        ShutterPlugin.__init__(self, *args, **kwargs)

    def _init(self):
        Logger().trace("UrsaMinorBt2Shutter._init()")
        AbstractHardwarePlugin._init(self)
        ShutterPlugin._init(self)
        self._hardware = UrsaMinorBt2Hardware()

    def _defineConfig(self):
        Logger().trace("UrsaMinorBt2Shutter._defineConfig()")
        AbstractHardwarePlugin._defineConfig(self)
        ShutterPlugin._defineConfig(self)
        self._addConfigKey('_focus', 'FOCUS_ENABLE', default=DEFAULT_FOCUS_ENABLE)
        self._addConfigKey('_focusPulse', 'FOCUS_PULSE_WIDTH', default=DEFAULT_FOCUS_PULSE_WIDTH)
        self._addConfigKey('_maintainFocus', 'FOCUS_MAINTAIN', default=DEFAULT_FOCUS_MAINTAIN)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self.__sendCmd("X", "1")

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self.__sendCmd("X", "0")

    def shutdown(self):
        Logger().trace("UrsaMinorBt2Shutter.shutdown()")
        self._triggerOffShutter()


class UrsaMinorBt2ShutterController(ShutterPluginController, HardwarePluginController):
    def _valueChanged(self, value=None):
        ShutterPluginController._valueChanged(self, value)
        self.refreshView()

    def _defineGui(self):
        Logger().trace("UrsaMinorBt2ShutterController._defineGui()")
        ShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addTab('Focus', TAB_FOCUS)
        self._addWidget('Focus', LABEL_FOCUS_ENABLE, CheckBoxField, (), 'FOCUS_ENABLE')
        self._addWidget('Focus', LABEL_FOCUS_PULSE_WIDTH, DoubleSpinBoxField, (0.1, 5., 1, 0.1, "", " s"), 'FOCUS_PULSE_WIDTH')
        self._addWidget('Focus', LABEL_MAINTAIN_FOCUS, CheckBoxField, (), 'FOCUS_MAINTAIN')

    def refreshView(self):
        focus = self._getWidget('Focus', LABEL_FOCUS_ENABLE).value()
        self._getWidget('Focus', LABEL_FOCUS_PULSE_WIDTH).setDisabled(not focus)
        self._getWidget('Focus', LABEL_MAINTAIN_FOCUS).setDisabled(not focus)


def register():
    """ Register plugins.
    """
    PluginsManager().register(UrsaMinorBt2Shutter, UrsaMinorBt2ShutterController, capacity='shutter', name=NAME)
