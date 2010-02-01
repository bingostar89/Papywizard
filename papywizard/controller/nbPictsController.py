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

- NbPictsController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractModalDialogController


class NbPictsController(AbstractModalDialogController):
    """ Nb picts controller object.
    """
    def _init(self):
        self._uiFile = "nbPictsDialog.ui"

    def _initWidgets(self):

        # Set limits
        maxYawNbPicts = 200 # Compute the maximum number of pictures
        maxPitchNbPicts = 200
        self._view.yawNbPictsSpinBox.setRange(1, maxYawNbPicts)
        self._view.pitchNbPictsSpinBox.setRange(1, maxPitchNbPicts)

    # Callbacks
    def _onAccepted(self):
        """ Ok button has been clicked.
        """
        Logger().trace("NbPictsController._onAccepted()")
        yawNbPicts = self._view.yawNbPictsSpinBox.value()
        pitchNbPicts = self._view.pitchNbPictsSpinBox.value()
        self._model.setCornersFromNbPicts(yawNbPicts, pitchNbPicts)
        Logger().debug("NbPictsController._onAccepted(): nb picts set to yaw=%d, pitch=%d" % (yawNbPicts, pitchNbPicts))

    # Interface
    def refreshView(self):
        currentYawNbPicts = self._model.mosaic.yawNbPicts
        currentPitchNbPicts = self._model.mosaic.pitchNbPicts
        self._view.yawNbPictsSpinBox.setValue(currentYawNbPicts)
        self._view.pitchNbPictsSpinBox.setValue(currentPitchNbPicts)
