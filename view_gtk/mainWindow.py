# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- MainWindow

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
        self.yawPosEntry.set_text("%.1f" % values['shooting']['yawPos'])
        self.pitchPosEntry.set_text("%.1f" % values['shooting']['pitchPos'])
        self.yawStartEntry.set_text("%.1f" % values['shooting']['yawStart'])
        self.pitchStartEntry.set_text("%.1f" % values['shooting']['pitchStart'])
        self.yawEndEntry.set_text("%.1f" % values['shooting']['yawEnd'])
        self.pitchEndEntry.set_text("%.1f" % values['shooting']['pitchEnd'])
        self.yawFovEntry.set_text("%.1f" % values['shooting']['yawFov'])
        self.pitchFovEntry.set_text("%.1f" % values['shooting']['pitchFov'])
        self.yawNbPictsEntry.set_text("%d" % values['shooting']['yawNbPicts'])
        self.pitchNbPictsEntry.set_text("%d" % values['shooting']['pitchNbPicts'])
        self.yawRealOverlapEntry.set_text(str(values['shooting']['yawRealOverlap']))
        self.pitchRealOverlapEntry.set_text(str(values['shooting']['pitchRealOverlap']))
