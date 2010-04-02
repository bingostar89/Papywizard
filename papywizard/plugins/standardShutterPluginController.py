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

Controller

Implements
==========

 - StandardShutterPluginController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.plugins.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, \
                                         DoubleSpinBoxField, CheckBoxField, SliderField

LABEL_TIME_VALUE = unicode(QtGui.QApplication.translate("standardShutterPluginController", "Time value"))
LABEL_MIRROR_LOCKUP = unicode(QtGui.QApplication.translate("standardShutterPluginController", "Mirror lockup"))
LABEL_BULB_ENABLE = unicode(QtGui.QApplication.translate("standardShutterPluginController", "Bulb"))
LABEL_BRACKETING_NB_PICTS = unicode(QtGui.QApplication.translate("standardShutterPluginController", "Bracketing nb picts"))

TAB_HARD = unicode(QtGui.QApplication.translate("standardShutterPluginController", 'Hard'))
LABEL_PULSE_WIDTH_HIGH = unicode(QtGui.QApplication.translate("standardShutterPluginController", "Pulse width high"))
LABEL_PULSE_WIDTH_LOW = unicode(QtGui.QApplication.translate("standardShutterPluginController", "Pulse width low"))


class StandardShutterPluginController(ShutterPluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        self._addWidget('Main', LABEL_TIME_VALUE, DoubleSpinBoxField, (0.1, 3600., 1, 0.1, "", " s"), 'TIME_VALUE')
        self._addWidget('Main', LABEL_BULB_ENABLE, CheckBoxField, (), 'BULB_ENABLE')
        self._addWidget('Main', LABEL_MIRROR_LOCKUP, CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', LABEL_BRACKETING_NB_PICTS, SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')
        self._addTab('Hard', TAB_HARD)
        self._addWidget('Hard', LABEL_PULSE_WIDTH_HIGH, SpinBoxField, (10, 1000, "", " ms"), 'PULSE_WIDTH_HIGH')
        self._addWidget('Hard', LABEL_PULSE_WIDTH_LOW, SpinBoxField, (10, 1000, "", " ms"), 'PULSE_WIDTH_LOW')
