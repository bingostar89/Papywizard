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

Graphical toolkit controller

Implements
==========

- TotalFovController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractModalDialogController


class TotalFovController(AbstractModalDialogController):
    """ Total fov controller object.
    """
    def _init(self):
        self._uiFile = "totalFovDialog.ui"

    def _initWidgets(self):
        pass

    # Callbacks
    def _onAccepted(self):
        """ Ok button has been clicked.
        """
        Logger().trace("TotalFovController._onAccepted()")
        yawFov = self._view.yawFovDoubleSpinBox.value()
        pitchFov = self._view.pitchFovDoubleSpinBox.value()
        self._model.setCornersFromFov(yawFov, pitchFov)
        Logger().debug("MainController._onAccepted(): total fov set to yaw=%.1f, pitch=%.1f" % (yawFov, pitchFov))

    # Interface
    def refreshView(self):
        currentYawFov = self._model.mosaic.yawFov
        currentPitchFov = self._model.mosaic.pitchFov
        self._view.yawFovDoubleSpinBox.setValue(currentYawFov)
        self._view.pitchFovDoubleSpinBox.setValue(currentPitchFov)
