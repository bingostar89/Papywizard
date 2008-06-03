# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- ManualMoveDialog

@author: Frederic Mantegazza
@copyright: 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import os
import sys

#import pygtk
#pygtk.require("2.0")
import gtk.glade

path = os.path.dirname(__file__)


class ManualMoveDialog(object):
    """ Manual move dialog.
    """
    def __init__(self):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "manualMoveDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets()

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.manualMoveDialog = self.wTree.get_widget("manualMoveDialog")
        self.yawPosEntry = self.wTree.get_widget("yawPosEntry")
        self.pitchPosEntry = self.wTree.get_widget("pitchPosEntry")
        self.setStartButton = self.wTree.get_widget("setStartButton")
        self.setEndButton = self.wTree.get_widget("setEndButton")
        self.yawMovePlusButton = self.wTree.get_widget("yawMovePlusButton")
        self.pitchMovePlusButton = self.wTree.get_widget("pitchMovePlusButton")
        self.pitchMoveMinusButton = self.wTree.get_widget("pitchMoveMinusButton")
        self.yawMinusButton = self.wTree.get_widget("yawMinusButton")
        self.doneButton = self.wTree.get_widget("doneButton")

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.yawPosEntry.set_text("%.1f" % values['yawPos'])
        self.pitchPosEntry.set_text("%.1f" % values['pitchPos'])
