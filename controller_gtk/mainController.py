# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Controller.

Implements class:

- MainController

@author: Frederic Mantegazza
@copyright: 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time
import threading

import gtk

from common import config
from common.loggingServices import Logger
from common.exception import HardwareError
from view_gtk.bluetoothConnectDialog import BluetoothConnectDialog
#from view_gtk.configDialog import ConfigDialog
from view_gtk.manualMoveDialog import ManualMoveDialog
from view_gtk.shootDialog import ShootDialog
from view_gtk.helpAboutDialog import HelpAboutDialog
from controller.abstractController import AbstractController
from controller_gtk.bluetoothConnectController import BluetoothConnectController
#from controller_gtk.configController import ConfigController
from controller_gtk.manualMoveController import ManualMoveController
from controller_gtk.shootController import ShootController
from controller.spy import Spy


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

        # Connect signal/slots
        dic = {"on_mainWindow_destroy": gtk.main_quit,
               "on_configMenuitem_activate": self.__onConfigButtonClicked,
               "on_quitMenuitem_activate": gtk.main_quit,
               "on_hardwareConnectMenuitem_toggled": self.__onHardwareConnectMenuToggled,
               "on_hardwareResetMenuitem_activate": self.__onHardwareResetMenuActivated,
               "on_view3DShowMenuitem_toggled": self.__onView3DShowMenuToggled,
               "on_helpAboutMenuitem_activate": self.__onHelpAboutMenuActivated,
               "on_setStartButton_clicked": self.__onSetStartButtonClicked,
               "on_setEndButton_clicked": self.__onSetEndButtonClicked,
               "on_zenithCheckbutton_toggled": self.__onZenithCheckbuttonToggled,
               "on_nadirCheckbutton_toggled": self.__onNadirCheckbuttonToggled,
               "on_fullSphericalButton_clicked": self.__onFullSphericalButtonClicked,
               "on_manualMoveButton_clicked": self.__onManualMoveButtonClicked,
               "on_configButton_clicked": self.__onConfigButtonClicked,
               "on_shootButton_clicked": self.__onShootButtonClicked
           }
        self.__view.wTree.signal_autoconnect(dic)
        
        # Nokia plateform stuff
        try:
            import hildon
            
            self.__view.mainWindow.connect("destroy", gtk.main_quit)
            self.__view.mainWindow.connect("key-press-event", self.__onKeyPressed)
            self.__view.mainWindow.connect("window-state-event", self.__onWindowStateChanged)
            
        except ImportError:
            pass
        
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
        #self.__connectToHardware()
        
        # Check if 3D view is available
        #if view3D is None:
            #self.__view.view3DShowVar.set(0)
            #self.__view.view3DMenu.entryconfig(self.__view.VIEW3D_SHOW_MENU_ENTRY, state=tk.DISABLED)
        
    # Nokia plateform callbacks
    def __onWindowStateChanged(self, widget, event, *args):
        if event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.__view.mindow_in_fullscreen = True
        else:
            self.__view.mindow_in_fullscreen = False

    def __onKeyPressed(self, widget, event, *args):
        if event.keyval == gtk.keysyms.F6:
            
            # The "Full screen" hardware key has been pressed
            if self.__view.mindow_in_fullscreen:
                self.__view.mainWindow.unfullscreen()
            else:
                self.__view.mainWindow.fullscreen()

    # Normal callbacks
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
        self.__view.statusbar.pop(self.__view.hardwareContextId)
        self.__view.statusbar.push(self.__view.hardwareContextId, "Connecting to real hardware...")
        try:

            ## Bluetooth driver
            #if config.DRIVER == "bluetooth":
                #view = BluetoothConnectDialog()
                #controller = BluetoothConnectController(self, self.__model, view)
                #retCode = view.bluetoothConnectDialog.run()
                #view.bluetoothConnectDialog.destroy()
                #if not retCode:
                    #Logger().warning("Connection to hardware canceled")
                    #self.__view.hardwareConnectMenuitem.set_active(False)
                    #return

            self.__model.switchToRealHardware()
            Spy().setRefreshRate(config.SPY_SLOW_REFRESH)
            #self.__view.hardwareResetMenuitem.set_sensitive(True)
            Logger().info("Now connected to real hardware")
            self.__view.connectImage.set_from_stock(gtk.STOCK_YES, 4)
            #self.__view.statusbar.push(self.__view.hardwareContextId, "Now connected to real hardware")

        except HardwareError: # Raised by model
            Logger().error("Can't connect to hardware; go back to simulation mode")
            #self.__view.statusbar.pop(self.__view.hardwareContextId)
            #self.__view.statusbar.push(self.__view.hardwareContextId, "Can't connect to hardware")
            self.__view.hardwareConnectMenuitem.set_active(False)

        self.__view.statusbar.pop(self.__view.hardwareContextId)

    def __goToSimulationMode(self):
        """ Connect to simulated hardware.
        """
        Logger().info("Go to simulation mode")
        self.__model.switchToSimulatedHardware()
        Spy().setRefreshRate(config.SPY_FAST_REFRESH)
        #self.__view.hardwareResetMenuitem.set_sensitive(False)
        self.__view.connectImage.set_from_stock(gtk.STOCK_NO, 4)

    def __onHardwareConnectMenuToggled(self, widget):
        """ Connect check button toggled.
        """
        switch = self.__view.hardwareConnectMenuitem.get_active()
        Logger().trace("MainController.__onHardwareConnectMenuActivated(%s)" % switch)
        if switch:
            self.__connectToHardware()
        else:
            self.__goToSimulationMode()

    def __onHardwareResetMenuActivated(self, widget):
        """ Hard reset menu selected.
        """
        Logger().trace("MainController.__onHardwareResetMenuActivated()")
        Logger().info("Reseting hardware")
        self.__model.hardware.reset()

    def __onView3DShowMenuToggled(self, widget):
        """ Connect check button toggled.
        """
        switch = self.__view.view3DShowMenuitem.get_active()
        Logger().trace("MainController.__onView3DShowMenuActivated(%s)" % switch)
        #if switch:
            #if self.__view3D is not None:
                #Logger().debug("MainController.__view3DShowMenu(): show 3D view")
                #self.__view3D.visible = True
            #else:
                #tkMB.showerror("3D View", "Some libs are missing in order to use 3D view")
                #self.__view.view3DShowVar.set(0)
        #else:
            #if self.__view3D is not None:
                #Logger().debug("MainController.__view3DShowMenu(): hide 3D view")
                #self.__view3D.visible=False
        
    def __onHelpAboutMenuActivated(self, widget):
        """ Connect check button toggled.
        """
        Logger().trace("MainController.__onHelpAboutMenuActivated()")
        view = HelpAboutDialog(self.__view)
        retCode = view.helpAboutDialog.run()
        view.helpAboutDialog.destroy()

    def __onSetStartButtonClicked(self, widget):
        Logger().trace("MainController.__onSetStartButtonClicked()")
        self.__model.storeStartPosition()
        self.refreshView()

    def __onSetEndButtonClicked(self, widget):
        Logger().trace("MainController.__onSetEndButtonClicked()")
        self.__model.storeEndPosition()
        self.refreshView()

    #def __onSetFovButtonClicked(self, widget):
        #Logger().trace("MainController.__onSetFovButtonClicked()")
        #tkMB.showwarning("Set total field of view", "Not yet implemented")

    #def __onSetNbPictsButtonClicked(self, widget):
        #tkMB.showwarning("Set total nb picts", "Not yet implemented")

    def __onZenithCheckbuttonToggled(self, widget):
        Logger().trace("MainController.__onZenithCheckbuttonToggled()")
        self.__model.mosaic.zenith = bool(self.__view.zenithCheckbutton.get_active())

    def __onNadirCheckbuttonToggled(self, widget):
        Logger().trace("MainController.__onNadirCheckbuttonToggled()")
        self.__model.mosaic.nadir = bool(self.__view.nadirCheckbutton.get_active())

    def __onFullSphericalButtonClicked(self, widget):
        Logger().trace("MainController.__fullPanoButtonClicked()")

    def __onManualMoveButtonClicked(self, widget):
        Logger().trace("MainController.__onManualMoveButtonClicked()")
        view = ManualMoveDialog()
        controller = ManualMoveController(self, self.__serializer, self.__model, view)
        retCode = view.manualMoveDialog.run()
        view.manualMoveDialog.destroy()

    def __onConfigButtonClicked(self, widget):
        Logger().trace("MainController.__onConfigButtonClicked()")
        #view = ConfigDialog(self.__view)
        #controller = ConfigController(self, self.__model, view) # Open as modal
        #self.refreshView()

    def __onShootButtonClicked(self, widget):
        Logger().trace("MainController.__onShootButtonClicked()")
        view = ShootDialog()
        controller = ShootController(self, self.__serializer, self.__model, view)
        retCode = view.shootDialog.run()
        view.shootDialog.destroy()
        
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


if __name__ == "__main__":
    import gtk
    from model.shooting import Shooting
    from hardware.head import HeadSimulation
    from view_gtk.mainWindow import MainWindow
    headSimulation = HeadSimulation()
    model = Shooting(None, headSimulation)
    Spy(model, config.SPY_FAST_REFRESH)
    Spy().start()
    view = MainWindow()
    test = MainController(None, model, view)
    gtk.main()
    
