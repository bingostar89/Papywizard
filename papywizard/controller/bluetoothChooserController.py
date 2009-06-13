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

- BluetoothChooserController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import time
import thread

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.common.bluetoothTransport import discoverDevices
from papywizard.controller.abstractController import AbstractModalDialogController
from papywizard.view.messageDialog import ExceptionMessageDialog


class BluetoothChooserController(AbstractModalDialogController):
    """ Bluetooth chooser controller object.
    """
    def _init(self):
        self._uiFile = "bluetoothChooserDialog.ui"

        self.__bluetoothDevices = []

        # Scan bluetooth devices
        try:
            self.__bluetoothDevices = discoverDevices()
        except Exception, msg:
            Logger().exception("refreshBluetoothList()")
            Logger().error("Can't scan bluetooth\n%s" % unicode(msg))
            dialog = ExceptionMessageDialog(self.tr("Can't scan bluetooth"), unicode(msg))
            dialog.exec_()

    def _initWidgets(self):
        pass

    #def _connectSignals(self):
        #AbstractModalDialogController._connectSignals(self)

    #def _disconnectSignals(self):
        #AbstractModalDialogController._disconnectSignals(self)

    # Interface
    def refreshView(self):
        self._view.bluetoothAddressComboBox.clear()
        for address, name in self.__bluetoothDevices:
            self._view.bluetoothAddressComboBox.addItem("%s -- %s" % (address, name))
        self._view.bluetoothAddressComboBox.setCurrentIndex(0)

    def getSelectedBluetoothAddress(self):
        return self._view.bluetoothAddressComboBox.currentText().split(" -- ")
