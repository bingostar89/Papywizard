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
        self._signalDict = {"on_clearButton_clicked": self.__onClearButtonClicked,
                            "on_saveButton_clicked": self.__onSaveButtonClicked,
                            "on_doneButton_clicked": self.__onDoneButtonClicked,
                        }

    def _initWidgets(self):
        pass

    def _connectSignals(self):
        pass

    def _disconnectSignals(self):
        pass

    # Callbacks
    def __onClearButtonClicked(self, widget):
        """ Clear button has been clicked.
        """
        Logger().trace("LoggerController.__onClearButtonClicked()")
        self._view.loggerPlainTextEdit.clear()
        self._view.clearButton.setEnable(False)
        self._view.saveButton.setEnable(False)

    def __onSaveButtonClicked(self, widget):
        """ Save button has been clicked.
        """
        Logger().trace("LoggerController.__onSaveButtonClicked()")
        dateTime = time.strftime("%Y-%m-%d_%Hh%Mm%Ss", time.localtime())
        logFileFormat = "papywizard_%s.log" % dateTime
        logFileName = os.path.join(ConfigManager().get('Preferences', 'DATA_STORAGE_DIR'), logFileFormat)
        buffer_ = self.loggerTextview.get_buffer()
        logText = buffer_.get_text(buffer_.get_start_iter(), buffer_.get_end_iter())
        logFile = file(logFileName, 'w')
        logFile.write(logText)
        logFile.close()
        Logger().debug("LoggerController.__onSaveButtonClicked(): log saved to '%s'" % logFileName)
        self._view.saveButton.setEnable(False)

    def __onDoneButtonClicked(self, widget):
        """ Done button has been clicked.
        """
        Logger().trace("LoggerController.__onDoneButtonClicked()")
        self.dialog.response(0)

    # Real work
    def refreshView(self):
        pass

    def setLogBuffer(self, buffer):
        """ Set the associated buffer.

        @param buffer: associated buffer
        @type buffer: gtk.TextBuffer
        """
        #self.loggerTextview.set_buffer(buffer)
