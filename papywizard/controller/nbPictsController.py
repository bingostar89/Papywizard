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

- NbPictsController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: shootController.py 333 2008-06-25 21:08:42Z fma $"

import pygtk
pygtk.require("2.0")
import gtk
import gobject

from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractController


class NbPictsController(AbstractController):
    """ Bluetooth chooser controller object.
    """
    def _init(self):
        self._gladeFile = "nbPictsDialog.glade"
        self._signalDict = {"on_okButton_clicked": self.__onOkButtonClicked,
                            "on_cancelButton_clicked": self.__onCancelButtonClicked,
                        }

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        super(NbPictsController, self)._retreiveWidgets()

        self.yawNbPictsSpinbutton = self.wTree.get_widget("yawNbPictsSpinbutton")
        self.pitchNbPictsSpinbutton = self.wTree.get_widget("pitchNbPictsSpinbutton")

    # Callbacks
    def __onOkButtonClicked(self, widget):
        """ Ok button has been clicked.
        """
        Logger().trace("NbPictsController.__onOkButtonClicked()")

    def __onCancelButtonClicked(self, widget):
        """ Cancel button has been clicked.
        """
        Logger().trace("NbPictsController.__onCancelButtonClicked()")

    def refreshView(self):
        pass

    # Real work
    def setMaxNbPicts(self, yawNbPicts, pitchNbPicts):
        """ Set the minium fov.
        
        @para yawNbPicts: yaw maximum nb pîcts
        @type yawNbPicts: int
        
        @param pitchNbPicts: pitch maximum nb pîcts
        @type pitchNbPicts: int
        """
        self.yawNbPictsSpinbutton.set_range(1, yawNbPicts)
        self.pitchNbPictsSpinbutton.set_range(1, pitchNbPicts)
    
    def setCurrentNbPicts(self, yawNbPicts, pitchNbPicts):
        """ Set the currentnb picts.
        
        @para yawNbPicts: yaw current nb pîcts
        @type yawNbPicts: int
        
        @param pitchNbPicts: pitch current nb pîcts
        @type pitchNbPicts: int
        """
        self.yawNbPictsSpinbutton.set_value(yawNbPicts)
        self.pitchNbPictsSpinbutton.set_value(pitchNbPicts)

    def getNbPicts(self):
        """ Return the yaw/pitch nb picts.
        
        @return: yaw/pitch nb picts
        @rtype: tuple
        """
        return self.yawNbPictsSpinbutton.get_value(), self.pitchNbPictsSpinbutton.get_value()
