# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Controller.

Implements class:

- MainController

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time
import threading

import Tkinter as tk
import tkMessageBox as tkMB

from common import config
from common.loggingServices import Logger
from common.exception import HardwareError
from view.mainWindow import MainWindow
from view.configDialog import ConfigDialog
from view.manualMoveDialog import ManualMoveDialog
from view.shootDialog import ShootDialog
from abstractController import AbstractController
from configController import ConfigController
from manualMoveController import ManualMoveController
from shootController import ShootController
from spy import Spy


class MainController(AbstractController):
    """ Main controller object.
    """
    def __init__(self, serializer, model, view, view3D=None):
        """ Init the object.

        @param serializer: object used to serialize Tkinter events
        @type serializer: {Serializer]

        @param model: model to use
        @type model: {Shooting}

        @param view: associated view
        @type view: {MainWindow}
        """
        self.__serializer = serializer
        self.__model = model
        self.__view = view
        self.__view3D = view3D
        
        self.__yawPos = 0
        self.__pitchPos = 0

        # Bind events
        self.__view.fileMenu.entryconfig(MainWindow.FILE_QUIT_MENU_ENTRY, command=self.__quit)
        self.__view.hardMenu.entryconfig(MainWindow.HARD_CONNECT_MENU_ENTRY, command=self.__hardConnectMenu)
        self.__view.hardMenu.entryconfig(MainWindow.HARD_RESET_MENU_ENTRY, command=self.__hardResetMenu)
        self.__view.view3DMenu.entryconfig(MainWindow.VIEW3D_SHOW_MENU_ENTRY, command=self.__view3DShowMenu)
        self.__view.helpMenu.entryconfig(MainWindow.HELP_ABOUT_MENU_ENTRY, command=self.__helpAboutMenu)
        
        self.__view.setStartButton.config(command=self.__setStartButtonClicked)
        self.__view.setEndButton.config(command=self.__setEndButtonClicked)
        #self.__view.setFovButton.config(command=self.__setFovButtonClicked)
        #self.__view.setNbPictsButton.config(command= self.__setNbPictsButtonClicked)
        self.__view.fullPanoButton.config(command=self.__fullPanoButtonClicked)
        self.__view.manualMoveButton.config(command=self.__manualMoveButtonClicked)
        self.__view.zenithCheckbutton.bind("<ButtonRelease-1>", self.__zenithCheckbuttonClicked)
        self.__view.nadirCheckbutton.bind("<ButtonRelease-1>", self.__nadirCheckbuttonClicked)
        self.__view.configButton.config(command=self.__configButtonClicked)
        self.__view.shootButton.config(command=self.__shootButtonClicked)
        self.__view.protocol("WM_DELETE_WINDOW", self.__quit)
        
        #self.__keyPressedDict = {'Left': False,
                                 #'Right': False,
                                 #'Up': False,
                                 #'Down': False}
        #self.__view.bind_all("<KeyPress>", self.__keyPressed)
        #self.__view.bind_all("<KeyRelease>", self.__keyReleased)
        
        # Fill widgets
        self.refreshView()
        
        # Connect Spy
        Spy().newPosSignal.connect(self.__refreshPos)
        
        # Try to autoconnect to real hardware
        self.__connectToHardware()
        
        # Check if 3D view is available
        if view3D is None:
            self.__view.view3DShowVar.set(0)
            self.__view.view3DMenu.entryconfig(self.__view.VIEW3D_SHOW_MENU_ENTRY, state=tk.DISABLED)

    #def __keyPressed(self, event):
        #""" Key pressed callback.
        #"""
        #Logger().trace("MainController.__keyPressed()")
        #Logger().debug("MainController.__keyPressed(): key=%s" % event.keysym)
        #if self.__keyPressedDict.has_key(event.keysym):
            #if not self.__keyPressedDict[event.keysym]:
                #self.__keyPressedDict[event.keysym] = True
                #if event.keysym == "Left" and not self.__keyPressedDict["Right"]:
                    #Logger().debug("MainController.__keyPressed(): start 'yaw' axis dir '-'")
                    #self.__model.hardware.startAxis('yaw', '-')
                #elif event.keysym == "Right" and not self.__keyPressedDict["Left"]:
                    #Logger().debug("MainController.__keyPressed(): start 'yaw' axis dir '-'")
                    #self.__model.hardware.startAxis('yaw', '+')
                #elif event.keysym == "Up" and not self.__keyPressedDict["Down"]:
                    #Logger().debug("MainController.__keyPressed(): start 'pitch' axis dir '-'")
                    #self.__model.hardware.startAxis('pitch', '+')
                #elif event.keysym == "Down" and not self.__keyPressedDict["Up"]:
                    #Logger().debug("MainController.__keyPressed(): start 'pitch' axis dir '+'")
                    #self.__model.hardware.startAxis('pitch', '-')
        #else:
            #Logger().warning("MainController.__keyPressed(): unbind '%s' key" % event.keysym)

    #def __keyReleased(self, event):
        #""" Key released callback.
        #"""
        #Logger().trace("MainController.__keyReleased()")
        #Logger().debug("MainController.__keyReleased(): key=%s" % event.keysym)
        #if self.__keyPressedDict.has_key(event.keysym):
            #if self.__keyPressedDict[event.keysym]:
                #self.__keyPressedDict[event.keysym] = False
                #if event.keysym == "Left" or event.keysym == "Right":
                    #Logger().debug("MainController.__keyReleased(): stop 'yaw' axis")
                    #self.__model.hardware.stopAxis('yaw')
                #elif event.keysym == "Up" or event.keysym == "Down":
                    #Logger().debug("MainController.__keyReleased(): stop 'pitch' axis")
                    #self.__model.hardware.stopAxis('pitch')
            #else:
                #Logger().error("MainController.__keyReleased(): key '%s' released but never pressed!" % event.keysym)
        #else:
            #Logger().warning("MainController.__keyReleased(): unbind '%s' key" % event.keysym)
    
    def __connectToHardware(self):
        """ Connect to real hardware.
        """
        Logger().info("Connecting to real hardware...")
        try:
            self.__model.switchToRealHardware()
            Spy().setRefreshRate(config.SPY_SLOW_REFRESH)
            self.__view.hardMenu.entryconfig(MainWindow.HARD_RESET_MENU_ENTRY, state=tk.NORMAL)
            self.__view.hardConnectVar.set(1)
            tkMB.showinfo("Hardware connect", "Now connected to real hardware")
        except HardwareError: # Raised by model
            tkMB.showerror("Hardware connect", "Can't connect to hardware. Stay in simulation mode")
            self.__view.hardConnectVar.set(0)
    
    def __hardConnectMenu(self):
        """ Connect check button toggled.
        """
        Logger().trace("MainController.__hardConnectMenu()")
        if self.__view.hardConnectVar.get():
            self.__connectToHardware()
        else:
            Logger().info("Go to simulation mode")
            self.__model.switchToSimulatedHardware()
            Spy().setRefreshRate(config.SPY_FAST_REFRESH)
            self.__view.hardMenu.entryconfig(MainWindow.HARD_RESET_MENU_ENTRY, state=tk.DISABLED)
            tkMB.showinfo("Hardware connect", "Now in simulation mode")

    def __hardResetMenu(self):
        """ Hard reset menu selected.
        """
        Logger().trace("MainController.__hardResetMenu()")
        if self.__view.hardConnectVar.get():
            Logger().info("Reseting hardware")
            self.__model.hardware.reset()

    def __view3DShowMenu(self):
        """ Connect check button toggled.
        """
        Logger().trace("MainController.__view3DShowMenu()")
        if self.__view.view3DShowVar.get():
            if self.__view3D is not None:
                Logger().debug("MainController.__view3DShowMenu(): show 3D view")
                self.__view3D.visible = True
            else:
                tkMB.showerror("3D View", "Some libs are missing in order to use 3D view")
                self.__view.view3DShowVar.set(0)
        else:
            if self.__view3D is not None:
                Logger().debug("MainController.__view3DShowMenu(): hide 3D view")
                self.__view3D.visible=False
        
    def __helpAboutMenu(self):
        """ Connect check button toggled.
        """
        Logger().trace("MainController.__helpAboutMenu()")
        tkMB.showinfo("About Papywizard",
                      "Copyright Frédéric Mantegazza\nVersion %s\nReleased under CeCILL license\nThanks to Kolor team" % config.VERSION)

    def __setStartButtonClicked(self):
        Logger().trace("MainController.__setStartButtonClicked()")
        #if tkMB.askokcancel("Set start position", "Move the head to the start position and click 'OK'"):
        self.__model.storeStartPosition()
        self.refreshView()

    def __setEndButtonClicked(self):
        Logger().trace("MainController.__setEndButtonClicked()")
        #if tkMB.askokcancel("Set end position", "Move the head to the end position and click 'OK'"):
        self.__model.storeEndPosition()
        self.refreshView()

    def __setFovButtonClicked(self):
        Logger().trace("MainController.__setFovButtonClicked()")
        tkMB.showwarning("Set total field of view", "Not yet implemented")

    def __setNbPictsButtonClicked(self):
        tkMB.showwarning("Set total nb picts", "Not yet implemented")

    def __fullPanoButtonClicked(self):
        Logger().trace("MainController.__fullPanoButtonClicked()")

    def __manualMoveButtonClicked(self):
        Logger().trace("MainController.__manualMoveButtonClicked()")
        self.__view.protocol("WM_DELETE_WINDOW", self.__doNotCloseWindow)
        view = ManualMoveDialog(self.__view)
        controller = ManualMoveController(self, self.__serializer, self.__model, view)
        self.__view.protocol("WM_DELETE_WINDOW", self.__quit)

    def __zenithCheckbuttonClicked(self, event):
        Logger().trace("MainController.__zenithCheckbuttonClicked()")
        self.__model.mosaic.zenith = bool(self.__view.zenithVar.get())

    def __nadirCheckbuttonClicked(self, event):
        Logger().trace("MainController.__nadirCheckbuttonClicked()")
        self.__model.mosaic.nadir = bool(self.__view.nadirVar.get())

    def __configButtonClicked(self):
        Logger().trace("MainController.__configButtonClicked()")
        self.__view.protocol("WM_DELETE_WINDOW", self.__doNotCloseWindow)
        view = ConfigDialog(self.__view)
        controller = ConfigController(self, self.__model, view) # Open as modal
        self.refreshView()
        self.__view.protocol("WM_DELETE_WINDOW", self.__quit)

    def __shootButtonClicked(self):
        Logger().trace("MainController.__shootButtonClicked()")
        self.__view.protocol("WM_DELETE_WINDOW", self.__doNotCloseWindow)
        view = ShootDialog(self.__view)
        controller = ShootController(self, self.__serializer, self.__model, view)
        self.__view.protocol("WM_DELETE_WINDOW", self.__quit)
        
    def __quit(self):
        """ Quit main controller.
        """
        Logger().trace("MainController.__quit()")
        self.__model.shutdown()
        self.__view.destroy()

    def __doNotCloseWindow(self):
        """ Window can't be closed while shooting.
        """
        Logger().trace("MainController.__doNotCloseWindow()")

    def __refreshPos(self, yaw, pitch):
        """ Refresh position according to new pos.
        
        @param yaw: yaw axis value
        @type yaw: float
        
        @param pitch: pitch axix value
        @type pitch: float
        """
        self.__yawPos = yaw
        self.__pitchPos = pitch
        self.__serializer.apply(self.refreshView)

    def refreshView(self):
        values = {'shooting': {'yawPos': self.__yawPos,
                               'pitchPos': self.__pitchPos,
                               'yawStart': self.__model.yawStart,
                               'pitchStart': self.__model.pitchStart,
                               'yawEnd': self.__model.yawEnd,
                               'pitchEnd': self.__model.pitchEnd,
                               'yawFov': self.__model.yawFov,
                               'pitchFov':  self.__model.pitchFov,
                               'yawNbPicts':  self.__model.yawNbPicts,
                               'pitchNbPicts':  self.__model.pitchNbPicts,
                               'yawRealOverlap': int(round(100 * self.__model.yawRealOverlap)),
                               'pitchRealOverlap': int(round(100 * self.__model.pitchRealOverlap))
                               },
                  'mosaic': {'zenith': self.__model.mosaic.zenith,
                             'nadir':self.__model.mosaic.nadir}
                 }
        self.__view.fillWidgets(values)
