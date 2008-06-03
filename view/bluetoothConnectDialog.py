# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- BluetoothConnectDialog

@author: Frederic Mantegazza
@copyright: 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import sys
import os.path

#import pygtk
#pygtk.require("2.0")
import gtk.glade

path = os.path.dirname(__file__)


class BluetoothConnectDialog(object):
    """ Main window.
    """
    def __init__(self):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "bluetoothConnectDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile) 
        
        # Retreive usefull widgets
        self._retreiveWidgets()
 
    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.bluetoothConnectDialog = self.wTree.get_widget("bluetoothConnectDialog")
        self.vbox = self.wTree.get_widget("vbox")
        self.connectbutton = self.wTree.get_widget("connectbutton")
        self.cancelbutton = self.wTree.get_widget("cancelbutton")

    def fillWidgets(self, bluetoothDevices):
        """ Fill widgets with model values.
        
        @params bluetoothDevices: bluetooth addresses of available devices
        @type bluetoothDevices: list of tuple
        """
        combobox = gtk.combo_box_new_text()
        self.vbox.pack_start(combobox)
        for name, address in bluetoothDevices:
            combobox.append_text("%s (%s)" % (name, address))
        