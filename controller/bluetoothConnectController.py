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

- BluetoothConnectController

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import gtk
import gobject

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.controller.abstractController import AbstractController


class BluetoothConnectController(AbstractController):
    """ Shoot controller object.
    """
    def __init__(self, parent, model, view):
        """ Init the object.

        @param parent: parent controller
        @type parent: {Controller}

        @param model: model to use
        @type mode: {Shooting}

        @param view: associated view
        @type view: {ConfigDialog}
        """
        self.__parent = parent
        self.__model = model
        self.__view = view

        # Connect signal/slots
        dic = {"on_rescanButton_clicked": self.__onRescanButtonClicked,
               "on_connectButton_clicked": self.__onConnectButtonClicked,
               "on_cancelButton_clicked": self.__onCancelButtonClicked
           }
        self.__view.wTree.signal_autoconnect(dic)

        # Fill widgets
        self.refreshView()

    def __onRescanButtonClicked(self, widget):
        """ Rescan button has been clicked.
        """
        Logger().trace("BluetoothConnectController.__onRescanButtonClicked()")
        self.refreshView()

    def __onConnectButtonClicked(self, widget):
        """ Connect button has been clicked.
        """
        Logger().trace("BluetoothConnectController.__onConnectButtonClicked()")
        self.__view.bluetoothConnectDialog.response(1)

    def __onCancelButtonClicked(self, widget):
        """ Cancel button has been clicked.
        """
        Logger().trace("BluetoothConnectController.__onConnectlButtonClicked()")
        self.__view.bluetoothConnectDialog.response(0)

    def refreshView(self):
        bluetoothDevices = self.__model.realHardware.driver.discoverDevices()
        Logger().debug("BluetoothConnectController.refreshView(): bluetoothDevices=%s" % bluetoothDevices)
        self.__view.fillWidgets(bluetoothDevices)