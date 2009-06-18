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

Graphical toolkit controller

Implements
==========

- ConnectController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: ConnectController.py 1914 2009-06-13 17:50:11Z fma $"

import sys
import time
import threading

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractModalDialogController


class ConnectController(AbstractModalDialogController):
    """ Connect controller object.
    """
    def _init(self):
        self._uiFile = "connectDialog.ui"

        if sys.platform == 'darwin':
            self.__pluginsConnector = self._model
        else:
            self.__pluginsConnector = PluginsConnectorThread(self._model)

    def _initWidgets(self):
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def _connectSignals(self):
        AbstractModalDialogController._connectSignals(self)

        self.connect(self._model, QtCore.SIGNAL("currentStep"), self.__onCurrentStep, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("stepStatus"), self.__onStepStatus, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self.__pluginsConnector, QtCore.SIGNAL("finished()"), self.__onFinished, QtCore.Qt.BlockingQueuedConnection)

    def _disconnectSignals(self):
        AbstractModalDialogController._disconnectSignals(self)

        self.disconnect(self._model, QtCore.SIGNAL("currentStep"), self.__onCurrentStep)
        self.disconnect(self._model, QtCore.SIGNAL("stepStatus"), self.__onStepStatus)
        self.disconnect(self.__pluginsConnector, QtCore.SIGNAL("finished()"), self.__onFinished)

    def _startModel(self):
        self.__pluginsConnector.start()

    # Callbacks Qt
    def _onCloseEvent(self, event):
        Logger().trace("ConnectController._onCloseEvent()")
        if self._view.buttonBox.isEnabled():
            event.accept()
        else:
            event.ignore()

    def _onAccepted(self):
        Logger().trace("ConnectController._onAccepted()")

    def _onRejected(self):
        Logger().trace("ConnectController._onRejected()")

    def __onCurrentStep(self, step):
        """ A new current step is available.

        @param step: new current step
        @type step: str
        """
        Logger().debug("ConnectController.__onCurrentStep(): step=%s" % step)
        self._view.pluginsStatusTextEdit.insertHtml(step)

    def __onStepStatus(self, status):
        """ Set the status of the current step.

        @param status: step status, in ('Ok', 'Failed')
        @type status: str
        """
        Logger().debug("ConnectController.__onStepStatus(): status=%s" % status)
        if status == 'Ok':
            self._view.pluginsStatusTextEdit.insertHtml("&nbsp;&nbsp;<span style='color:#005500;'>[%s]</span><br />" % status)
        else:
            self._view.pluginsStatusTextEdit.insertHtml("&nbsp;&nbsp;<span style='color:#550000;'>[%s]</span><br />" % status)

    def __onFinished(self):
        """ Pb: not called!
        """
        Logger().trace("ConnectController.__onFinished()")
        self._view.buttonBox.setEnabled(True)
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        # Check connection status
        # If all is Ok, automatically close the dialog
        pluginsStatus = self._model.getPluginsStatus()
        if pluginsStatus['yawAxis']['init'] and \
           pluginsStatus['pitchAxis']['init'] and \
           pluginsStatus['shutter']['init']:
            time.sleep(1)
            self._view.accept()

    # Interface
    def refreshView(self):
        pass


class PluginsConnectorThread(QtCore.QThread):
    """ Special thread starting connector.
    """
    def __init__(self, connector):
        """ Init the connector thread.
        """
        QtCore.QThread.__init__(self)
        self.__pluginsConnector = connector

    def run(self):
        threading.currentThread().setName("Connector")
        self.__pluginsConnector.start()
