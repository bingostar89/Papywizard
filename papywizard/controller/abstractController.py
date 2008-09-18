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

- AbstractController

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import os.path

import pygtk
pygtk.require("2.0")
import gtk.glade

path = os.path.dirname(__file__)


class AbstractController(object):
    """ Base class for controllers.
    """
    def __init__(self, parent=None, model=None):
        """ Init the controller.

        @param parent: parent controller
        @type parent: {Controller}

        @param model: model to use
        @type model: {Shooting}
        """
        self._parent = parent
        self._model = model

        self._init()

        # Set the Glade file
        gladeFile = os.path.join(path, os.path.pardir, "view", self._gladeFile)
        self.wTree = gtk.glade.XML(gladeFile)

        self._retreiveWidgets()
        self._connectSignals()
        self.refreshView()

    def _init(self):
        """ Misc. init.
        """
        self._gladeFile = None
        self._signalDict = None
        
    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.dialog = self.wTree.get_widget("dialog")
        if self.dialog is None:
            raise ValueError("can't retreive main dialog widget")

    def _connectSignals(self):
        """ Connect widgets signals.
        """
        self.wTree.signal_autoconnect(self._signalDict)

    def run(self):
        """ Run the dialog.
        """
        return self.dialog.run()
        
    def destroyView(self):
        """ Destroy the view.
        """
        self.dialog.destroy()
    
    def refreshView(self):
        """ Refresh the view widgets according to model values.
        """
        raise NotImplementedError
