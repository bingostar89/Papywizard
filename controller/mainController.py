# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Fr�d�ric Mantegazza

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

- MainController

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import thread

import gtk
import gobject

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.exception import HardwareError
from papywizard.view.configDialog import ConfigDialog
from papywizard.view.manualMoveDialog import ManualMoveDialog
from papywizard.view.shootDialog import ShootDialog
from papywizard.view.helpAboutDialog import HelpAboutDialog
from papywizard.view.connectBanner import ConnectBanner
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.configController import ConfigController
from papywizard.controller.manualMoveController import ManualMoveController
from papywizard.controller.shootController import ShootController
from papywizard.controller.connectController import ConnectController
from papywizard.controller.spy import Spy


class MainController(AbstractController):
    """ Main controller object.
    """
    def __init__(self, serializer, model, view):
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

        self.__yawPos = 0
        self.__pitchPos = 0
        
        self.__statusbarTimeoutEventId = None
        self.__connect = None
        self.__connectErrorMessage = None

        # Connect signal/slots
        dic = {"on_quitMenuitem_activate": gtk.main_quit,
               "on_hardwareConnectMenuitem_toggled": self.__onHardwareConnectMenuToggled,
               "on_hardwareSetOriginMenuitem_activate": self.__onHardwareSetOriginMenuActivated,
               "on_hardwareResetMenuitem_activate": self.__onHardwareResetMenuActivated,
               "on_helpAboutMenuitem_activate": self.__onHelpAboutMenuActivated,
               "on_setStartButton_clicked": self.__onSetStartButtonClicked,
               "on_setEndButton_clicked": self.__onSetEndButtonClicked,
               "on_set360Button_clicked": self.__onSet360ButtonClicked,
               "on_set180Button_clicked": self.__onSet180ButtonClicked,
               "on_configButton_clicked": self.__onConfigMenuActivated,
               "on_manualMoveButton_clicked": self.__onManualMoveButtonClicked,
               "on_shootButton_clicked": self.__onShootButtonClicked,
           }
        self.__view.wTree.signal_autoconnect(dic)
        self.__view.mainWindow.connect("destroy", gtk.main_quit)
        self.__view.mainWindow.connect("key-press-event", self.__onKeyPressed)
        self.__view.mainWindow.connect("key-release-event", self.__onKeyReleased)
        self.__view.mainWindow.connect("window-state-event", self.__onWindowStateChanged)

        self.__keyPressedDict = {'FullScreen': False,
                                 'Right': False,
                                 'Left': False,
                                 'Up': False,
                                 'Down': False,
                                 'Home': False,
                                 'End': False
                             }
        self.__key = {'FullScreen': gtk.keysyms.F6,
                      'Right': gtk.keysyms.Right,
                      'Left': gtk.keysyms.Left,
                      'Up': gtk.keysyms.Up,
                      'Down': gtk.keysyms.Down,
                      'Home': gtk.keysyms.Home,
                      'End': gtk.keysyms.End,
                      'Return': gtk.keysyms.Return,
                      }

        # Nokia plateform stuff
        try:
            import hildon
            self.__key['Home'] = gtk.keysyms.F8
            self.__key['End'] = gtk.keysyms.F7
            self.__view.window_in_fullscreen = False
        except ImportError:
            pass

        # Fill widgets
        self.refreshView()

        # Connect stuffs
        Spy().newPosSignal.connect(self.__refreshPos)
        self.__model.switchToRealHardwareSignal.connect(self.__switchToRealHardwareCallback)

        # Try to autoconnect to real hardware (todo: use a config flag)
        self.__view.hardwareConnectMenuitem.set_active(True)

    # Helpers
        
    # Callbacks
    def __onKeyPressed(self, widget, event, *args):
        Logger().trace("MainController.__onKeyPressed()")
        
        # 'FullScreen' key
        if event.keyval == self.__key['FullScreen']:
            if not self.__keyPressedDict['FullScreen']:
                Logger().debug("MainController.__onKeyPressed(): 'FullScreen' key pressed")
                if self.__view.window_in_fullscreen:
                    self.__view.mainWindow.unfullscreen()
                else:
                    self.__view.mainWindow.fullscreen()
                self.__keyPressedDict['FullScreen'] = True
            return True

        # 'Right' key
        elif event.keyval == self.__key['Right']:
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyPressed(): 'Right' key pressed; start 'yaw' axis dir '+'")
                self.__keyPressedDict['Right'] = True
                self.__model.hardware.startAxis('yaw', '+')
            return True

        # 'Left' key
        elif event.keyval == self.__key['Left']:
            if not self.__keyPressedDict['Left'] and not self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyPressed(): 'Left' key pressed; start 'yaw' axis dir '-'")
                self.__keyPressedDict['Left'] = True
                self.__model.hardware.startAxis('yaw', '-')
            return True

        # 'Up' key
        elif event.keyval == self.__key['Up']:
            if not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyPressed(): 'Up' key pressed; start 'pitch' axis dir '+'")
                self.__keyPressedDict['Up'] = True
                self.__model.hardware.startAxis('pitch', '+')
            return True

        # 'Down' key
        elif event.keyval == self.__key['Down']:
            if not self.__keyPressedDict['Down'] and not self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyPressed(): 'Down' key pressed; start 'pitch' axis dir '-'")
                self.__keyPressedDict['Down'] = True
                self.__model.hardware.startAxis('pitch', '-')
            return True

        # 'Home' key
        elif event.keyval == self.__key['Home']:
            if not self.__keyPressedDict['Home'] and \
               not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; store start position")
                self.__keyPressedDict['Home'] = True
                self.__model.mosaic.storeStartPosition(self.__yawPos, self.__pitchPos)
                self.refreshView()
            return True

        # 'End' key
        elif event.keyval == self.__key['End']:
            if not self.__keyPressedDict['End'] and not self.__keyPressedDict['Home'] and \
               not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; store end position")
                self.__keyPressedDict['End'] = True
                self.__model.mosaic.storeEndPosition(self.__yawPos, self.__pitchPos)
                self.refreshView()
            return True

        # 'Return' key
        elif event.keyval == self.__key['Return']:
            Logger().debug("MainController.__onKeyPressed(): 'Return' key pressed; open shoot dialog")
            self.__openShootdialog()
            return True

        else:
            Logger().warning("MainController.__onKeyPressed(): unbind '%s' key" % event.keyval)

    def __onKeyReleased(self, widget, event, *args):
        Logger().trace("MainController.__onKeyReleased()")
        
        # 'FullScreen' key
        if event.keyval == self.__key['FullScreen']:
            if self.__keyPressedDict['FullScreen']:
                Logger().debug("MainController.__onKeyReleased(): 'FullScreen' key released")
                self.__keyPressedDict['FullScreen'] = False
            return True

        # 'Right' key
        if event.keyval == self.__key['Right']:
            if self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyReleased(): 'Right' key released; stop 'yaw' axis")
                self.__model.hardware.stopAxis('yaw')
                self.__keyPressedDict['Right'] = False
            return True

        # 'Left' key
        if event.keyval == self.__key['Left']:
            if self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyReleased(): 'Left' key released; stop 'yaw' axis")
                self.__model.hardware.stopAxis('yaw')
                self.__keyPressedDict['Left'] = False
            return True

        # 'Up' key
        if event.keyval == self.__key['Up']:
            if self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyReleased(): 'Up' key released; stop 'pitch' axis")
                self.__model.hardware.stopAxis('pitch')
                self.__keyPressedDict['Up'] = False
            return True

        # 'Down' key
        if event.keyval == self.__key['Down']:
            if self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyReleased(): 'Down' key released; stop 'pitch' axis")
                self.__model.hardware.stopAxis('pitch')
                self.__keyPressedDict['Down'] = False
            return True

        # 'Home' key
        if event.keyval == self.__key['Home']:
            if self.__keyPressedDict['Home']:
                Logger().debug("MainController.__onKeyReleased(): 'Home' key released")
                self.__keyPressedDict['Home'] = False
            return True

        # 'End' key
        if event.keyval == self.__key['End']:
            if self.__keyPressedDict['End']:
                Logger().debug("MainController.__onKeyReleased(): 'End' key released")
                self.__keyPressedDict['End'] = False
            return True

        else:
            Logger().warning("MainController.__onKeyReleased(): unbind '%s' key" % event.keyval)

    def __onWindowStateChanged(self, widget, event, *args):
        Logger().debug("MainController.__onWindowStateChanged()")
        if event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.__view.window_in_fullscreen = True
        else:
            self.__view.window_in_fullscreen = False

    def __onHardwareConnectMenuToggled(self, widget):
        switch = self.__view.hardwareConnectMenuitem.get_active()
        Logger().trace("MainController.__onHardwareConnectMenuActivated(%s)" % switch)
        if switch:
            self.__connectToHardware()
        else:
            self.__goToSimulationMode()

    def __onHardwareResetMenuActivated(self, widget):
        Logger().trace("MainController.__onHardwareResetMenuActivated()")
        Logger().info("Reseting hardware")
        self.__model.hardware.reset()
        self.setStatusbarMessage("Hardware has been reseted", 10)

    def __onHardwareSetOriginMenuActivated(self, widget):
        Logger().trace("MainController.__onHardwareSetOriginMenuActivated()")
        Logger().info("Set hardware origin")
        self.__model.hardware.setOrigin()
        self.setStatusbarMessage("Origin set to current position", 10)

    def __onHelpAboutMenuActivated(self, widget):
        Logger().trace("MainController.__onHelpAboutMenuActivated()")
        view = HelpAboutDialog(self.__view)
        retCode = view.helpAboutDialog.run()
        view.helpAboutDialog.destroy()

    def __onSetStartButtonClicked(self, widget):
        Logger().trace("MainController.__onSetStartButtonClicked()")
        #yaw, pitch = self.__mode.hardware.readPosition()
        self.__model.mosaic.storeStartPosition(self.__yawPos, self.__pitchPos)
        self.refreshView()
        self.setStatusbarMessage("Start position set to current position", 10)

    def __onSetEndButtonClicked(self, widget):
        Logger().trace("MainController.__onSetEndButtonClicked()")
        #yaw, pitch = self.__mode.hardware.readPosition()
        self.__model.mosaic.storeEndPosition(self.__yawPos, self.__pitchPos)
        self.refreshView()
        self.setStatusbarMessage("End position set to current position", 10)

    def __onSet360ButtonClicked(self, widget):
        Logger().trace("MainController.__onSet360ButtonClicked()")
        #yaw, pitch = self.__mode.hardware.readPosition()
        self.__model.mosaic.setYaw360(self.__yawPos)
        self.refreshView()
        self.setStatusbarMessage(u"Start/End yaw positions set to 360�", 10)

    def __onSet180ButtonClicked(self, widget):
        Logger().trace("MainController.__onSet180ButtonClicked()")
        #yaw, pitch = self.__mode.hardware.readPosition()
        self.__model.mosaic.setPitch180(self.__pitchPos)
        self.refreshView()
        self.setStatusbarMessage(u"Start/End pitch positions set to 180�", 10)

    def __onManualMoveButtonClicked(self, widget):
        Logger().trace("MainController.__onManualMoveButtonClicked()")
        view = ManualMoveDialog()
        controller = ManualMoveController(self, self.__serializer, self.__model, view)
        retCode = view.manualMoveDialog.run()
        view.manualMoveDialog.destroy()

    def __onConfigMenuActivated(self, widget):
        Logger().trace("MainController.__onConfigMenuActivated()")
        view = ConfigDialog()
        controller = ConfigController(self, self.__model, view)
        retCode = view.configDialog.run()
        view.configDialog.destroy()
        Logger().setLevel(ConfigManager().get('Logger', 'LOGGER_LEVEL'))
        ConfigManager().save()
        self.refreshView()

    def __openShootdialog(self):
        self.__model.initProgress()
        view = ShootDialog()
        controller = ShootController(self, self.__model, view)
        retCode = view.shootDialog.run()
        view.shootDialog.destroy()

    def __onShootButtonClicked(self, widget):
        Logger().trace("MainController.__onShootButtonClicked()")
        self.__openShootdialog()

    def __switchToRealHardwareCallback(self, flag, message=""):
        Logger().debug("MainController.__hardwareInit(): flag=%s" % flag)
        self.__connectStatus = flag
        self.__connectErrorMessage = message
        self.__connectController.closeBanner()
    
    # Real work
    def __connectToHardware(self):
        """ Connect to real hardware.
        """
        def refreshProgressbar(rogressbar):
            """ Refresh the progressbar in activity mode.
            
            Should be called by a timeout.
            """
            progressbar.pulse()
            return True
        
        Logger().info("Connecting to real hardware...")
        self.setStatusbarMessage("Connecting to real hardware...")
        self.__view.hardwareConnectMenuitem.set_sensitive(False)
        
        # Open connection banner (todo: use real banner on Nokia). Make a special object
        self.__connectStatus = None
        view = ConnectBanner()
        self.__connectController = ConnectController(self.__view, self.__model, view)
        self.__connectBanner = view.connectBanner
        self.__connectBanner.show()
        
        # Launch connexion thread
        thread.start_new_thread(self.__model.switchToRealHardware, ())
        
        # Wait for end of connection
        while self.__connectStatus is None:
            while gtk.events_pending():
                gtk.main_iteration()
            time.sleep(0.05)
        
        # Check connection status
        if self.__connectStatus:
            Spy().setRefreshRate(config.SPY_SLOW_REFRESH)
            self.__view.connectImage.set_from_stock(gtk.STOCK_YES, 4)
            Logger().info("Now connected to real hardware")
            self.setStatusbarMessage("Now connected to real hardware", 5)
        else:
            Logger().error("Connection to hardware failed (%s)" % self.__connectErrorMessage)
            messageDialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
                                                     message_format="Connection to hardware failed")
            messageDialog.format_secondary_text(self.__connectErrorMessage)
            messageDialog.run()
            messageDialog.destroy()
            self.__view.hardwareConnectMenuitem.set_active(False)
            
        self.__view.hardwareConnectMenuitem.set_sensitive(True)

    def __goToSimulationMode(self):
        """ Connect to simulated hardware.
        """
        Logger().info("Go to simulation mode")
        self.__model.switchToSimulatedHardware()
        Spy().setRefreshRate(config.SPY_FAST_REFRESH)
        self.__view.connectImage.set_from_stock(gtk.STOCK_NO, 4)
        self.setStatusbarMessage("Now in simulation mode", 5)

    def __refreshPos(self, yaw, pitch):
        """ Refresh position according to new pos.

        @param yaw: yaw axis value
        @type yaw: float

        @param pitch: pitch axix value
        @type pitch: float
        """
        Logger().trace("MainController.__refreshPos()")
        self.__yawPos = yaw
        self.__pitchPos = pitch
        self.__serializer.apply(self.refreshView)
        
    def setStatusbarMessage(self, message=None, delay=0):
        """ Display a message on the statusbar.
        
        @param message: message to display. If None, clear statusbar
        @type message: str
        
        @param delay: display message duration, in s (0 means forever)
        @type delay: int
        """
        self.__view.statusbar.pop(self.__view.statusbarContextId)
        if self.__statusbarTimeoutEventId is not None:
            gobject.source_remove(self.__statusbarTimeoutEventId)
        if message is not None:
            self.__view.statusbar.push(self.__view.statusbarContextId, message)
            if delay:
                self.__statusbarTimeoutEventId = gobject.timeout_add(delay * 1000, self.setStatusbarMessage)
            else:
                self.__statusbarTimeoutEventId = None

    def refreshView(self):
        values = {'yawPos': self.__yawPos,
                  'pitchPos': self.__pitchPos,
                  'yawStart': self.__model.mosaic.yawStart,
                  'pitchStart': self.__model.mosaic.pitchStart,
                  'yawEnd': self.__model.mosaic.yawEnd,
                  'pitchEnd': self.__model.mosaic.pitchEnd,
                  'yawFov': self.__model.mosaic.yawFov,
                  'pitchFov':  self.__model.mosaic.pitchFov,
                  'yawNbPicts':  self.__model.mosaic.yawNbPicts,
                  'pitchNbPicts':  self.__model.mosaic.pitchNbPicts,
                  'yawRealOverlap': int(round(100 * self.__model.mosaic.yawRealOverlap)),
                  'pitchRealOverlap': int(round(100 * self.__model.mosaic.pitchRealOverlap))
              }
        self.__view.fillWidgets(values)
