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

Message dialog dialog

Implements
==========

- BaseMessageDialog
- InfoMessageDialog
- WarningMessageDialog
- ErrorDialogController
- ExceptionMessageDialog


@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: messageController.py 1345 2009-01-18 15:52:55Z fma $"

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger

_ = lambda a: a


class BaseMessageDialog(QtGui.QMessageBox):
    """ Abstract message dialog.
    """
    def __init__(self, subTitle, message):
        """ Init the base message dialog.

        @param subTitle: dialog subTitle
        @type subTitle: str

        @param message: dialog message
        @type message: str
        """
        QtGui.QMessageBox.__init__(self)
        self._init()
        self.setInformativeText(message)
        self.setText(subTitle)

    def _init(self):
        raise NotImplementedError


class InfoMessageDialog(BaseMessageDialog):
    """ Info message dialog.
    """
    def _init(self):
        self.setIcon(QtGui.QMessageBox.Information)
        self.setStandardButtons(QtGui.QMessageBox.Close)
        self.setWindowTitle(_("Info"))


class WarningMessageDialog(BaseMessageDialog):
    """ Warning message dialog.
    """
    def _init(self):
        self.setIcon(QtGui.QMessageBox.Warning)
        self.setStandardButtons(QtGui.QMessageBox.Close)
        self.setWindowTitle(_("Warning"))


class ErrorMessageDialog(BaseMessageDialog):
    """ Error message dialog.
    """
    def _init(self):
        self.setIcon(QtGui.QMessageBox.Critical)
        self.setStandardButtons(QtGui.QMessageBox.Close)
        self.setWindowTitle(_("Error"))


class ExceptionMessageDialog(BaseMessageDialog):
    """ Exception message dialog.
    """
    def _init(self):
        self.setIcon(QtGui.QMessageBox.Critical)
        self.setStandardButtons(QtGui.QMessageBox.Close)
        self.setWindowTitle(_("Exception"))
        self.setDetailedText(Logger().getTraceback())


class YesNoMessageDialog(BaseMessageDialog):
    """ Yes/No question message dialog.
    """
    def _init(self):
        self.setIcon(QtGui.QMessageBox.Question)
        self.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        self.setDefaultButton(QtGui.QMessageBox.Yes)
        self.setWindowTitle(_("Question"))
