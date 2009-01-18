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

- LoggerController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import os.path
import time

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.controller.abstractController import AbstractModalDialogController


class LoggerController(AbstractModalDialogController):
    """ Logger controller object.
    """
    def _init(self):
        self._uiFile = "loggerDialog.ui"

    def _initWidgets(self):
        pass

    def _connectQtSignals(self):
        super(LoggerController, self)._connectQtSignals()
        QtCore.QObject.connect(self._view.clearLogPushButton, QtCore.SIGNAL("clicked()"), self.__onClearLogPushButtonClicked)
        QtCore.QObject.connect(self._view.saveLogPushButton, QtCore.SIGNAL("clicked()"), self.__onSaveLogPushButtonClicked)

    def _connectSignals(self):
        pass

    def _disconnectSignals(self):
        pass

    # Callbacks
    def __onClearLogPushButtonClicked(self):
        """ Clear button has been clicked.
        """
        Logger().trace("LoggerController.__onClearLogPushButtonClicked()")
        self._view.loggerPlainTextEdit.clear()
        self._view.clearLogPushButton.setEnabled(False)
        self._view.saveLogPushButton.setEnabled(False)

    def __onSaveLogPushButtonClicked(self):
        """ Save button has been clicked.
        """
        Logger().trace("LoggerController.__onSaveLogPushButtonClicked()")
        dateTime = time.strftime("%Y-%m-%d_%Hh%Mm%Ss", time.localtime())
        logFileFormat = "papywizard_%s.log" % dateTime
        logFileName = os.path.join(ConfigManager().get('Preferences', 'DATA_STORAGE_DIR'), logFileFormat)
        logText = self._view.loggerPlainTextEdit.toPlainText()
        logFile = file(logFileName, 'w')
        logFile.write(logText)
        logFile.close()
        Logger().debug("LoggerController.__onSaveLogPushButtonClicked(): log saved to '%s'" % logFileName)
        self._view.saveLogPushButton.setEnabled(False)

    # Interface
    def refreshView(self):
        
        # Scroll to the bottom left of the window
        self._view.loggerPlainTextEdit.moveCursor(QtGui.QTextCursor.End)
        self._view.loggerPlainTextEdit.moveCursor(QtGui.QTextCursor.StartOfLine)

    def appendPlainText(self, text):
        """ Set the text.

        @param text: text to display
        @type text: str
        """
        self._view.loggerPlainTextEdit.appendPlainText(text)
        self.refreshView()

    def appendHtml(self, html):
        """ Set the text as html.

        @param html: text to display
        @type html: str
        """
        self._view.loggerPlainTextEdit.appendHtml(html)
        self.refreshView()
