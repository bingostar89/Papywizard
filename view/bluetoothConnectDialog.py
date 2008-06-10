# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Frédéric Mantegazza

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

View

Implements
==========

- BluetoothConnectDialog

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
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
        