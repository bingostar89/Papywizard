# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- ConfigDialog

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


class ConfigDialog(tk.Toplevel):
    """ Preference dialog.
    """
    def __init__(self, master):
        """ Init the object.
        """
        tk.Toplevel.__init__(self, master)
        self.title("Configuration")
        self.__master = master
        self.transient(master)
        self._createWidgets()
        self.grab_set()

    def _createWidgets(self):
        """ Create the preferences widgets.
        """
        tk.Label(self, text="Tv (s)").grid(row=0, column=0, sticky=tk.E)
        self.timeValueVar = tk.DoubleVar(self)
        timeValueEntry = tk.Entry(self, textvariable=self.timeValueVar, width=5, justify=tk.RIGHT)
        timeValueEntry.grid(row=0, column=1)

        tk.Label(self, text="Nb picts").grid(row=1, column=0, sticky=tk.E)
        self.nbPictsVar = tk.IntVar(self)
        nbPictsEntry = tk.Entry(self, textvariable=self.nbPictsVar , width=5, justify=tk.RIGHT)
        nbPictsEntry.grid(row=1, column=1)

        tk.Label(self, text="Delay (s)").grid(row=2, column=0, sticky=tk.E)
        self.delayVar = tk.DoubleVar(self)
        delayEntry = tk.Entry(self, textvariable=self.delayVar, width=5, justify=tk.RIGHT)
        delayEntry.grid(row=2, column=1)

        tk.Label(self, text="Sensor ratio").grid(row=3, column=0, sticky=tk.E)
        self.sensorCoefVar = tk.DoubleVar(self)
        sensorCoefEntry = tk.Entry(self, textvariable=self.sensorCoefVar, width=5, justify=tk.RIGHT)
        sensorCoefEntry.grid(row=3, column=1)
        self.sensorRatioVar = tk.StringVar(self)
        sensorRatioOptionMenu = tk.OptionMenu(self, self.sensorRatioVar, *config.SENSOR_RATIOS.keys())
        sensorRatioOptionMenu.grid(row=3, column=2)

        tk.Label(self, text="Overlap (%)").grid(row=4, column=0, sticky=tk.E)
        self.overlapVar = tk.IntVar(self)
        overlapEntry = tk.Entry(self, textvariable=self.overlapVar, width=5, justify=tk.RIGHT)
        overlapEntry.grid(row=4, column=1)

        tk.Label(self, text="Focal (mm)").grid(row=5, column=0, sticky=tk.E)
        self.focalVar = tk.DoubleVar(self)
        focalEntry = tk.Entry(self, textvariable=self.focalVar, width=5, justify=tk.RIGHT)
        focalEntry.grid(row=5, column=1)
        self.fisheyeVar = tk.IntVar(self)
        fisheyeCheckButton = tk.Checkbutton(self, text="fisheye", variable=self.fisheyeVar)
        fisheyeCheckButton.grid(row=5, column=2)

        tk.Label(self, text="Camera orient.").grid(row=7, column=0, sticky=tk.E)
        self.cameraOrientationVar = tk.StringVar(self)
        cameraOrientationOptionMenu = tk.OptionMenu(self, self.cameraOrientationVar, 'landscape', 'portrait')
        cameraOrientationOptionMenu['width'] = 9
        cameraOrientationOptionMenu.grid(row=7, column=1, columnspan=2, sticky=tk.W)

        self.manualShootVar = tk.IntVar(self)
        manualShootCheckbutton = tk.Checkbutton(self, text="Manual shooting", variable=self.manualShootVar)
        manualShootCheckbutton.grid(row=8, column=0, columnspan=2, sticky=tk.W)

        frame = tk.Frame(self)
        self.okButton = tk.Button(frame, text="Ok")
        self.okButton.pack(side=tk.LEFT)
        self.cancelButton = tk.Button(frame, text="Cancel")
        self.cancelButton.pack(side=tk.LEFT)
        self.defaultButton = tk.Button(frame, text="Default")
        self.defaultButton.pack(side=tk.RIGHT)
        frame.grid(row=9, column=0, columnspan=4, sticky=tk.W+tk.E)
        
        self.resizable(False, False)

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.timeValueVar.set(values['camera']['timeValue'])
        self.nbPictsVar.set(values['camera']['nbPicts'])
        self.delayVar.set(values['shooting']['delay'])
        self.sensorCoefVar.set(values['camera']['sensorCoef'])
        self.sensorRatioVar.set(values['camera']['sensorRatio'])
        self.overlapVar.set(values['shooting']['overlap'])
        self.focalVar.set(values['lens']['focal'])
        self.fisheyeVar.set(values['lens']['fisheye'])
        self.cameraOrientationVar.set(values['shooting']['cameraOrientation'])
        self.manualShootVar.set(values['shooting']['manualShoot'])
