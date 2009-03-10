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

- MerlinAxis
- MerlinAxisController
- MerlinYawAxis
- MerlinYawAxisController
- MerlinPitchAxis
- MerlinPitchAxisController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

#from papywizard.common.pluginManager import PluginManager
from papywizard.controller.axisPluginController import AxisPluginController
from papywizard.hardware.axisPlugin import AxisPlugin
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, CheckBoxField


class MerlinAxis(AxisPlugin):
    name = "Merlin"

    def _init(self):
        self._numAxis = None

    def drive(self, position, speed='normal'):
        # Control axis
        pass


class MerlinAxisController(AxisPluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        self._addWidget('General', "Channel", SpinBoxField(1, 2, 1))
        self._addWidget('General', "Speed", ComboBoxField(['low', 'normal', 'fast'], 'normal'))


class MerlinYawAxis(MerlinAxis):
    capacity = 'yawAxis'

    def _init(self):
        self._numAxis = 1


class MerlinYawAxisController(MerlinAxisController):
    pass


class MerlinPitchAxis(MerlinAxis):
    capacity = 'pitchAxis'

    def _init(self):
        self._numAxis = 2


class MerlinPitchAxisController(MerlinAxisController):
    pass


def register():
    """ Register plugins.
    """
    PluginManager().register(MerlinYawAxis, MerlinYawAxisController)
    PluginManager().register(MerlinPitchAxis, MerlinPitchAxisController)


def main():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    plugin = MerlinYawAxis()
    controller = MerlinYawAxisController(parent=None, model=plugin)
    controller.exec_()
