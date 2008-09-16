# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Fr�d�ric Mantegazza

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

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: shootController.py 333 2008-06-25 21:08:42Z fma $"

import time
import threading
import os.path

import bluetooth
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

#from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractController

path = os.path.dirname(__file__)


class BluetoothChooserController(AbstractController):
    """ Bluetooth chooser controller object.
    """
    def _init(self):
        self._gladeFile = "bluetoothChooserDialog.glade"
        self._signalDict = {"on_okButton_clicked": self.__onOkButtonClicked,
                            "on_cancelButton_clicked": self.__onCancelButtonClicked,
                            "on_refreshButton_clicked": self.__onRefreshButtonClicked
                        }

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        super(BluetoothChooserController, self)._retreiveWidgets()

        self.bluetoothAddressCombobox = self.wTree.get_widget("bluetoothAddressCombobox")
        self.__bluetoothListStore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.bluetoothAddressCombobox.set_model(self.__bluetoothListStore)
        cell = gtk.CellRendererText()
        self.bluetoothAddressCombobox.pack_start(cell, True)
        self.bluetoothAddressCombobox.add_attribute(cell, 'text', 0)
        cell = gtk.CellRendererText()
        self.bluetoothAddressCombobox.pack_start(cell, True)
        self.bluetoothAddressCombobox.add_attribute(cell, 'text', 1)

    # Callbacks
    def __onOkButtonClicked(self, widget):
        """ Ok button has been clicked.
        """
        Logger().trace("BluetoothChooserController.__onOkButtonClicked()")

    def __onCancelButtonClicked(self, widget):
        """ Cancel button has been clicked.

        Close the dialog.
        """
        Logger().trace("BluetoothChooserController.__onCancelButtonClicked()")

    def __onRefreshButtonClicked(self, widget):
        """ Refresh button has been clicked.

        Refresh bluetooth device list.
        """
        Logger().trace("BluetoothChooserController.__onRefreshButtonClicked()")
        self.refreshView()

    def refreshView(self):
        try:

            # Move to model
            devices = bluetooth.discover_devices(lookup_names=True)
            #devices = [('00:50:C2:58:56:6B', 'AIRserial4 55293'),
                       #('00:16:41:9E:5F:83', 'FODINGERPORT')]
            self.__bluetoothListStore.clear()
            for address, name in devices:
                self.__bluetoothListStore.append([address, name])
            self.bluetoothAddressCombobox.set_active(0)
        except:
            Logger().exception("BluetoothChooserController.__refreshView()")

    # Real work
    def getSelectedBluetoothAddress(self):
         selectedIter = self.bluetoothAddressCombobox.get_active_iter()
         return self.__bluetoothListStore.get(selectedIter, 0, 1)
