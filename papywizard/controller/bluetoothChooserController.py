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
    def __init__(self, parent, model):
        """ Init the object.

        @param parent: parent controller
        @type parent: {AbstractController}

        @param model: model to use
        @type model: {Shooting}
        """
        self.__parent = parent
        self.__model = model

        # Set the Glade file
        gladeFile = os.path.join(path, os.path.pardir, "view", "bluetoothChooserDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets()

        # Connect signal/slots
        self._signalDict = {"on_okButton_clicked": self.__onOkButtonClicked,
                            "on_cancelButton_clicked": self.__onCancelButtonClicked,
                            "on_refreshButton_clicked": self.__onRefreshButtonClicked
                        }

        # Associated TreeModel
        self.__bluetoothListStore = gtk.ListStore(gobject.TYPE_STRING)
        self.bluetoothAddressCombobox.set_model(self.__bluetoothListStore)

        # Fill widgets
        self.refreshView()

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.bluetoothAddressCombobox = self.wTree.get_widget("bluetoothAddressCombobox")

        # Nokia plateform stuff
        try:
            import hildon
            pass
        except ImportError:
            pass

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

    def __onRefreshButtonClicked(self):
        """ Refresh button has been clicked.

        Refresh bluetooth device list.
        """
        self.refreshView()

    def refreshView(self):
        #addresses = self.__model.getBluetoothAddresses()
        self.bluetoothAddressCombobox.clear()
        for i, ad in enumerate(('first', 'second')):
            self.__bluetoothListStore.append((ad, i))

    def getBluetoothAddress(self):
        return self.__bluetoothListStore.get_value((bluetoothAddressCombobox.get_active_iter(), 0))
        #return self.__model.xxx
