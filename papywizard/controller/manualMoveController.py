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

Graphical toolkit controller

Implements
==========

- ManualMoveController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import gtk

from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.spy import Spy


class ManualMoveController(AbstractController):
    """ Manual move controller object.
    """
    def __init__(self, parent, serializer, model, view):
        """ Init the object.

        @param parent: parent controller
        @type parent: {Controller}

        @param serializer: object used to serialize Tkinter events
        @type serializer: {Serializer}

        @param model: model to use
        @type model: {Shooting}

        @param view: associated view
        @type view: {ManualMoveDialog}
        """
        self.__parent = parent
        self.__serializer = serializer
        self.__model = model
        self.__view = view

        # Connect signal/slots
        dic = {"on_setStartButton_clicked": self.__onSetStartButtonClicked,
               "on_setEndButton_clicked": self.__onSetEndButtonClicked,
               "on_yawMovePlusButton_pressed": self.__onYawMovePlusButtonPressed,
               "on_yawMovePlusButton_released": self.__onYawMovePlusButtonReleased,
               "on_pitchMovePlusButton_pressed": self.__onPitchMovePlusButtonPressed,
               "on_pitchMovePlusButton_released": self.__onPitchMovePlusButtonReleased,
               "on_yawMoveMinusButton_pressed": self.__onYawMoveMinusButtonPressed,
               "on_yawMoveMinusButton_released": self.__onYawMoveMinusButtonReleased,
               "on_hardwareSetOriginButton_clicked": self.onHardwareSetOriginButtonClicked,
               "on_pitchMoveMinusButton_pressed": self.__onPitchMoveMinusButtonPressed,
               "on_pitchMoveMinusButton_released": self.__onPitchMoveMinusButtonReleased,
               "on_doneButton_clicked": self.__onDoneButtonClicked
           }
        self.__view.wTree.signal_autoconnect(dic)

        # Fill widgets
        self.refreshView()

        # Connect Spy
        Spy().newPosSignal.connect(self.__refreshPos)

    def __onSetStartButtonClicked(self, widget):
        Logger().trace("ConfigController.__setStartButtonClicked()")
        #if tkMB.askokcancel("Set start position", "Move the head to the start position and click 'OK'"):
        self.__model.storeStartPosition()
        self.__parent.refreshView()

    def __onSetEndButtonClicked(self, widget):
        Logger().trace("ConfigController.__setEndButtonClicked()")
        #if tkMB.askokcancel("Set end position", "Move the head to the end position and click 'OK'"):
        self.__model.storeEndPosition()
        self.__parent.refreshView()

    def __onYawMovePlusButtonPressed(self, widget):
        """ Vert. move plus button pressed.

        Start vertical axis in plus direction.
        """
        Logger().trace("ManualMoveController.__yawMovePlusButtonPressed()")
        self.__model.hardware.startAxis('yaw', '+')

    def __onYawMovePlusButtonReleased(self, widget):
        """ Vert. move plus button released.
        """
        Logger().trace("ManualMoveController.__yawMovePlusButtonReleased()")
        self.__model.hardware.stopAxis('yaw')
        self.__model.hardware.waitStopAxis('yaw')
        self.refreshView()

    def __onPitchMovePlusButtonPressed(self, widget):
        """ Horiz. move plus button pressed.
        """
        Logger().trace("ManualMoveController.__pitchMovePlusButtonPressed()")
        self.__model.hardware.startAxis('pitch', '+')

    def __onPitchMovePlusButtonReleased(self, widget):
        """ Horiz. move plus button released.
        """
        Logger().trace("ManualMoveController.__pitchMovePlusButtonReleased()")
        self.__model.hardware.stopAxis('pitch')
        self.__model.hardware.waitStopAxis('pitch')
        self.refreshView()

    def onHardwareSetOriginButtonClicked(self, widget):
        Logger().trace("ManualMoveController.onHardwareSetOriginButtonClicked()")
        Logger().info("Set hardware origin")
        self.__model.hardware.setOrigin()
        self.__parent.setStatusbarMessage("Origin set to current position", 10)

    #def __onHomeButtonClicked(self):
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

    #def __onStopHome(self):
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

    def __onPitchMoveMinusButtonPressed(self, widget):
        """ Horiz. move minus button pressed.
        """
        Logger().trace("ManualMoveController.__onPitchMoveMinusButtonPressed()")
        self.__model.hardware.startAxis('pitch', '-')

    def __onPitchMoveMinusButtonReleased(self, widget):
        """ Horiz. move minus button released.
        """
        Logger().trace("ManualMoveController.__onPitchMoveMinusButtonReleased()")
        self.__model.hardware.stopAxis('pitch')
        self.__model.hardware.waitStopAxis('pitch')
        self.refreshView()

    def __onYawMoveMinusButtonPressed(self, widget):
        """ Vert. move minus button pressed.
        """
        Logger().trace("ManualMoveController.__onYawMoveMinusButtonPressed()")
        self.__model.hardware.startAxis('yaw', '-')

    def __onYawMoveMinusButtonReleased(self, widget):
        """ Vert. move minus button released.
        """
        Logger().trace("ManualMoveController.__onYawMoveMinusButtonReleased()")
        self.__model.hardware.stopAxis('yaw')
        self.__model.hardware.waitStopAxis('yaw')
        self.refreshView()

    def __onDoneButtonClicked(self, widget):
        """ Done button has been clicked.
        """
        Logger().trace("ConfigController.__onDoneButtonClicked()")
        self.__view.manualMoveDialog.response(0)

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


#if __name__ == "__main__":
    #import gtk
    #from model.shooting import Shooting
    #from hardware.head import HeadSimulation
    #from view_gtk.manualMoveDialog import ManualMoveDialog
    #headSimulation = HeadSimulation()
    #model = Shooting(None, headSimulation)
    #Spy(model, config.SPY_FAST_REFRESH)
    #Spy().start()
    #view = ManualMoveDialog()
    #test = ManualMoveController(None, model, view)
    #gtk.main()

