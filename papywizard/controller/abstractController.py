# -*- coding: utf-8 -*-

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

- AbstractController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path

import pygtk
pygtk.require("2.0")
import gtk.glade

from papywizard.common.loggingServices import Logger

if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "common")
else:
    path = os.path.dirname(__file__)


class AbstractController(object):
    """ Base class for controllers.
    """
    def __init__(self, parent=None, model=None, serializer=None):
        """ Init the controller.

        @param parent: parent controller
        @type parent: {Controller}

        @param model: model to use
        @type model: {Shooting}

        @param serializer: serializer for multi-threading operations
        @type serializer: {Serializer}
        """
        self._parent = parent
        self._model = model
        self._serializer = serializer

        self._init()

        # Set the Glade file
        gladeFile = os.path.join(path, os.path.pardir, "view", self._gladeFile)
        self.wTree = gtk.glade.XML(gladeFile)

        self._retreiveWidgets()
        self._initWidgets()
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
            raise ValueError("Can't retreive main dialog widget")

    def _initWidgets(self):
        """ Init widgets.
        """
        raise NotImplementedError

    def _connectSignals(self):
        """ Connect widgets signals.
        """
        self.wTree.signal_autoconnect(self._signalDict)
        self.dialog.connect("delete-event", self._onDelete)

    def _disconnectSignals(self):
        """ Disconnect widgets signals.
        """
        pass

    def _setFontParams(self, widget, scale=None, weight=None):
        """ Change the widget font size.

         @param widget: widget to change the font
         @type widget: {gtk.Widget}

         @param scale: scale for the new font size
         @type scale: int

         @param weight: new weight
         @type weight: PangoWeight enum
        """
        context = widget.get_pango_context()
        font = context.get_font_description()
        if scale is not None:
            font.set_size(int(font.get_size() * scale))
        if weight is not None:
            font.set_weight(weight)
        widget.modify_font(font)

    # Cllbacks GTK
    def _onDelete(self, widget, event):
        """ 'delete-event' signal callback.
        """
        Logger().trace("AbstractController._onDelete()")

    # Interface
    def run(self):
        """ Run the dialog.
        """
        return self.dialog.run()

    def shutdown(self):
        """ Shutdown the controller.

        mainly destroy the view.
        """
        self.dialog.destroy()
        self._disconnectSignals()

    def refreshView(self):
        """ Refresh the view widgets according to model values.
        """
        raise NotImplementedError
