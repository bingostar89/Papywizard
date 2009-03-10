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

Controller

Implements
==========

- HardwarePluginController
- AxisPluginController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common.orderedDict import OrderedDict
from papywizard.controller.abstractPluginController import AbstractPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, CheckBoxField, SliderField


class HardwarePluginController(AbstractPluginController):
    """ Plugin controller for hardware-based plugins.
    """
    def _defineGui(self):
        """
        @todo: use ConfigManager to save values
        """
        AbstractPluginController._defineGui(self)
        self._addTab('Com')
        self._addWidget('Com', "driver", ComboBoxField(['bluetooth', 'serial', 'ethernet'], 'bluetooth'))
        self._addWidget('Com', "BT device address", LineEditField("00:50:C2:58:55:B9"))
        self._addWidget('Com', "Serial port", LineEditField("0"))
        self._addWidget('Com', "Ethernet host", LineEditField("localhost"))
        self._addWidget('Com', "Ethernet port", SpinBoxField(1024, 65535, 7165))
        self._addWidget('Com', "Automatic connection", CheckBoxField(False))


class AxisPluginController(HardwarePluginController):
    """ Plugin controller for axis.
    """
