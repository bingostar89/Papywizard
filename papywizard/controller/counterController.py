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

Graphical toolkit controller

Implements
==========

 - CounterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractModalDialogController


class CounterController(AbstractModalDialogController):
    """ Counter controller object.
    """
    def _init(self):
        self._uiFile = "counterDialog.ui"

        self.__key = {'Return': QtCore.Qt.Key_Return,
                      'Escape': QtCore.Qt.Key_Escape
                      }

        self.__counter = self._model.shootingCounter

    def _initWidgets(self):

        # Let the dialog be managed as a window so it can
        # be displayed fullscreen on Nokia N8x0 devices
        self._view.setWindowFlags(QtCore.Qt.Window)

    def _connectSignals(self):
        AbstractModalDialogController._connectSignals(self)

        self.connect(self._view.increaseCounterToolButton, QtCore.SIGNAL("clicked()"), self.__onIncreaseCounterToolButtonClicked)
        self.connect(self._view.resetCounterToolButton, QtCore.SIGNAL("clicked()"), self.__onResetCounterToolButtonClicked)
        self.connect(self._view.decreaseCounterToolButton, QtCore.SIGNAL("clicked()"), self.__onDecreaseCounterToolButtonClicked)
        self.connect(self._view.triggerShutterToolButton, QtCore.SIGNAL("clicked()"), self.__onTriggerShutterToolButtonClicked)

        self._view._originalKeyPressEvent = self._view.keyPressEvent
        self._view.keyPressEvent = self.__onKeyPressed
        self._view._originalKeyReleaseEvent = self._view.keyReleaseEvent
        self._view.keyReleaseEvent = self.__onKeyReleased

    def _disconnectSignals(self):
        AbstractModalDialogController._disconnectSignals(self)

        self._view.keyPressEvent = self._view._originalKeyPressEvent
        self._view.keyReleaseEvent = self._view._originalKeyReleaseEvent

        self.disconnect(self._view.increaseCounterToolButton, QtCore.SIGNAL("clicked()"), self.__onIncreaseCounterToolButtonClicked)
        self.disconnect(self._view.resetCounterToolButton, QtCore.SIGNAL("clicked()"), self.__onResetCounterToolButtonClicked)
        self.disconnect(self._view.decreaseCounterToolButton, QtCore.SIGNAL("clicked()"), self.__onDecreaseCounterToolButtonClicked)
        self.disconnect(self._view.triggerShutterToolButton, QtCore.SIGNAL("clicked()"), self.__onTriggerShutterToolButtonClicked)

    def __onKeyPressed(self, event):
        Logger().debug("CounterController.__onKeyPressed(): key='%s" % event.key())

        # 'Return' key
        if event.key() == self.__key['Return']:
            Logger().debug("CounterController.__onKeyPressed(): 'Return' key pressed")
            self._view.accept()
            event.ignore()

        elif event.key() == self.__key['Escape']:
            Logger().debug("CounterController.__onKeyPressed(): 'Escape' key pressed")
            self._view.reject()
            event.ignore()

        else:
            event.accept()

    def __onKeyReleased(self, event):
        Logger().debug("CounterController.__onKeyReleased(): key='%s" % event.key())
        event.accept()

    # Callbacks
    def _onAccepted(self):
        Logger().trace("CounterController._onAccepted()")
        self._model.shootingCounter = self.__counter

    def __onIncreaseCounterToolButtonClicked(self):
        Logger().trace("CounterController.__onIncreaseCounterToolButtonClicked():")
        self.__counter += 1
        if self.__counter > 999:  # Put max value in config?
            self.__counter = 1
        self.refreshView()

    def __onResetCounterToolButtonClicked(self):
        Logger().trace("CounterController.__onResetCounterToolButtonClicked():")
        self.__counter = self._model.shootingCounter
        self.refreshView()

    def __onDecreaseCounterToolButtonClicked(self):
        Logger().trace("CounterController.__onDecreaseCounterToolButtonClicked():")
        self.__counter -= 1
        if self.__counter < 1:
            self.__counter = 1
        self.refreshView()

    def __onTriggerShutterToolButtonClicked(self):
        Logger().trace("CounterController.__onTriggerShutterToolButtonClicked():")
        Logger().info("Trigger shutter (manual)")
        time.sleep(5)
        retCode = self._model.shutter.shoot(-1)
        # @todo: check retcode?

    # Interface
    def refreshView(self):
        self._view.counterLcdNumber.display(self.__counter)
