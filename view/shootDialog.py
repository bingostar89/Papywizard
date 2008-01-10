# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- ShootDialog

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


class ShootDialog(tk.Toplevel):
    """ Shoot dialog.
    """
    def __init__(self, master):
        """ Init the object.
        """
        tk.Toplevel.__init__(self, master)
        self.title("Shooting")
        self.__master = master
        self.transient(master)
        self._createWidgets()
        self.grab_set()

    def _createWidgets(self):
        """ Create the shoot dialog widgets.
        """
        font = tkF.Font(family="Helvetica", size=-14, weight=tkF.BOLD)

        tk.Label(self, text="Yaw", font=font, width=6).grid(row=0, column=1, sticky=tk.E)
        tk.Label(self, text="Pitch", font=font, width=6).grid(row=0, column=2, sticky=tk.E)
        
        tk.Label(self, text="Position (deg):").grid(row=1, column=0, sticky=tk.E)
        self.yawPosLabel = tk.Label(self)
        self.yawPosLabel.grid(row=1, column=1, sticky=tk.E)
        self.pitchPosLabel = tk.Label(self)
        self.pitchPosLabel.grid(row=1, column=2, sticky=tk.E)
        
        tk.Label(self, text="Mosaic:").grid(row=2, column=0, sticky=tk.E)
        self.yawCoefLabel = tk.Label(self)
        self.yawCoefLabel.grid(row=2, column=1, sticky=tk.E)
        self.pitchCoefLabel = tk.Label(self)
        self.pitchCoefLabel.grid(row=2, column=2, sticky=tk.E)

        #frame = tk.Frame(self)
        #tk.Label(frame, text="Yaw", font=font, width=8).grid(row=0, column=0, sticky=tk.E)
        #tk.Label(frame, text="Pitch", font=font, width=8).grid(row=0, column=1, sticky=tk.E)
        #self.yawCoefLabel = tk.Label(frame, width=8)
        #self.yawCoefLabel.grid(row=1, column=0, sticky=tk.E)
        #self.pitchCoefLabel = tk.Label(frame, width=8)
        #self.pitchCoefLabel.grid(row=1, column=1, sticky=tk.E)
        #frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E)
        
        frame = tk.Frame(self)
        tk.Label(frame, text="Progress").grid(row=0, column=0, sticky=tk.E)
        self.progressLabel = tk.Label(frame, width=15)
        self.progressLabel.grid(row=0, column=1, sticky=tk.W+tk.E)
        tk.Label(frame, text="Sequence").grid(row=1, column=0, sticky=tk.E)
        self.sequenceLabel = tk.Label(frame, width=15)
        self.sequenceLabel.grid(row=1, column=1, sticky=tk.E)
        frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E)
        
        frame = tk.Frame(self)
        self.startSuspendResumeButton = tk.Button(frame, text="Start", font=font, width=7,
                                                  background="green", activebackground="green",
                                                  disabledforeground="grey40")
        self.startSuspendResumeButton.grid(row=0, column=0, sticky=tk.W+tk.E)
        self.stopButton = tk.Button(frame, text="Stop", font=font, width=5,
                                    background="darkred", activebackground="darkred", disabledforeground="grey40",
                                    state=tk.DISABLED)
        self.stopButton.grid(row=0, column=1, sticky=tk.W+tk.E)
        frame.grid(row=4, column=0, columnspan=3, sticky=tk.W+tk.E)
        
        self.resizable(False, False)

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.yawPosLabel.config(text="%.1f" % values['yawPos'])
        self.pitchPosLabel.config(text="%.1f" % values['pitchPos'])
        self.yawCoefLabel.config(text=values['yawCoef'])
        self.pitchCoefLabel.config(text=values['pitchCoef'])
        self.progressLabel.config(text=values['progress'])
        self.sequenceLabel.config(text=values['sequence'])
