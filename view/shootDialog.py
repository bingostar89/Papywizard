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

- ShootDialog

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import os

#import pygtk
#pygtk.require("2.0")
import gtk.glade
import pango

path = os.path.dirname(__file__)


class ShootDialog(object):
    """ Shoot dialog.
    """
    def __init__(self):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "shootDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets()
        
        # Font test
        self.yawPosEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchPosEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawCoefEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchCoefEntry.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.sequenceEntry.modify_font(pango.FontDescription("Arial 10 Bold"))

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
        self.sequenceEntry = self.wTree.get_widget("sequenceEntry")
        self.progressbar = self.wTree.get_widget("progressbar")
        self.manualShootCheckbutton = self.wTree.get_widget("manualShootCheckbutton")
        self.dataFileEnableCheckbutton = self.wTree.get_widget("dataFileEnableCheckbutton")
        self.startButton = self.wTree.get_widget("startButton")
        self.suspendResumeButton = self.wTree.get_widget("suspendResumeButton")
        self.suspendResumeLabel = self.wTree.get_widget("suspendResumeLabel")
        self.stopButton = self.wTree.get_widget("stopButton")
        self.doneButton = self.wTree.get_widget("doneButton")

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.yawPosEntry.set_text("%.1f" % values['yawPos'])
        self.pitchPosEntry.set_text("%.1f" % values['pitchPos'])
        self.yawCoefEntry.set_text(values['yawIndex'])
        self.pitchCoefEntry.set_text(values['pitchIndex'])
        self.sequenceEntry.set_text(values['sequence'])
        self.progressbar.set_fraction(values['progress']['fraction'])
        self.progressbar.set_text(values['progress']['text'])
        try:
            self.dataFileEnableCheckbutton.set_active(values['dataFileEnable'])
        except KeyError:
            pass

