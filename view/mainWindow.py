# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

View.

Implements class:

- MainWindow

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import Tkinter as tk
import tkFont as tkF

from common.loggingServices import Logger


class MainWindow(tk.Tk):
    """ Main window.
    """
    FILE_QUIT_MENU_ENTRY = 0
    HARD_CONNECT_MENU_ENTRY = 0
    HARD_RESET_MENU_ENTRY = 2
    VIEW3D_SHOW_MENU_ENTRY = 0
    HELP_ABOUT_MENU_ENTRY = 0
    
    def __init__(self):
        """ Init the object.
        """
        tk.Tk.__init__(self)
        self.title("Papywizard")
        self._createMenus()
        self._createWidgets()

    def _createMenus(self):
        """ Add menus to main windows.
        """
        menuBar = tk.Menu(self)
        
        self.fileMenu = tk.Menu(menuBar, tearoff=0)
        self.fileMenu.add_command(label="Quit")
        menuBar.add_cascade(label="File", menu=self.fileMenu)

        self.hardMenu = tk.Menu(menuBar, tearoff=0)
        self.hardConnectVar = tk.IntVar(self)
        self.hardMenu.add_checkbutton(label="Connect", variable=self.hardConnectVar)
        self.hardMenu.add_separator()
        self.hardMenu.add_command(label="Reset", state=tk.DISABLED)
        menuBar.add_cascade(label="Hardware", menu=self.hardMenu)
        
        self.view3DMenu = tk.Menu(menuBar, tearoff=0)
        self.view3DShowVar = tk.IntVar(self)
        self.view3DShowVar.set(1)
        self.view3DMenu.add_checkbutton(label="Show", variable=self.view3DShowVar)
        menuBar.add_cascade(label="View 3D", menu=self.view3DMenu)

        self.helpMenu = tk.Menu(menuBar, tearoff=0)
        self.helpMenu.add_command(label="About")
        menuBar.add_cascade(label="Help", menu=self.helpMenu)

        self['menu'] = menuBar


    def _createWidgets(self):
        """ Populate main window.
        """
        font = tkF.Font(family="Helvetica", size=-14, weight=tkF.BOLD)
        tk.Label(self, text="Yaw", font=font, width=6).grid(row=0, column=1, sticky=tk.E)
        tk.Label(self, text="Pitch", font=font, width=6).grid(row=0, column=2, sticky=tk.E)
        
        tk.Label(self, text="Position (deg):").grid(row=1, column=0, sticky=tk.E)
        self.yawPosLabel = tk.Label(self)
        self.yawPosLabel.grid(row=1, column=1, sticky=tk.E)
        self.pitchPosLabel = tk.Label(self)
        self.pitchPosLabel.grid(row=1, column=2, sticky=tk.E)
        
        tk.Label(self, text="Start (deg):").grid(row=2, column=0, sticky=tk.E)
        self.yawStartLabel = tk.Label(self)
        self.yawStartLabel.grid(row=2, column=1, sticky=tk.E)
        self.pitchStartLabel = tk.Label(self)
        self.pitchStartLabel.grid(row=2, column=2, sticky=tk.E)
        self.setStartButton = tk.Button(self, text="Set")
        self.setStartButton.grid(row=2, column=3)
        
        tk.Label(self, text="End (deg):").grid(row=3, column=0, sticky=tk.E)
        self.yawEndLabel = tk.Label(self)
        self.yawEndLabel.grid(row=3, column=1, sticky=tk.E)
        self.pitchEndLabel = tk.Label(self)
        self.pitchEndLabel.grid(row=3, column=2, sticky=tk.E)
        self.setEndButton = tk.Button(self, text="Set")
        self.setEndButton.grid(row=3, column=3)
        
        tk.Label(self, text="total FoV (deg):").grid(row=4, column=0, sticky=tk.E)
        self.yawFovLabel = tk.Label(self)
        self.yawFovLabel.grid(row=4, column=1, sticky=tk.E)
        self.pitchFovLabel = tk.Label(self)
        self.pitchFovLabel.grid(row=4, column=2, sticky=tk.E)
        #self.setFovButton = tk.Button(self, text="Set")
        #self.setFovButton.grid(row=4, column=3)
        
        tk.Label(self, text="Nb Picts:").grid(row=5, column=0, sticky=tk.E)
        self.yawNbPictsLabel = tk.Label(self)
        self.yawNbPictsLabel.grid(row=5, column=1, sticky=tk.E)
        self.pitchNbPictsLabel = tk.Label(self)
        self.pitchNbPictsLabel.grid(row=5, column=2, sticky=tk.E)
        #self.setNbPictsButton = tk.Button(self, text="Set")
        #self.setNbPictsButton.grid(row=5, column=3)
        
        tk.Label(self, text="Real overlap (%):").grid(row=6, column=0)
        self.yawRealOverlapLabel = tk.Label(self)
        self.yawRealOverlapLabel.grid(row=6, column=1, sticky=tk.E)
        self.pitchRealOverlapLabel = tk.Label(self)
        self.pitchRealOverlapLabel.grid(row=6, column=2, sticky=tk.E)
        
        frame = tk.Frame(self)
        self.zenithVar = tk.IntVar(self)
        self.zenithVar.set(False)
        self.zenithCheckbutton = tk.Checkbutton(frame, text="Zenith", variable=self.zenithVar)
        self.zenithCheckbutton.pack(side=tk.LEFT)
        self.nadirVar = tk.IntVar(self)
        self.nadirVar.set(False)
        self.nadirCheckbutton = tk.Checkbutton(frame, text="Nadir", variable=self.nadirVar)
        self.nadirCheckbutton.pack(side=tk.RIGHT)
        frame.grid(row=7, column=0, columnspan=4)
        
        frame = tk.Frame(self)
        self.fullPanoButton = tk.Button(frame, text="360x180")
        self.fullPanoButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.manualMoveButton = tk.Button(frame, text="Manual move")
        self.manualMoveButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        frame.grid(row=8, column=0, columnspan=4, sticky=tk.W+tk.E)
        
        frame = tk.Frame(self)
        self.configButton = tk.Button(frame, text="Configuration")
        self.configButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.shootButton = tk.Button(frame, text="Shoot")
        self.shootButton.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        frame.grid(row=9, column=0, columnspan=4, sticky=tk.W+tk.E)
        
        self.resizable(False, False)

    def fillWidgets(self, values):
        """ Fill widgets with model values.
        
        @params values: model values
        @type values: dict
        """
        self.yawPosLabel.config(text="%.1f" % values['shooting']['yawPos'])
        self.pitchPosLabel.config(text="%.1f" % values['shooting']['pitchPos'])
        self.yawStartLabel.config(text="%.1f" % values['shooting']['yawStart'])
        self.pitchStartLabel.config(text="%.1f" % values['shooting']['pitchStart'])
        self.yawEndLabel.config(text="%.1f" % values['shooting']['yawEnd'])
        self.pitchEndLabel.config(text="%.1f" % values['shooting']['pitchEnd'])
        self.yawFovLabel.config(text="%.1f" % values['shooting']['yawFov'])
        self.pitchFovLabel.config(text="%.1f" % values['shooting']['pitchFov'])
        self.yawNbPictsLabel.config(text="%d" % values['shooting']['yawNbPicts'])
        self.pitchNbPictsLabel.config(text="%d" % values['shooting']['pitchNbPicts'])
        self.yawRealOverlapLabel.config(text=str(values['shooting']['yawRealOverlap']))
        self.pitchRealOverlapLabel.config(text=str(values['shooting']['pitchRealOverlap']))
        self.zenithVar.set(values['mosaic']['zenith'])
        self.nadirVar.set(values['mosaic']['nadir'])
