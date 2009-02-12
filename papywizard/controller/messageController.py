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

Message dialog controller

Implements
==========

- BaseMessageController
- InfoMessageController
- WarningMessageController
- ErrorDialogController
- ExceptionMessageController


@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger

_ = lambda a: a


class BaseMessageController(QtCore.QObject): # Inherits QMessageDialog
    """ Abstract message controller.
    """
    def __init__(self, subTitle, message):
        """ Init the base message controller.

        @param subTitle: dialog subTitle
        @type subTitle: str

        @param message: dialog message
        @type message: str
        """
        QtCore.QObject.__init__(self)
        self._dialog = QtGui.QMessageBox()
        self._init()
        self._dialog.setInformativeText(message)
        self._dialog.setText(subTitle)

    def _init(self):
        raise NotImplementedError

    def exec_(self):
        """ Run the dialog.

        @return: response
        @rtype: int
        """
        response = self._dialog.exec_()
        return response

    def shutdown(self):
        """ Dummy method for compatibility.
        """
        pass


class InfoMessageController(BaseMessageController):
    """ Info message controller.
    """
    def _init(self):
        self._dialog.setIcon(QtGui.QMessageBox.Information)
        self._dialog.setStandardButtons(QtGui.QMessageBox.Close)
        self._dialog.setWindowTitle(self.tr("Info"))


class WarningMessageController(BaseMessageController):
    """ Warning message controller.
    """
    def _init(self):
        self._dialog.setIcon(QtGui.QMessageBox.Warning)
        self._dialog.setStandardButtons(QtGui.QMessageBox.Close)
        self._dialog.setWindowTitle(self.tr("Warning"))


class ErrorMessageController(BaseMessageController):
    """ Error message controller.
    """
    def _init(self):
        self._dialog.setIcon(QtGui.QMessageBox.Critical)
        self._dialog.setStandardButtons(QtGui.QMessageBox.Close)
        self._dialog.setWindowTitle(self.tr("Error"))


class ExceptionMessageController(BaseMessageController):
    """ Exception message controller.
    """
    def _init(self):
        self._dialog.setIcon(QtGui.QMessageBox.Critical)
        self._dialog.setStandardButtons(QtGui.QMessageBox.Close)
        self._dialog.setWindowTitle(self.tr("Exception"))
        self._dialog.setDetailedText(Logger().getTraceback())


class YesNoMessageController(BaseMessageController):
    """ Yes/No question message controller.
    """
    def _init(self):
        self._dialog.setIcon(QtGui.QMessageBox.Question)
        self._dialog.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        self._dialog.setDefaultButton(QtGui.QMessageBox.Yes)
        self._dialog.setWindowTitle(self.tr("Question"))
