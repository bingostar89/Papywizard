# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Controller.

Implements class:

- ManualMoveController

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import threading

import Tkinter as tk
import tkMessageBox as tkMB

from common.loggingServices import Logger
from abstractController import AbstractController
from spy import Spy


class ManualMoveController(AbstractController):
    """ Manual move controller object.
    """
    def __init__(self, parent, serializer, model, view):
        """ Init the object.

        @param parent: parent controller
        @type parent: {Controller}

        @param serializer: object used to serialize Tkinter events
        @type serializer: {Serializer]

        @param model: model to use
        @type mode: {Shooting}

        @param view: associated view
        @type view: {ManualMoveDialog}
        """
        self.__parent = parent
        self.__serializer = serializer
        self.__model = model
        self.__view = view
        
        # Bind events
        self.__view.setStartButton.config(command=self.__setStartButtonClicked)
        self.__view.setEndButton.config(command=self.__setEndButtonClicked)
        self.__view.yawMovePlusButton.bind('<ButtonPress-1>', self.__yawMovePlusButtonPressed)
        self.__view.yawMovePlusButton.bind('<ButtonRelease-1>', self.__yawMovePlusButtonReleased)
        self.__view.pitchMovePlusButton.bind('<ButtonPress-1>', self.__pitchMovePlusButtonPressed)
        self.__view.pitchMovePlusButton.bind('<ButtonRelease-1>', self.__pitchMovePlusButtonReleased)
        #self.__view.homeButton.config(command=self.__homeButtonClicked)
        self.__view.pitchMoveMinusButton.bind('<ButtonPress-1>', self.__pitchMoveMinusButtonPressed)
        self.__view.pitchMoveMinusButton.bind('<ButtonRelease-1>', self.__pitchMoveMinusButtonReleased)
        self.__view.yawMinusButton.bind('<ButtonPress-1>', self.__yawMoveMinusButtonPressed)
        self.__view.yawMinusButton.bind('<ButtonRelease-1>', self.__yawMoveMinusButtonReleased)
        #self.__view.doneButton.config(command=self.__doneButtonClicked)
        self.__view.protocol("WM_DELETE_WINDOW", self.__view.destroy)
        
        # Fill widgets
        self.refreshView()
        
        # Connect Spy
        Spy().newPosSignal.connect(self.__refreshPos)

        self.__view.wait_window(self.__view)

    def __setStartButtonClicked(self):
        Logger().trace("ConfigController.__setStartButtonClicked()")
        #if tkMB.askokcancel("Set start position", "Move the head to the start position and click 'OK'"):
        self.__model.storeStartPosition()
        self.__parent.refreshView()

    def __setEndButtonClicked(self):
        Logger().trace("ConfigController.__setEndButtonClicked()")
        #if tkMB.askokcancel("Set end position", "Move the head to the end position and click 'OK'"):
        self.__model.storeEndPosition()
        self.__parent.refreshView()

    def __yawMovePlusButtonPressed(self, event):
        """ Vert. move plus button pressed.
        
        Start vertical axis in plus direction.
        """
        Logger().trace("ManualMoveController.__yawMovePlusButtonPressed()")
        self.__model.hardware.startAxis('yaw', '+')

    def __yawMovePlusButtonReleased(self, event):
        """ Vert. move plus button released.
        """
        Logger().trace("ManualMoveController.__yawMovePlusButtonReleased()")
        self.__model.hardware.stopAxis('yaw')
        self.__model.hardware.waitStopAxis('yaw')
        self.refreshView()

    def __pitchMovePlusButtonPressed(self, event):
        """ Horiz. move plus button pressed.
        """
        Logger().trace("ManualMoveController.__pitchMovePlusButtonPressed()")
        self.__model.hardware.startAxis('pitch', '+')

    def __pitchMovePlusButtonReleased(self, event):
        """ Horiz. move plus button released.
        """
        Logger().trace("ManualMoveController.__pitchMovePlusButtonReleased()")
        self.__model.hardware.stopAxis('pitch')
        self.__model.hardware.waitStopAxis('pitch')
        self.refreshView()

    #def __homeButtonClicked(self):
        #""" Home button clicked.
        
        #Goto home position (0., 0.)
        #"""
        #Logger().trace("ManualMoveController.__homeButtonClicked()")
        #def checkEnd(self):
            #""" Check end of homing.
            
            #This method executes once, then registers itself in the TKinter
            #event handler to be execute again after a delay, and exits.
            #This way, GUI events can be handled while model is shooting.
            #"""
            #yaw, pitch = self.__model.hardware.readPosition()
            #Logger().debug("ManualMoveController.__homeButtonClicked.checkEnd(): yaw=%.1f, pitch=%.1f" % (yaw, pitch))
            #if abs(round(yaw, 2)) < 0.1 and abs(round(pitch, 2)) < 0.1:
                #Logger().debug("ManualMoveController.__homeButtonClicked.checkEnd(): home position reached")
                #self.__view.homeButton.config(text="Home", command=self.__homeButtonClicked)
                                                            
                #self.__view.protocol("WM_DELETE_WINDOW", self.__view.destroy)
                #self.refreshView()
                #return
            
            ##self.refreshView()
            #self.__view.after(200, checkEnd, self)
        
        #self.__model.hardware.gotoPosition(0, 0, wait=False)

        #self.__view.homeButton.config(text="Stop", command=self.__stopHome)
                                      
        #self.__view.protocol("WM_DELETE_WINDOW", self.__doNotCloseWindow)
            
        ## Check end of shooting
        #checkEnd(self)
        
    #def __stopHome(self):
        #""" Stop the goto home function.
        #"""
        #Logger().trace("ManualMoveController.__stopHome()")
        #self.__model.hardware.stopAxis('yaw')
        #self.__model.hardware.stopAxis('pitch')
        #self.__view.homeButton.config(text="Home", command=self.__homeButtonClicked)
        #self.__view.protocol("WM_DELETE_WINDOW", self.__view.destroy)
        #self.refreshView()

    #def __doNotCloseWindow(self):
        #""" Window can't be closed while homing.
        #"""
        #Logger().trace("ManualMoveController.__doNotCloseWindow()")
    
    def __pitchMoveMinusButtonPressed(self, event):
        """ Horiz. move minus button pressed.
        """
        Logger().trace("ManualMoveController.__pitchMoveMinusButtonPressed()")
        self.__model.hardware.startAxis('pitch', '-')

    def __pitchMoveMinusButtonReleased(self, event):
        """ Horiz. move minus button released.
        """
        Logger().trace("ManualMoveController.__pitchMoveMinusButtonReleased()")
        self.__model.hardware.stopAxis('pitch')
        self.__model.hardware.waitStopAxis('pitch')
        self.refreshView()

    def __yawMoveMinusButtonPressed(self, event):
        """ Vert. move minus button pressed.
        """
        Logger().trace("ManualMoveController.__yawMoveMinusButtonPressed()")
        self.__model.hardware.startAxis('yaw', '-')

    def __yawMoveMinusButtonReleased(self, event):
        """ Vert. move minus button released.
        """
        Logger().trace("ManualMoveController.__yawMoveMinusButtonReleased()")
        self.__model.hardware.stopAxis('yaw')
        self.__model.hardware.waitStopAxis('yaw')
        self.refreshView()
        
    def __doneButtonClicked(self):
        """ Done button has been clicked.
        """
        Logger().trace("ConfigController.__doneButtonClicked()")
        self.__view.destroy()

    def __refreshPos(self, yaw, pitch):
        """ Refresh position according to new pos.
        
        @param yaw: yaw axis value
        @type yaw: float
        
        @param pitch: pitch axis value
        @type pitch: float
        """
        Logger().trace("ManualMoveController.__refreshPos()")
        values = {'yawPos': yaw, 'pitchPos': pitch}
        self.__serializer.apply(self.__view.fillWidgets, values)

    def refreshView(self):
        yaw, pitch = self.__model.hardware.readPosition()
        values = {'yawPos': yaw, 'pitchPos': pitch}
        self.__view.fillWidgets(values)
