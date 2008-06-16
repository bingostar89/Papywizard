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

- MainWindow

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
import pango

path = os.path.dirname(__file__)


class MainWindow(object):
    """ Main window.
    """
    def __init__(self):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "mainWindow.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets()
        
        # Font test
        self.yawPosEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchPosEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawStartEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchStartEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawEndEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchEndEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawFovEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchFovEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawNbPictsEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchNbPictsEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawRealOverlapEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchRealOverlapEntry.modify_font(pango.FontDescription("Arial 10 Bold"))

        # Nokia plateform stuff
        try:
            import hildon

            self.app = hildon.Program()
            window = hildon.Window()
            window.set_title(self.mainWindow.get_title())
            self.window_in_fullscreen = False
            self.app.add_window(window)
            self.mainVbox.reparent(window)

            menu = gtk.Menu()
            for child in self.menubar.get_children():
                child.reparent(menu)
            window.set_menu(menu)

            self.menubar.destroy()
            self.mainWindow.destroy()
            window.show_all()
            self.menuBar = menu
            self.mainWindow = window

        except ImportError:
            pass

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.mainWindow = self.wTree.get_widget("mainWindow")
        self.mainVbox = self.wTree.get_widget("mainVbox")
        self.menubar = self.wTree.get_widget("menubar")
        self.hardwareConnectMenuitem = self.wTree.get_widget("hardwareConnectMenuitem")
        self.hardwareResetMenuitem = self.wTree.get_widget("hardwareResetMenuitem")
        self.view3DShowMenuitem = self.wTree.get_widget("view3DShowMenuitem")
        self.yawPosEntry = self.wTree.get_widget("yawPosEntry")
        self.pitchPosEntry = self.wTree.get_widget("pitchPosEntry")
        self.yawStartEntry = self.wTree.get_widget("yawStartEntry")
        self.pitchStartEntry = self.wTree.get_widget("pitchStartEntry")
        self.yawEndEntry = self.wTree.get_widget("yawEndEntry")
        self.pitchEndEntry = self.wTree.get_widget("pitchEndEntry")
        self.yawFovEntry = self.wTree.get_widget("yawFovEntry")
        self.pitchFovEntry = self.wTree.get_widget("pitchFovEntry")
        self.yawNbPictsEntry = self.wTree.get_widget("yawNbPictsEntry")
        self.pitchNbPictsEntry = self.wTree.get_widget("pitchNbPictsEntry")
        self.yawRealOverlapEntry = self.wTree.get_widget("yawRealOverlapEntry")
        self.pitchRealOverlapEntry = self.wTree.get_widget("pitchRealOverlapEntry")
        self.statusbar = self.wTree.get_widget("statusbar")
        self.generalContextId = self.statusbar.get_context_id("general")
        self.hardwareContextId = self.statusbar.get_context_id("hardware")
        self.connectImage = self.wTree.get_widget("connectImage")

    def fillWidgets(self, values):
        """ Fill widgets with model values.

        @params values: model values
        @type values: dict
        """
        self.yawPosEntry.set_text("%.1f" % values['yawPos'])
        self.pitchPosEntry.set_text("%.1f" % values['pitchPos'])
        self.yawStartEntry.set_text("%.1f" % values['yawStart'])
        self.pitchStartEntry.set_text("%.1f" % values['pitchStart'])
        self.yawEndEntry.set_text("%.1f" % values['yawEnd'])
        self.pitchEndEntry.set_text("%.1f" % values['pitchEnd'])
        self.yawFovEntry.set_text("%.1f" % values['yawFov'])
        self.pitchFovEntry.set_text("%.1f" % values['pitchFov'])
        self.yawNbPictsEntry.set_text("%d" % values['yawNbPicts'])
        self.pitchNbPictsEntry.set_text("%d" % values['pitchNbPicts'])
        self.yawRealOverlapEntry.set_text(str(values['yawRealOverlap']))
        self.pitchRealOverlapEntry.set_text(str(values['pitchRealOverlap']))
