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

- GotoController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: nbPictsController.py 2345 2010-04-02 06:05:51Z fma $"

import time

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractModalDialogController
from papywizard.view.messageDialog import WarningMessageDialog, ErrorMessageDialog, \
                                          ExceptionMessageDialog, YesNoMessageDialog, \
                                          AbortMessageDialog


class GotoController(AbstractModalDialogController):
    """ Goto controller object.
    """
    def _init(self):
        self._uiFile = "gotoDialog.ui"

    def _initWidgets(self):
        pass

    def _connectSignals(self):
        AbstractModalDialogController._connectSignals(self)

        self.connect(self._view.goPushButton, QtCore.SIGNAL("clicked()"), self._onGoPushButtonClicked)
        self.connect(self._view.freeRadioButton, QtCore.SIGNAL("toggled(bool)"), self._onFreeRadioButtonToggled)

    def _disconnectSignals(self):
        AbstractModalDialogController._connectSignals(self)

        self.disconnect(self._view.goPushButton, QtCore.SIGNAL("clicked()"), self._onGoPushButtonClicked)
        self.disconnect(self._view.freeRadioButton, QtCore.SIGNAL("toggled(bool)"), self._onFreeRadioButtonToggled)

    # Callbacks
    def _onGoPushButtonClicked(self):
        """ Go push button has been clicked.
        """
        Logger().trace("GotoController.__onGoPushButtonClicked()")
        if self._view.referenceRadioButton.isChecked():
            yaw = 0.
            pitch = 0.
            useOffset = True
        elif self._view.initialRadioButton.isChecked():
            yaw = 0.
            pitch = 0.
            useOffset = False
        elif self._view.freeRadioButton.isChecked():
            yaw = self._view.yawFovDoubleSpinBox.value()
            pitch = self._view.pitchFovDoubleSpinBox.value()
            useOffset = True
        Logger().debug("GotoController.__onGoPushButtonClicked(): yaw=%.1f, pitch=%.1f, useOffset=%s" % (yaw, pitch, useOffset))

        self._model.head.gotoPosition(yaw, pitch, useOffset=useOffset, wait=False)
        dialog = AbortMessageDialog(self.tr("Goto position"), self.tr("Please wait..."))
        dialog.show()
        while self._model.head.isAxisMoving():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)
            if dialog.result() == QtGui.QMessageBox.Abort:
                self._model.head.stopAxis()
                self._parent.setStatusbarMessage(self.tr("Operation aborted"), 10)
                break
            time.sleep(0.01)
        else:
            self._parent.setStatusbarMessage(self.tr("Position reached"), 10)
        dialog.hide()

    def _onFreeRadioButtonToggled(self, checked):
        """ Reference radio button has been toggled.
        """
        Logger().debug("GotoController._onReferenceRadioButtonToggled(): checked=%s" % checked)
        self._view.yawFovDoubleSpinBox.setEnabled(checked)
        self._view.pitchFovDoubleSpinBox.setEnabled(checked)

    # Interface
    def refreshView(self):
        pass
