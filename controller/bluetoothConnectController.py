# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Controller.

Implements class:

- BluetoothConnectController

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
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