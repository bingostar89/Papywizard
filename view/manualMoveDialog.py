# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- ManualMoveDialog

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import sys

import Tkinter as tk
import tkFont as tkF

from common import config
from common.loggingServices import Logger


class ManualMoveDialog(tk.Toplevel):
    """ Manual move dialog.
    """
    def __init__(self, master):
        """ Init the object.
        """
        tk.Toplevel.__init__(self, master)
        self.title("Manual Move")
        self.__master = master
        self.transient(master)
        self._createWidgets()
        self.grab_set()

    def _createWidgets(self):
        """ Create the manual move dialog widgets.
        """
        font = tkF.Font(family="Helvetica", size=-14, weight=tkF.BOLD)
        frame = tk.Frame(self)
        tk.Label(frame, text="Yaw", font=font, width=8).grid(row=0, column=0, sticky=tk.E)
        tk.Label(frame, text="Pitch", font=font, width=8).grid(row=0, column=1, sticky=tk.E)
        self.yawPosLabel = tk.Label(frame, width=8)
        self.yawPosLabel.grid(row=1, column=0, sticky=tk.E)
        self.pitchPosLabel = tk.Label(frame, width=8)
        self.pitchPosLabel.grid(row=1, column=1, sticky=tk.E)
        frame.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E)

        self.setStartButton = tk.Button(self, height=2, width=4, text="Set\nStart")
        self.setStartButton.grid(row=2, column=0)
        self.pitchMovePlusButton = tk.Button(self, height=3, width=5, text="Pitch +")
        self.pitchMovePlusButton.grid(row=2, column=1)
        self.setEndButton = tk.Button(self, height=2, width=4, text="Set\nEnd")
        self.setEndButton.grid(row=2, column=2)
        self.yawMinusButton = tk.Button(self, height=3, width=5, text="Yaw -")
        self.yawMinusButton.grid(row=3, column=0)
        #self.homeButton = tk.Button(self, height=3, width=5, text="Home")
        #self.homeButton.grid(row=3, column=1)
        self.yawMovePlusButton = tk.Button(self, height=3, width=5, text="Yaw +")
        self.yawMovePlusButton.grid(row=3, column=2)
        self.pitchMoveMinusButton = tk.Button(self, height=3, width=5, text="Pitch -")
        self.pitchMoveMinusButton.grid(row=4, column=1)

        #frame = tk.Frame(self)
        #self.doneButton = tk.Button(frame, text="Done")
        #self.doneButton.pack(side=tk.RIGHT)
        #frame.grid(row=5, column=0, columnspan=3, sticky=tk.W+tk.E)
        
        self.resizable(False, False)

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.yawPosLabel.config(text="%.1f" % values['yawPos'])
        self.pitchPosLabel.config(text="%.1f" % values['pitchPos'])
