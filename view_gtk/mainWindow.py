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
 
    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.mainWindow = self.wTree.get_widget("mainWindow")
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
        self.zenithCheckbutton = self.wTree.get_widget("zenithCheckbutton")
        self.nadirCheckbutton = self.wTree.get_widget("nadirCheckbutton")

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
        self.zenithCheckbutton.set_active(values['mosaic']['zenith'])
        self.nadirCheckbutton.set_active(values['mosaic']['nadir'])
