# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Controller.

Implements class:

- ShootController

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
from abstractController import AbstractController
from spy import Spy


class ShootController(AbstractController):
    """ Shoot controller object.
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
        @type view: {ConfigDialog}
        """
        self.__parent = parent
        self.__serializer = serializer
        self.__model = model
        self.__view = view
        
        # Bind events
        self.__view.startSuspendResumeButton.config(command=self.__startButtonClicked)
        self.__view.stopButton.config(command=self.__stopButtonClicked)
        self.__view.protocol("WM_DELETE_WINDOW", self.__view.destroy)
        
        # Fill widgets
        self.refreshView()
        
        # Connect Spy
        Spy().newPosSignal.connect(self.__refreshPos)
        
        self.__view.wait_window(self.__view)

    def __startButtonClicked(self):
        """ Start button has been clicked.
        
        The model's start() method is called in a thread
        """
        Logger().trace("ShootController.__startButtonClicked()")
        def checkEnd(self, thread):
            """ Check end of shooting.
            
            This method executes once, then registers itself in the TKinter
            event handler to be execute again after a delay, and exits.
            This way, GUI events can be handled while model is shooting.
            """
            if not self.__model.isShooting():
                self.__view.startSuspendResumeButton.config(text="Start", background="green",activebackground="green",
                                                            command=self.__startButtonClicked)
                self.__view.stopButton.config(background="darkred", activebackground="darkred", state=tk.DISABLED)
                self.__view.protocol("WM_DELETE_WINDOW", self.__view.destroy)
                self.refreshView()
                thread.join()
                return
            
            self.refreshView() # Can conflict with Spy?
            self.__view.after(200, checkEnd, self, thread)
        
        thread = threading.Thread(target=self.__model.start)
        thread.start()

        self.__view.startSuspendResumeButton.config(text="Suspend", background="yellow", activebackground="yellow",
                                                    command=self.__suspendButtonClicked)
        self.__view.stopButton.config(background="red", activebackground="red", state=tk.NORMAL)
        self.__view.protocol("WM_DELETE_WINDOW", self.__doNotCloseWindow)
        
        # Wait for shooting really starts
        # Use condition
        time.sleep(0.1)
            
        # Check end of shooting
        checkEnd(self, thread)
        
    def __suspendButtonClicked(self):
        """ Suspend button has been clicked.
        """
        Logger().trace("ShootController.__suspendButtonClicked()")
        self.__model.suspend()
        self.__view.startSuspendResumeButton.config(text="Resume", background="green", activebackground="green",
                                                    command=self.__resumeButtonClicked)
        
    def __resumeButtonClicked(self):
        """ Resume button has been clicked.
        """
        Logger().trace("ShootController.__resumeButtonClicked()")
        self.__model.resume()
        self.__view.startSuspendResumeButton.config(text="Suspend", background="yellow", activebackground="yellow",
                                                    command=self.__suspendButtonClicked)
        
    def __stopButtonClicked(self):
        """ Stop button has been clicked.
        """
        Logger().trace("ShootController.__stopButtonClicked()")
        self.__model.stop()
        
        # Wait for shooting really stops
        # todo: use condition
        while self.__model.isShooting():
            time.sleep(0.1)

    def __doNotCloseWindow(self):
        """ Window can't be closed while shooting.
        """
        Logger().trace("ShootController.__doNotCloseWindow()")

    def __refreshPos(self, yaw, pitch):
        """ Refresh position according to new pos.
        
        @param yaw: yaw axis value
        @type yaw: float
        
        @param pitch: pitch axix value
        @type pitch: float
        """
        Logger().trace("ShootController.__refreshPos()")
        
        # Hugly design!
        values = self.__model.getState()
        values.update({'yawPos': yaw, 'pitchPos': pitch})
        self.__serializer.apply(self.__view.fillWidgets, values)
    
    def refreshView(self):
        values = self.__model.getState()
        self.__view.fillWidgets(values)
        