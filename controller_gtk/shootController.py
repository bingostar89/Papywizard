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

import gtk
import gobject

from common import config
from common.loggingServices import Logger
from controller.abstractController import AbstractController
from controller.spy import Spy


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

        # Connect signal/slots
        dic = {"on_startButton_clicked": self.__onStartButtonClicked,
               "on_stopButton_clicked": self.__onStopButtonClicked,
               "on_doneButton_clicked": self.__onDoneButtonClicked
           }
        self.__view.wTree.signal_autoconnect(dic)
        self.__suspendResumeHandler = self.__view.suspendResumeButton.connect('clicked', self.__onSuspendButtonClicked)
        
        # Fill widgets
        self.refreshView()
        
        # Connect Spy
        Spy().newPosSignal.connect(self.__refreshPos)

    def __onStartButtonClicked(self, widget):
        """ Start button has been clicked.
        
        The model's start() method is called in a thread
        """
        Logger().trace("ShootController.__startButtonClicked()")
        def checkEnd():
            """ Check end of shooting.
            
            This method executes once, then registers itself in the TKinter
            event handler to be execute again after a delay, and exits.
            This way, GUI events can be handled while model is shooting.
            """
            Logger().trace("checkEnd()")
            if not self.__model.isShooting():
                Logger().debug("checkEnd(): model not shooting anymore")
                self.__view.startButton.set_sensitive(True)
                self.__view.suspendResumeButton.set_label("Suspend")
                self.__view.suspendResumeButton.disconnect(self.__suspendResumeHandler)
                self.__suspendResumeHandler = self.__view.suspendResumeButton.connect('clicked', self.__onSuspendButtonClicked)
                self.__view.suspendResumeButton.set_sensitive(False)
                self.__view.stopButton.set_sensitive(False)
                self.__view.doneButton.set_sensitive(True)
                self.refreshView()
                thread.join()
                Logger().debug("checkEnd(): model thread over")
                return False # Stop execution by Gtk
            
            self.refreshView() # Can conflict with Spy?
            
            return True
        
        self.__view.startButton.set_sensitive(False)
        self.__view.suspendResumeButton.set_sensitive(True)
        self.__view.stopButton.set_sensitive(True)
        self.__view.doneButton.set_sensitive(False)

        thread = threading.Thread(target=self.__model.start)
        thread.start()
        
        # Wait for shooting really starts
        # Use condition
        time.sleep(0.1)
        
        # Check end of shooting
        gobject.timeout_add(200, checkEnd)
        #checkEnd()
        
    def __onSuspendButtonClicked(self, widget):
        """ Suspend button has been clicked.
        """
        Logger().trace("ShootController.__suspendButtonClicked()")
        self.__model.suspend()
        self.__view.suspendResumeButton.set_label("Resume")
        self.__view.suspendResumeButton.disconnect(self.__suspendResumeHandler)
        self.__suspendResumeHandler = self.__view.suspendResumeButton.connect('clicked', self.__onResumeButtonClicked)
        
    def __onResumeButtonClicked(self, widget):
        """ Resume button has been clicked.
        """
        Logger().trace("ShootController.__resumeButtonClicked()")
        self.__model.resume()
        self.__view.suspendResumeButton.set_label("Suspend")
        self.__view.suspendResumeButton.disconnect(self.__suspendResumeHandler)
        self.__suspendResumeHandler = self.__view.suspendResumeButton.connect('clicked', self.__onSuspendButtonClicked)
        
    def __onStopButtonClicked(self, widget):
        """ Stop button has been clicked.
        """
        Logger().trace("ShootController.__stopButtonClicked()")
        self.__model.stop()
        
        # Wait for shooting really stops
        # todo: use condition
        while self.__model.isShooting():
            time.sleep(0.1)
        
    def __onDoneButtonClicked(self, widget):
        """ Done button has been clicked.
        """
        Logger().trace("ShootController.__onDoneButtonClicked()")
        self.__view.manualMoveDialog.response(0)

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
        