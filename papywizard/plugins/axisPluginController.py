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

Controller

Implements
==========

- AxisPluginController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtGui

from papywizard.plugins.abstractPluginController import AbstractPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, DoubleSpinBoxField, \
                                         SpinBoxField, CheckBoxField, SliderField

LABEL_LOW_LIMIT = unicode(QtGui.QApplication.translate("axisPluginController", "Low limit"))
LABEL_HIGH_LIMIT = unicode(QtGui.QApplication.translate("axisPluginController", "High limit"))


class AxisPluginController(AbstractPluginController):
    """ Plugin controller for 'yawAxis' and 'pitchAxis' capacities.
    """
    def _defineGui(self):
        """ Add high/low limits
        """
        self._addWidget('Main', LABEL_LOW_LIMIT, DoubleSpinBoxField, (-9999.9, 9999.9, 1, .1, "", u" °"), 'LOW_LIMIT')
        self._addWidget('Main', LABEL_HIGH_LIMIT, DoubleSpinBoxField, (-9999.9, 9999.9, 1, .1, "", u" °"), 'HIGH_LIMIT')
