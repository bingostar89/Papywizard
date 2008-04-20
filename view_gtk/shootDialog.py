# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- ShootDialog

@author: Frederic Mantegazza
@copyright: 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import os

#import pygtk
#pygtk.require("2.0")
import gtk.glade

path = os.path.dirname(__file__)


class ShootDialog(object):
    """ Shoot dialog.
    """
    def __init__(self, master):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "shootDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile) 
        
        # Retreive usefull widgets
        self._retreiveWidgets()
        
        self.suspendResumeButton.set_state(gtk.STATE_INSENSITIVE)
        self.stopButton.set_state(gtk.STATE_INSENSITIVE)
 
    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.shootDialog = self.wTree.get_widget("shootDialog")
        self.yawPosEntry = self.wTree.get_widget("yawPosEntry")
        self.pitchPosEntry = self.wTree.get_widget("pitchPosEntry")
        self.yawCoefEntry = self.wTree.get_widget("yawCoefEntry")
        self.pitchCoefEntry = self.wTree.get_widget("pitchCoefEntry")
        self.progressEntry = self.wTree.get_widget("progressEntry")
        self.sequenceEntry = self.wTree.get_widget("sequenceEntry")
        self.startButton = self.wTree.get_widget("startButton")
        self.suspendResumeButton = self.wTree.get_widget("suspendResumeButton")
        self.stopButton = self.wTree.get_widget("stopButton")
        self.doneButton = self.wTree.get_widget("doneButton")

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.yawPosEntry.set_text("%.1f" % values['yawPos'])
        self.pitchPosEntry.set_text("%.1f" % values['pitchPos'])
        self.yawCoefEntry.set_text(str(values['yawCoef']))
        self.pitchCoefEntry.set_text(str(values['pitchCoef']))
        self.sequenceEntry.set_text(values['progress'])
        self.sequenceEntry.set_text(values['sequence'])
