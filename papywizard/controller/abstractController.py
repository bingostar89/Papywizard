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

- AbstractController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import types
import os.path

import PyQt4.uic
from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger

if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "controller")
else:
    path = os.path.dirname(__file__)


class AbstractController(QtCore.QObject):
    """ Base class for controllers.
    """
    def __init__(self, parent=None, model=None):
        """ Init the controller.

        @param parent: parent controller
        @type parent: {Controller}

        @param model: model to use
        @type model: {Shooting}
        """
        QtCore.QObject.__init__(self)
        self._parent = parent # Pass parent to __init__()?
        self._model = model

        self._uiFile = None
        self._init()

        # Build the GUI from ui file
        uiFile = os.path.join(path, os.path.pardir, "view", "ui", self._uiFile)
        self._view = PyQt4.uic.loadUi(uiFile)

        self._initWidgets()
        self._connectSignals()
        self._lateInit()
        self.refreshView()

    def _init(self):
        """ Misc. init.
        """
        raise NotImplementedError("AbstractController._init() must be overloaded")

    def _initWidgets(self):
        """ Init widgets.
        """
        raise NotImplementedError("AbstractController._initWidgets() must be overloaded")

    def _connectSignals(self):
        """ Connect widgets signals.
        """
        self._view._originalCloseEvent = self._view.closeEvent
        self._view.closeEvent = self._onCloseEvent

    def _disconnectSignals(self):
        """ Disconnect widgets signals.
        """
        self._view.closeEvent = self._view._originalCloseEvent

    def _lateInit(self):
        """ Late init.

        Can be used to init things *after* the GUI is setup.

        @todo: make abstract, and overload in sub-classes
        """
        #raise NotImplementedError("AbstractController._lateInit() must be overloaded")

    # Callbacks Qt
    def _onCloseEvent(self, event):
        """ close signal callback.
        """
        Logger().trace("AbstractController._onCloseEvent()")
        event.accept()

    # Interface
    def shutdown(self):
        """ Shutdown the controller.
        """
        self._disconnectSignals()
        #del self._view

    def refreshView(self):
        """ Refresh the view widgets according to model values.
        """
        raise NotImplementedError("AbstractController.refreshView() must be overloaded")


class AbstractModalDialogController(AbstractController):
    """
    """
    def _connectSignals(self):
        AbstractController._connectSignals(self)

        self.connect(self._view.buttonBox, QtCore.SIGNAL("accepted()"), self._onAccepted)
        self.connect(self._view.buttonBox, QtCore.SIGNAL("rejected()"), self._onRejected)

    def _disconnectSignals(self):
        AbstractController._disconnectSignals(self)

        self.disconnect(self._view.buttonBox, QtCore.SIGNAL("accepted()"), self._onAccepted)
        self.disconnect(self._view.buttonBox, QtCore.SIGNAL("rejected()"), self._onRejected)

    # Callbacks
    def _onAccepted(self):
        """ Ok button has been clicked.
        """
        Logger().trace("AbstractModalDialogController._onAccepted()")

    def _onRejected(self):
        """ Cancel button has been clicked.
        """
        Logger().trace("AbstractModalDialogController._onRejected()")

    # Interface
    def show(self):
        """ Show the dialog.
        """
        self._view.show()

    def exec_(self):
        """ Run the dialog.
        """
        return self._view.exec_()
