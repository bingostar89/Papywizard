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

Graphical toolkit controller

Implements
==========

- ConnectController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
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

from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractController

path = os.path.dirname(__file__)


class ConnectController(AbstractController):
    """ Connect controller object.
    """
    def __init__(self, parent, model):
        """ Init the object.

        @param parent: parent controller
        @type parent: {AbstractController}

        @param model: model to use
        @type mode: {Shooting}
        """
        self.__parent = parent
        self.__model = model
        
        # Set the Glade file
        gladeFile = os.path.join(path, os.path.pardir, "view", "connectBanner.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets()

        # Connect signal/slots
        self.connectBanner.connect("delete-event", self.__onDelete)

        # Fill widgets
        self.refreshView()
        
        self.__eventId = gobject.timeout_add (100, self.__refreshProgressbar)

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.connectBanner = self.wTree.get_widget("connectBanner")
        self.progressbar = self.wTree.get_widget("progressbar")

        # Nokia plateform stuff
        try:
            import hildon
            pass
        except ImportError:
            pass

    # Callbacks
    def __onDelete(self, widget, event):
        Logger().trace("ConnectController.__onDelete()")
        return True

    def __refreshProgressbar(self):
        self.progressbar.pulse()
        return True

    def refreshView(self):
        pass
        
    def closeBanner(self):
        gobject.source_remove(self.__eventId)
        self.connectBanner.destroy()
