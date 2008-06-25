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

#from papywizard.view.lcdLabel import LCDLabel

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
        self.yawPosLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchPosLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawStartLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchStartLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawEndLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchEndLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawFovLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchFovLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawNbPictsLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchNbPictsLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawRealOverlapLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchRealOverlapLabel.modify_font(pango.FontDescription("Arial 10 Bold"))

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
        
        # Tests purpose
        #self.mainWindow.set_geometry_hints(min_width=800, min_height=480)

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.mainWindow = self.wTree.get_widget("mainWindow")
        self.mainVbox = self.wTree.get_widget("mainVbox")
        self.menubar = self.wTree.get_widget("menubar")
        self.hardwareConnectMenuitem = self.wTree.get_widget("hardwareConnectMenuitem")
        self.hardwareResetMenuitem = self.wTree.get_widget("hardwareResetMenuitem")
        self.view3DShowMenuitem = self.wTree.get_widget("view3DShowMenuitem")
        self.yawPosLabel = self.wTree.get_widget("yawPosLabel")
        self.pitchPosLabel = self.wTree.get_widget("pitchPosLabel")
        self.yawStartLabel = self.wTree.get_widget("yawStartLabel")
        self.pitchStartLabel = self.wTree.get_widget("pitchStartLabel")
        self.yawEndLabel = self.wTree.get_widget("yawEndLabel")
        self.pitchEndLabel = self.wTree.get_widget("pitchEndLabel")
        self.yawFovLabel = self.wTree.get_widget("yawFovLabel")
        self.pitchFovLabel = self.wTree.get_widget("pitchFovLabel")
        self.yawNbPictsLabel = self.wTree.get_widget("yawNbPictsLabel")
        self.pitchNbPictsLabel = self.wTree.get_widget("pitchNbPictsLabel")
        self.yawRealOverlapLabel = self.wTree.get_widget("yawRealOverlapLabel")
        self.pitchRealOverlapLabel = self.wTree.get_widget("pitchRealOverlapLabel")
        self.statusbar = self.wTree.get_widget("statusbar")
        self.statusbarContextId = self.statusbar.get_context_id("default")
        self.connectImage = self.wTree.get_widget("connectImage")

    def fillWidgets(self, values):
        """ Fill widgets with model values.

        @params values: model values
        @type values: dict
        """
        self.yawPosLabel.set_text("%.1f" % values['yawPos'])
        self.pitchPosLabel.set_text("%.1f" % values['pitchPos'])
        self.yawStartLabel.set_text("%.1f" % values['yawStart'])
        self.pitchStartLabel.set_text("%.1f" % values['pitchStart'])
        self.yawEndLabel.set_text("%.1f" % values['yawEnd'])
        self.pitchEndLabel.set_text("%.1f" % values['pitchEnd'])
        self.yawFovLabel.set_text("%.1f" % values['yawFov'])
        self.pitchFovLabel.set_text("%.1f" % values['pitchFov'])
        self.yawNbPictsLabel.set_text("%d" % values['yawNbPicts'])
        self.pitchNbPictsLabel.set_text("%d" % values['pitchNbPicts'])
        self.yawRealOverlapLabel.set_text(str(values['yawRealOverlap']))
        self.pitchRealOverlapLabel.set_text(str(values['pitchRealOverlap']))
