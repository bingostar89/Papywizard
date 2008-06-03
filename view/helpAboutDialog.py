# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- HelpAboutDialog

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


class HelpAboutDialog(object):
    """ Manual move dialog.
    """
    def __init__(self, master):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "helpAboutDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile) 
        
        # Retreive usefull widgets
        self._retreiveWidgets()
 
    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.helpAboutDialog = self.wTree.get_widget("helpAboutDialog")
