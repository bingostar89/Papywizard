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

- AbstractController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path

import PyQt4.uic
from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger

if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "common")
else:
    path = os.path.dirname(__file__)


class AbstractController(object):
    """ Base class for controllers.
    """
    def __init__(self, parent=None, model=None, serializer=None):
        """ Init the controller.

        @param parent: parent controller
        @type parent: {Controller}

        @param model: model to use
        @type model: {Shooting}

        @param serializer: serializer for multi-threading operations
        @type serializer: {Serializer}
        """
        self._parent = parent
        self._model = model
        self._serializer = serializer

        self._init()

        # Build the GUI from ui file
        uiFile = os.path.join(path, os.path.pardir, "view", self._uiFile)
        self._view = PyQt4.uic.loadUi(uiFile)

        self._initWidgets()
        self._connectQtSignals()
        self._connectSignals()
        self.refreshView()

    def _init(self):
        """ Misc. init.
        """
        self._uiFile = None

    def _initWidgets(self):
        """ Init widgets.
        """
        raise NotImplementedError

    def _connectQtSignals(self):
        """ Connect widgets signals.
        """
        QtCore.QObject.connect(self._view, QtCore.SIGNAL("destroyed(QObject *)"), self._onDestroyed)
        # todo: connect the window close button signal

    def _connectSignals(self):
        """ Connect widgets signals.
        """
        raise NotImplementedError

    def _disconnectSignals(self):
        """ Disconnect widgets signals.
        """
        raise NotImplementedError

    # Callbacks Qt
    def _onDestroyed(self, widget):
        """ 'destroyed' signal callback.
        """
        Logger().trace("AbstractController._onDestroyed()")

    def shutdown(self):
        """ Shutdown the controller.

        mainly destroy the view.
        """
        self._disconnectSignals()
        del self._view # ???!!???

    def refreshView(self):
        """ Refresh the view widgets according to model values.
        """
        raise NotImplementedError


class AbstractModalDialogController(AbstractController):

    # Interface
    def exec_(self):
        """ Run the dialog.
        """
        return self._view.exec_()
