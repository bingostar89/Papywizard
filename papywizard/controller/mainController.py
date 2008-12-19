# -*- coding: utf-8 -*-

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

- MainController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import thread
import os.path
import webbrowser

import pygtk
pygtk.require("2.0")
import gtk
import pango
import gobject

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.presetManager import PresetManager
from papywizard.common.exception import HardwareError
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.messageController import ErrorMessageController, WarningMessageController
from papywizard.controller.loggerController import LoggerController
from papywizard.controller.helpAboutController import HelpAboutController
from papywizard.controller.totalFovController import TotalFovController
from papywizard.controller.nbPictsController import NbPictsController
from papywizard.controller.presetInfoController import PresetInfoController
from papywizard.controller.configController import ConfigController
from papywizard.controller.shootController import ShootController
from papywizard.controller.waitController import WaitController
from papywizard.controller.spy import Spy


class MainController(AbstractController):
    """ Main controller object.
    """
    def __init__(self, model, serializer, gtkLogStream):
        """ Init the controller.

        @param serializer: object used to serialize toolkit events
        @type serializer: {Serializer}
        """
        super(MainController, self).__init__(None, model, serializer)
        self.__gtkLogStream = gtkLogStream

        # Try to autoconnect to real hardware
        if ConfigManager().getBoolean('Preferences', 'HARDWARE_AUTO_CONNECT'):
            self.hardwareConnectMenuitem.set_active(True)

    def _init(self):
        self._gladeFile = "mainWindow.glade"
        self._signalDict = {"on_fileLoadPresetMenuitem_activate": self.__onFileLoadPresetMenuitemActivate,
                            "on_fileLoadGtkrcMenuitem_activate": self.__onFileLoadGtkrcMenuitemActivate,
                            "on_quitMenuitem_activate": gtk.main_quit,
                            "on_hardwareConnectMenuitem_toggled": self.__onHardwareConnectMenuitemToggled,
                            "on_hardwareSetLimitYawMinusMenuitem_activate": self.__onHardwareSetLimitYawMinusMenuitemActivate,
                            "on_hardwareSetLimitYawPlusMenuitem_activate": self.__onHardwareSetLimitYawPlusMenuitemActivate,
                            "on_hardwareSetLimitPitchPlusMenuitem_activate": self.__onHardwareSetLimitPitchPlusMenuitemActivate,
                            "on_hardwareSetLimitPitchMinusMenuitem_activate": self.__onHardwareSetLimitPitchMinusMenuitemActivate,
                            "on_hardwareClearLimitsMenuitem_activate": self.__onHardwareClearLimitsMenuitemActivate,
                            "on_helpManualMenuitem_activate": self.__onHelpManualMenuitemActivate,
                            "on_helpWhatsThisMenuitem_activate": self.__onHelpWhatsThisMenuitemActivate,
                            "on_helpViewLogMenuitem_activate": self.__onHelpViewLogMenuitemActivate,
                            "on_helpAboutMenuitem_activate": self.__onHelpAboutMenuitemActivate,

                            "on_modeMosaicRadiobutton_toggled": self.__onModeMosaicRadiobuttonToggled,

                            "on_setYawStartButton_clicked": self.__onSetYawStartButtonClicked,
                            "on_setPitchStartButton_clicked": self.__onSetPitchStartButtonClicked,
                            "on_setYawEndButton_clicked": self.__onSetYawEndButtonClicked,
                            "on_setPitchEndButton_clicked": self.__onSetPitchEndButtonClicked,
                            "on_setStartButton_clicked": self.__onSetStartButtonClicked,
                            "on_setEndButton_clicked": self.__onSetEndButtonClicked,
                            "on_totalFovButton_clicked": self.__onTotalFovButtonClicked,
                            "on_nbPictsButton_clicked": self.__onNbPictsButtonClicked,

                            "on_presetCombobox_changed": self.__onPresetComboboxChanged,
                            "on_presetInfoButton_clicked": self.__onPresetInfoButtonClicked,

                            "on_hardwareSetOriginButton_clicked": self.__onHardwareSetOriginButtonClicked,
                            "on_yawMovePlusTogglebutton_pressed": self.__onYawMovePlusTogglebuttonPressed,
                            "on_yawMovePlusTogglebutton_released": self.__onYawMovePlusTogglebuttonReleased,
                            "on_pitchMovePlusTogglebutton_pressed": self.__onPitchMovePlusTogglebuttonPressed,
                            "on_pitchMovePlusTogglebutton_released": self.__onPitchMovePlusTogglebuttonReleased,
                            "on_yawMoveMinusTogglebutton_pressed": self.__onYawMoveMinusTogglebuttonPressed,
                            "on_yawMoveMinusTogglebutton_released": self.__onYawMoveMinusTogglebuttonReleased,
                            "on_pitchMoveMinusTogglebutton_pressed": self.__onPitchMoveMinusTogglebuttonPressed,
                            "on_pitchMoveMinusTogglebutton_released": self.__onPitchMoveMinusTogglebuttonReleased,

                            "on_configButton_clicked": self.__onConfigButtonClicked,
                            "on_shootButton_clicked": self.__onShootButtonClicked,
                        }

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
                      'Tab': gtk.keysyms.Tab,
                      'space': gtk.keysyms.space,
                      'Return': gtk.keysyms.Return,
                      }

        # Nokia plateform stuff
        try:
            import hildon
            self.__key['Home'] = gtk.keysyms.F8
            self.__key['End'] = gtk.keysyms.F7
        except ImportError:
            pass

        self.__yawPos = 0
        self.__pitchPos = 0
        self.__statusbarTimeoutEventId = None
        self.__connectStatus = None
        self.__connectErrorMessage = None
        self.__mosaicInputParam = 'startEnd'
        self.__manualSpeed = 'normal'
        #self.__fullScreen = False

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        super(MainController, self)._retreiveWidgets()

        self.mainVbox = self.wTree.get_widget("mainVbox")
        self.menubar = self.wTree.get_widget("menubar")
        self.hardwareConnectMenuitem = self.wTree.get_widget("hardwareConnectMenuitem")
        self.hardwareResetMenuitem = self.wTree.get_widget("hardwareResetMenuitem")
        self.modeMosaicRadiobutton = self.wTree.get_widget("modeMosaicRadiobutton")
        self.modePresetRadiobutton = self.wTree.get_widget("modePresetRadiobutton")
        self.mosaicFrame = self.wTree.get_widget("mosaicFrame")
        self.setYawStartButtonLabel = self.wTree.get_widget("setYawStartButton").child
        self.setPitchStartButtonLabel = self.wTree.get_widget("setPitchStartButton").child
        self.setYawEndButtonLabel = self.wTree.get_widget("setYawEndButton").child
        self.setPitchEndButtonLabel = self.wTree.get_widget("setPitchEndButton").child
        self.setStartTogglebutton = self.wTree.get_widget("setStartTogglebutton")
        self.setEndTogglebutton = self.wTree.get_widget("setEndTogglebutton")
        self.totalFovButton = self.wTree.get_widget("totalFovButton")
        self.nbPictsButton = self.wTree.get_widget("nbPictsButton")
        self.yawFovLabel = self.wTree.get_widget("yawFovLabel")
        self.pitchFovLabel = self.wTree.get_widget("pitchFovLabel")
        self.yawNbPictsLabel = self.wTree.get_widget("yawNbPictsLabel")
        self.pitchNbPictsLabel = self.wTree.get_widget("pitchNbPictsLabel")
        self.yawRealOverlapLabel = self.wTree.get_widget("yawRealOverlapLabel")
        self.pitchRealOverlapLabel = self.wTree.get_widget("pitchRealOverlapLabel")
        self.yawResolutionLabel = self.wTree.get_widget("yawResolutionLabel")
        self.pitchResolutionLabel = self.wTree.get_widget("pitchResolutionLabel")
        self.presetFrame = self.wTree.get_widget("presetFrame")
        self.presetCombobox = self.wTree.get_widget("presetCombobox")
        self.yawHeadPosLabel = self.wTree.get_widget("yawHeadPosLabel")
        self.pitchHeadPosLabel = self.wTree.get_widget("pitchHeadPosLabel")
        self.manualSpeedImage =  self.wTree.get_widget("manualSpeedImage")
        self.yawMovePlusTogglebutton = self.wTree.get_widget("yawMovePlusTogglebutton")
        self.pitchMovePlusTogglebutton = self.wTree.get_widget("pitchMovePlusTogglebutton")
        self.yawMoveMinusTogglebutton = self.wTree.get_widget("yawMoveMinusTogglebutton")
        self.pitchMoveMinusTogglebutton = self.wTree.get_widget("pitchMoveMinusTogglebutton")
        self.configButton = self.wTree.get_widget("configButton")
        self.shootButton = self.wTree.get_widget("shootButton")
        self.statusbar = self.wTree.get_widget("statusbar")
        self.statusbarContextId = self.statusbar.get_context_id("default")
        self.connectImage = self.wTree.get_widget("connectImage")

    def _initWidgets(self):
        listStore = gtk.ListStore(gobject.TYPE_STRING)
        self.presetCombobox.set_model(listStore)
        cell = gtk.CellRendererText()
        self.presetCombobox.pack_start(cell, True)
        #self.presetCombobox.add_attribute(cell, 'text', 0)
        self.__populatePresetCombobox()

        # Font
        self._setFontParams(self.yawHeadPosLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.pitchHeadPosLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.setYawStartButtonLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.setPitchStartButtonLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.setYawEndButtonLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.setPitchEndButtonLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.yawFovLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.pitchFovLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.yawNbPictsLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.pitchNbPictsLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.yawRealOverlapLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.pitchRealOverlapLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.yawResolutionLabel, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.pitchResolutionLabel, weight=pango.WEIGHT_BOLD)

        # Nokia plateform stuff
        try:
            import hildon

            self.app = hildon.Program()
            window = hildon.Window()
            window.set_title(self.dialog.get_title())
            #window.fullscreen()
            #self.__fullScreen = True
            self.app.add_window(window)
            self.mainVbox.reparent(window)

            menu = gtk.Menu()
            for child in self.menubar.get_children():
                child.reparent(menu)
            window.set_menu(menu)

            self.menubar.destroy()
            self.dialog.destroy()
            window.show_all()
            self.menuBar = menu
            self.dialog = window

        except ImportError:
            pass

        if self.__fullScreen:
            self.dialog.fullscreen()

    def _connectSignals(self):
        super(MainController, self)._connectSignals()

        self.dialog.connect("destroy", gtk.main_quit)
        self.dialog.connect("key-press-event", self.__onKeyPressed)
        self.dialog.connect("key-release-event", self.__onKeyReleased)
        #self.dialog.connect("window-state-event", self.__onWindowStateChanged)

        Spy().newPosSignal.connect(self.__refreshPos)
        self._model.switchToRealHardwareSignal.connect(self.__switchToRealHardwareCallback)

    def _disconnectSignals(self):
        Spy().newPosSignal.disconnect(self.__refreshPos)
        self._model.switchToRealHardwareSignal.disconnect(self.__switchToRealHardwareCallback)

    # Properties
    def __getFullScreenFlag(self):
        """
        """
        return ConfigManager().getBoolean('General', 'FULLSCREEN_FLAG')

    def __setFullScreenFlag(self, flag):
        """
        """
        ConfigManager().setBoolean('General', 'FULLSCREEN_FLAG', flag)

    __fullScreen = property(__getFullScreenFlag, __setFullScreenFlag)

    # Callbacks
    def __onKeyPressed(self, widget, event, *args):
        Logger().trace("MainController.__onKeyPressed()")

        # 'FullScreen' key
        if event.keyval == self.__key['FullScreen']:
            if not self.__keyPressedDict['FullScreen']:
                Logger().debug("MainController.__onKeyPressed(): 'FullScreen' key pressed")
                if self.__fullScreen:
                    self.dialog.unfullscreen()
                    self.__fullScreen = False
                else:
                    self.dialog.fullscreen()
                    self.__fullScreen = True
                self.__keyPressedDict['FullScreen'] = True
            return True

        # 'Right' key
        if event.keyval == self.__key['Right']:
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyPressed(): 'Right' key pressed; start 'yaw' axis dir '+'")
                self.__keyPressedDict['Right'] = True
                self.yawMovePlusTogglebutton.set_active(True)
                self._model.hardware.startAxis('yaw', '+')
            return True

        # 'Left' key
        elif event.keyval == self.__key['Left']:
            if not self.__keyPressedDict['Left'] and not self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyPressed(): 'Left' key pressed; start 'yaw' axis dir '-'")
                self.__keyPressedDict['Left'] = True
                self.yawMoveMinusTogglebutton.set_active(True)
                self._model.hardware.startAxis('yaw', '-')
            return True

        # 'Up' key
        elif event.keyval == self.__key['Up']:
            if not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyPressed(): 'Up' key pressed; start 'pitch' axis dir '+'")
                self.__keyPressedDict['Up'] = True
                self.pitchMovePlusTogglebutton.set_active(True)
                self._model.hardware.startAxis('pitch', '+')
            return True

        # 'Down' key
        elif event.keyval == self.__key['Down']:
            if not self.__keyPressedDict['Down'] and not self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyPressed(): 'Down' key pressed; start 'pitch' axis dir '-'")
                self.__keyPressedDict['Down'] = True
                self.pitchMoveMinusTogglebutton.set_active(True)
                self._model.hardware.startAxis('pitch', '-')
            return True

        # 'Home' key
        elif event.keyval == self.__key['Home']:
            if not self.__keyPressedDict['Home'] and \
               not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                self.__keyPressedDict['Home'] = True
                if self.__manualSpeed == 'normal':
                    self.__manualSpeed = 'slow'
                    Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; select slow speed")
                    self._model.hardware.setManualSpeed('slow')
                    self.manualSpeedImage.set_from_stock(gtk.STOCK_MEDIA_PLAY, 4)
                    self.setStatusbarMessage(_("Manual speed set to slow"), 10)
                elif self.__manualSpeed == 'fast':
                    self.__manualSpeed = 'normal'
                    Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; select normal speed")
                    self._model.hardware.setManualSpeed('normal')
                    self.manualSpeedImage.set_from_stock(gtk.STOCK_MEDIA_FORWARD, 4)
                    self.setStatusbarMessage(_("Manual speed set to normal"), 10)
            return True

        # 'End' key
        elif event.keyval == self.__key['End']:
            if not self.__keyPressedDict['End'] and not self.__keyPressedDict['Home'] and \
               not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                self.__keyPressedDict['End'] = True
                if self.__manualSpeed == 'slow':
                    self.__manualSpeed = 'normal'
                    Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; select normal speed")
                    self._model.hardware.setManualSpeed('normal')
                    self.manualSpeedImage.set_from_stock(gtk.STOCK_MEDIA_FORWARD, 4)
                    self.setStatusbarMessage(_("Manual speed set to normal"), 10)
                elif self.__manualSpeed == 'normal':
                    controller = WarningMessageController(_("Fast manual speed"),
                                                          _("Manual speed set to 'fast'\nThis can be dangerous for the hardware!"))
                    self.__manualSpeed = 'fast'
                    Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; select fast speed")
                    self._model.hardware.setManualSpeed('fast')
                    self.manualSpeedImage.set_from_stock(gtk.STOCK_DIALOG_WARNING, 4)
                    self.setStatusbarMessage(_("Manual speed set to fast"), 10)

            return True

        # 'Tab' key
        elif event.keyval == self.__key['Tab']:
            Logger().debug("MainController.__onKeyPressed(): 'Tab' key pressed; blocked")
            return True

        # 'space' key
        elif event.keyval == self.__key['space']:
            Logger().debug("MainController.__onKeyPressed(): 'space' key pressed; blocked")
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
                self._model.hardware.stopAxis('yaw')
                self._model.hardware.waitStopAxis('yaw')
                self.__keyPressedDict['Right'] = False
                self.yawMovePlusTogglebutton.set_active(False)
            return True

        # 'Left' key
        if event.keyval == self.__key['Left']:
            if self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyReleased(): 'Left' key released; stop 'yaw' axis")
                self._model.hardware.stopAxis('yaw')
                self._model.hardware.waitStopAxis('yaw')
                self.__keyPressedDict['Left'] = False
                self.yawMoveMinusTogglebutton.set_active(False)
            return True

        # 'Up' key
        if event.keyval == self.__key['Up']:
            if self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyReleased(): 'Up' key released; stop 'pitch' axis")
                self._model.hardware.stopAxis('pitch')
                self._model.hardware.waitStopAxis('pitch')
                self.__keyPressedDict['Up'] = False
                self.pitchMovePlusTogglebutton.set_active(False)
            return True

        # 'Down' key
        if event.keyval == self.__key['Down']:
            if self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyReleased(): 'Down' key released; stop 'pitch' axis")
                self._model.hardware.stopAxis('pitch')
                self._model.hardware.waitStopAxis('pitch')
                self.__keyPressedDict['Down'] = False
                self.pitchMoveMinusTogglebutton.set_active(False)
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

        # 'Tab' key
        elif event.keyval == self.__key['Tab']:
            Logger().debug("MainController.__onKeyReleased(): 'Tab' key released")
            return True

        # 'space' key
        elif event.keyval == self.__key['space']:
            Logger().debug("MainController.__onKeyReleased(): 'space' key released")
            return True

        else:
            Logger().warning("MainController.__onKeyReleased(): unbind '%s' key" % event.keyval)

    #def __onWindowStateChanged(self, widget, event, *args):
        #Logger().debug("MainController.__onWindowStateChanged()")
        #if event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN:
            #self.__fullScreen = True
        #else:
            #self.__fullScreen = False

    def __onFileLoadPresetMenuitemActivate(self, widget):
        """
        @todo: make a custom dialog
        """
        Logger().trace("MainController.__onFileLoadPresetMenuitemActivate()")
        fileDialog = gtk.FileChooserDialog(title="Import Preset file", parent=self.dialog,
                                           action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                           buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.set_name("xml files")
        filter.add_pattern("*.xml")
        fileDialog.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("all files")
        filter.add_pattern("*")
        fileDialog.add_filter(filter)
        #fileDialog.set_current_folder_uri(config.HOME_DIR)
        fileDialog.set_filename(os.path.join(config.HOME_DIR, config.PRESET_FILE))
        response = fileDialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            presetFileName = fileDialog.get_filename()
            self.__importPresetFile(presetFileName)
        fileDialog.destroy()

    def __onFileLoadGtkrcMenuitemActivate(self, widget):
        Logger().trace("MainController.__onFileLoadGtkrcMenuitemActivate()")
        fileDialog = gtk.FileChooserDialog(title="Load Gtkrc file", parent=self.dialog,
                                           action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                           buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.set_name("all files")
        filter.add_pattern("*")
        fileDialog.add_filter(filter)
        #fileDialog.set_current_folder_uri(config.HOME_DIR)
        fileDialog.set_filename(os.path.join(config.HOME_DIR, config.GTKRC_FILE))
        response = fileDialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            gtkrcFileName = fileDialog.get_filename()
            Logger().debug("MainController.__onFileLoadGtkrcMenuitemActivate(): resources file=%s" % gtkrcFileName)
            gtk.rc_parse(gtkrcFileName)
            screen = self.dialog.get_screen()
            settings = gtk.settings_get_for_screen(screen)
            gtk.rc_reset_styles(settings)
        fileDialog.destroy()

    def __onHardwareConnectMenuitemToggled(self, widget):
        switch = self.hardwareConnectMenuitem.get_active()
        Logger().debug("MainController.__onHardwareConnectMenuitemToggled(%s)" % switch)
        if switch:
            self.__connectToHardware()
        else:
            self.__goToSimulationMode()

    def __onHardwareSetLimitYawMinusMenuitemActivate(self, widget):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('yaw', '-', yaw)
        Logger().debug("MainController.__onHardwareSetLimitYawMinusMenuitemActivate(): yaw minus limit set to %.1f" % yaw)
        self.setStatusbarMessage(_("Yaw - limit set"), 10)

    def __onHardwareSetLimitYawPlusMenuitemActivate(self, widget):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('yaw', '+', yaw)
        Logger().debug("MainController.__onHardwareSetLimitYawPlusMenuitemActivate(): yaw plus limit set to %.1f" % yaw)
        self.setStatusbarMessage(_("Yaw + limit set"), 10)

    def __onHardwareSetLimitPitchPlusMenuitemActivate(self, widget):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('pitch', '+', pitch)
        Logger().debug("MainController.__onHardwareSetLimitPitchPlusMenuitemActivate(): pitch plus limit set to %.1f" % pitch)
        self.setStatusbarMessage(_("Pitch + limit set"), 10)

    def __onHardwareSetLimitPitchMinusMenuitemActivate(self, widget):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('pitch', '-', pitch)
        Logger().debug("MainController.__onHardwareSetLimitPitchMinusMenuitemActivate(): pitch minus limit set to %.1f" % pitch)
        self.setStatusbarMessage(_("Pitch - limit set"), 10)

    def __onHardwareClearLimitsMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHardwareClearLimitsMenuitemActivate()")
        self._model.hardware.clearLimits()
        self.setStatusbarMessage(_("Limits cleared"), 10)

    def __onHelpManualMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHelpManualMenuitemActivate()")
        webbrowser.open(config.USER_GUIDE_URL)

    def __onHelpWhatsThisMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHelpWhatsThisMenuitemActivate()")
        Logger().warning("Not yet implemented")

    def __onHelpViewLogMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHelpViewLogMenuitemActivate()")
        controller = LoggerController(self, self._model, self._serializer)
        controller.setLogBuffer(self.__gtkLogStream)
        controller.run()
        controller.shutdown()

    def __onHelpAboutMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHelpAboutMenuitemActivate()")
        controller = HelpAboutController(self, self._model, self._serializer)
        controller.run()
        controller.shutdown()

    def __onModeMosaicRadiobuttonToggled(self, widget):
        Logger().trace("MainController.__onModeMosaicRadiobuttonToggled()")
        modeMosaic = self.modeMosaicRadiobutton.get_active()
        if modeMosaic and self._model.camera.lens.type_ == 'fisheye':
            WarningMessageController(_("Wrong shooting mode"),
                                     _("Can't set shooting mode to 'mosaic'\nwhile using 'fisheye' lens type"))
            self.modeMosaicRadiobutton.set_active(False)
            self.modePresetRadiobutton.set_active(True)
        elif modeMosaic and self._model.cameraOrientation == 'custom':
            WarningMessageController(_("Wrong camera orientation"),
                                     _("Can't set shooting mode to 'mosaic'\nwhile using 'custom' camera orientation"))
            self.modeMosaicRadiobutton.set_active(False)
            self.modePresetRadiobutton.set_active(True)
        else:
            self.mosaicFrame.set_sensitive(modeMosaic)
            self.presetFrame.set_sensitive(not modeMosaic)
            if modeMosaic:
                self._model.mode = 'mosaic'
            else:
                self._model.mode = 'preset'
            Logger().debug("MainController.__onModeMosaicRadiobuttonToggled(): shooting mode set to '%s'" % self._model.mode)
        self.refreshView()

    def __onSetYawStartButtonClicked(self, widget):
        Logger().trace("MainController.__onSetYawStartButtonClicked()")
        self._model.mosaic.yawStart = self.__yawPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Yaw start set from current position"), 10)

    def __onSetPitchStartButtonClicked(self, widget):
        Logger().trace("MainController.__onSetPitchStartButtonClicked()")
        self._model.mosaic.pitchStart = self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Pitch start set from current position"), 10)

    def __onSetYawEndButtonClicked(self, widget):
        Logger().trace("MainController.__onSetYawEndButtonClicked()")
        self._model.mosaic.yawEnd = self.__yawPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Yaw end set from current position"), 10)

    def __onSetPitchEndButtonClicked(self, widget):
        Logger().trace("MainController.__onSetEndPitchButtonClicked()")
        self._model.mosaic.pitchEnd = self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Pitch end set from current position"), 10)

    def __onSetStartButtonClicked(self, widget):
        Logger().trace("MainController.__onSetStartButtonClicked()")
        self.__setYawPitchStartPosition()

    def __onSetEndButtonClicked(self, widget):
        Logger().trace("MainController.__onSetEndButtonClicked()")
        self.__setYawPitchEndPosition()

    def __onTotalFovButtonClicked(self, widget):
        Logger().trace("MainController.__onTotalFovButtonClicked()")
        self.__openTotalFovDialog()

    def __onNbPictsButtonClicked(self, widget):
        Logger().trace("MainController.__onNbPictsButtonClicked()")
        self.__openNbPictsDialog()

    def __onPresetComboboxChanged(self, widget):
        presets = PresetManager().getPresets()
        try:
            preset = presets.getByIndex(self.presetCombobox.get_active())
            self._model.preset.name = preset.getName()
        except ValueError:
            #Logger().exception("MainController.__onPresetComboboxChanged()", debug=True)
            pass

    def __onPresetInfoButtonClicked(self, widget):
        Logger().trace("MainController.__onPresetInfoButtonClicked()")
        controller = PresetInfoController(self, self._model, self._serializer)
        controller.run()
        controller.shutdown()

    def __onHardwareSetOriginButtonClicked(self, widget):
        Logger().trace("MainController.onHardwareSetOriginButtonClicked()")
        Logger().info("Set hardware origin")
        self._model.hardware.setOrigin()
        self.setStatusbarMessage(_("Origin set at current position"), 10)

    def __onYawMovePlusTogglebuttonPressed(self, widget):
        Logger().trace("MainController.__yawMovePlusTogglebuttonPressed()")
        self._model.hardware.startAxis('yaw', '+')

    def __onYawMovePlusTogglebuttonReleased(self, widget):
        Logger().trace("MainController.__yawMovePlusTogglebuttonReleased()")
        self._model.hardware.stopAxis('yaw')
        self._model.hardware.waitStopAxis('yaw')
        self.yawMovePlusTogglebutton.set_active(False)
        self.refreshView()

    def __onPitchMovePlusTogglebuttonPressed(self, widget):
        Logger().trace("MainController.__pitchMovePlusTogglebuttonPressed()")
        self._model.hardware.startAxis('pitch', '+')

    def __onPitchMovePlusTogglebuttonReleased(self, widget):
        Logger().trace("MainController.__pitchMovePlusTogglebuttonReleased()")
        self._model.hardware.stopAxis('pitch')
        self._model.hardware.waitStopAxis('pitch')
        self.pitchMovePlusTogglebutton.set_active(False)
        self.refreshView()

    def __onPitchMoveMinusTogglebuttonPressed(self, widget):
        Logger().trace("MainController.__onPitchMoveMinusTogglebuttonPressed()")
        self._model.hardware.startAxis('pitch', '-')

    def __onPitchMoveMinusTogglebuttonReleased(self, widget):
        Logger().trace("MainController.__onPitchMoveMinusTogglebuttonReleased()")
        self._model.hardware.stopAxis('pitch')
        self._model.hardware.waitStopAxis('pitch')
        self.pitchMoveMinusTogglebutton.set_active(False)
        self.refreshView()

    def __onYawMoveMinusTogglebuttonPressed(self, widget):
        Logger().trace("MainController.__onYawMoveMinusTogglebuttonPressed()")
        self._model.hardware.startAxis('yaw', '-')

    def __onYawMoveMinusTogglebuttonReleased(self, widget):
        Logger().trace("MainController.__onYawMoveMinusTogglebuttonReleased()")
        self._model.hardware.stopAxis('yaw')
        self._model.hardware.waitStopAxis('yaw')
        self.yawMoveMinusTogglebutton.set_active(False)
        self.refreshView()

    def __onConfigButtonClicked(self, widget):
        Logger().trace("MainController.__onConfigButtonClicked()")
        self.__openConfigDialog()

    def __onShootButtonClicked(self, widget):
        Logger().trace("MainController.__onShootButtonClicked()")
        self.__openShootdialog()

    def __switchToRealHardwareCallback(self, flag, message=""):
        Logger().debug("MainController.__switchToRealHardwareCallback(): flag=%s" % flag)
        self.__connectStatus = flag
        self.__connectErrorMessage = message
        self.__waitController.closeBanner()

    # Helpers
    def __setYawPitchStartPosition(self):
        """ Set yaw/pitch end from current position.
        """
        self._model.mosaic.yawStart, self._model.mosaic.pitchStart = self.__yawPos, self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Yaw/pitch start set from current position"), 10)

    def __setYawPitchEndPosition(self):
        """ Set yaw/pitch start from current position.
        """
        self._model.mosaic.yawEnd, self._model.mosaic.pitchEnd = self.__yawPos, self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Yaw/pitch end set from current position"), 10)

    def __openTotalFovDialog(self):
        """
        """
        controller = TotalFovController(self, self._model)
        response = controller.run()
        controller.shutdown()
        if response == 0:
            self.__mosaicInputParam = 'fov'
            self.refreshView()
            self.setStatusbarMessage(_("Field of view set to user value"), 10)

    def __openNbPictsDialog(self):
        """
        """
        controller = NbPictsController(self, self._model)
        response = controller.run()
        controller.shutdown()
        if response == 0:
            self.__mosaicInputParam = 'nbPicts'
            self.refreshView()
            self.setStatusbarMessage(_("Number of pictures set to user value"), 10)

    def __openConfigDialog(self):
        """
        """
        self.setStatusbarMessage(_("Opening configuration dialog. Please wait..."))
        while gtk.events_pending():
            gtk.main_iteration()
        controller = ConfigController(self, self._model, self._serializer)
        self.setStatusbarMessage()
        response = controller.run()
        controller.shutdown()
        if response == 0:
            Logger().setLevel(ConfigManager().get('Preferences', 'LOGGER_LEVEL'))
            if self.__mosaicInputParam == 'startEnd':
                pass
            elif self.__mosaicInputParam == 'fov':
                yawFov = float(self.yawFovLabel.get_text())
                pitchFov = float(self.pitchFovLabel.get_text())
                self._model.setStartEndFromFov(yawFov, pitchFov)
            elif self.__mosaicInputParam == 'nbPicts':
                yawNbPicts = int(self.yawNbPictsLabel.get_text())
                pitchNbPicts = int(self.pitchNbPictsLabel.get_text())
                self._model.setStartEndFromNbPicts(yawNbPicts, pitchNbPicts)
            self.refreshView()

    def __openShootdialog(self):
        """
        """
        self._model.setStepByStep(False)
        self.shootButton.set_sensitive(False)
        self.setStatusbarMessage(_("Opening shoot dialog. Please wait..."))
        while gtk.events_pending():
            gtk.main_iteration()
        controller = ShootController(self, self._model, self._serializer)
        if self.__fullScreen:
            controller.dialog.fullscreen()
        self.shootButton.set_sensitive(True)
        self.setStatusbarMessage()
        controller.run()

    def __populatePresetCombobox(self):
        """
        """
        self.presetCombobox.get_model().clear()
        presets = PresetManager().getPresets()
        i = 0
        while True:
            try:
                preset = presets.getByIndex(i)
                name = preset.getName()
                self.presetCombobox.append_text(name)
                i += 1
            except ValueError:
                #Logger().exception("MainController.__populatePresetCombobox()", debug=True)
                break

    def __importPresetFile(self, presetFileName):
        """ Importe the presets from given file.

        @param presetFileName: name of the preset xml file
        @type presetFileName: str
        """
        Logger().debug("MainController.__importPresetFile(): preset file=%s" % presetFileName)
        try:
            PresetManager().importPresetFile(presetFileName)
            self.__populatePresetCombobox()
            self.refreshView()
        except Exception, msg:
            Logger().exception("MainController.__importPresetFile()")
            ErrorMessageController(_("Can't import preset file"), str(msg))

    def __connectToHardware(self):
        """ Connect to real hardware.
        """
        def refreshProgressbar(progressbar):
            """ Refresh the progressbar in activity mode.

            Should be called by a timeout.
            """
            progressbar.pulse()
            return True

        Logger().info("Connecting to real hardware...")
        self.setStatusbarMessage(_("Connecting to real hardware..."))
        #self.hardwareConnectMenuitem.set_sensitive(False)

        # Open connection banner (todo: use real banner on Nokia). Make a special object
        self.__connectStatus = None
        self.__waitController = WaitController(self, self._model, self._serializer)
        self.__waitBanner = self.__waitController.dialog
        self.__waitBanner.show()

        # Launch connexion thread
        thread.start_new_thread(self._model.switchToRealHardware, ())

        # Wait for end of connection
        while self.__connectStatus is None:
            while gtk.events_pending():
                gtk.main_iteration()
            time.sleep(0.05)

        # Check connection status
        if self.__connectStatus:
            Spy().setRefreshRate(config.SPY_SLOW_REFRESH)
            self.connectImage.set_from_stock(gtk.STOCK_YES, 4)
            Logger().info("Now connected to real hardware")
            self.setStatusbarMessage(_("Now connected to real hardware"), 5)
        else:
            Logger().error("Can't connect to hardware\n%s" % self.__connectErrorMessage)
            ErrorMessageController(_("Can't connect to hardware"), self.__connectErrorMessage)
            self.hardwareConnectMenuitem.set_active(False)

        #self.hardwareConnectMenuitem.set_sensitive(True)

    def __goToSimulationMode(self):
        """ Connect to simulated hardware.
        """
        Logger().info("Go to simulation mode")
        self._model.switchToSimulatedHardware()
        Spy().setRefreshRate(config.SPY_FAST_REFRESH)
        self.connectImage.set_from_stock(gtk.STOCK_NO, 4)
        self.setStatusbarMessage(_("Now in simulation mode"), 5)

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
        self._serializer.addWork(self.refreshView)

    # Interface
    def setStatusbarMessage(self, message=None, delay=0):
        """ Display a message on the statusbar.

        @param message: message to display. If None, clear statusbar
        @type message: str

        @param delay: display message duration, in s (0 means forever)
        @type delay: int
        """
        self.statusbar.pop(self.statusbarContextId)
        if self.__statusbarTimeoutEventId is not None:
            gobject.source_remove(self.__statusbarTimeoutEventId)
        if message is not None:
            self.statusbar.push(self.statusbarContextId, message)
            if delay:
                self.__statusbarTimeoutEventId = gobject.timeout_add(delay * 1000, self.setStatusbarMessage)
            else:
                self.__statusbarTimeoutEventId = None

    def refreshView(self):
        if self._model.mode == 'mosaic':
            flag = True
        else:
            flag = False

        if self._model.mode == 'mosaic':
            self.modeMosaicRadiobutton.set_active(True)
            self.modePresetRadiobutton.set_active(False)
            self.mosaicFrame.set_sensitive(True)
            self.presetFrame.set_sensitive(False)
            self.setYawStartButtonLabel.set_label("%.1f" % self._model.mosaic.yawStart)
            self.setPitchStartButtonLabel.set_label("%.1f" % self._model.mosaic.pitchStart)
            self.setYawEndButtonLabel.set_label("%.1f" % self._model.mosaic.yawEnd)
            self.setPitchEndButtonLabel.set_label("%.1f" % self._model.mosaic.pitchEnd)
            self.yawFovLabel.set_text("%.1f" % self._model.mosaic.yawFov)
            self.pitchFovLabel.set_text("%.1f" % self._model.mosaic.pitchFov)
            self.yawNbPictsLabel.set_text("%d" % self._model.mosaic.yawNbPicts)
            self.pitchNbPictsLabel.set_text("%d" % self._model.mosaic.pitchNbPicts)
            self.yawRealOverlapLabel.set_text("%d" % int(round(100 * self._model.mosaic.yawRealOverlap)))
            self.pitchRealOverlapLabel.set_text("%d" % int(round(100 * self._model.mosaic.pitchRealOverlap)))
            self.yawResolutionLabel.set_text("%d" % round(self._model.mosaic.getYawResolution()))
            self.pitchResolutionLabel.set_text("%d" % round(self._model.mosaic.getPitchResolution()))
        else:
            self.modeMosaicRadiobutton.set_active(False)
            self.modePresetRadiobutton.set_active(True)
            self.mosaicFrame.set_sensitive(False)
            self.presetFrame.set_sensitive(True)
        presets = PresetManager().getPresets()
        try:
            self.presetCombobox.set_active(presets.nameToIndex(self._model.preset.name))
        except ValueError:
            Logger().warning("Previously selected '%s' preset not found" % self._model.preset.name)
            self.presetCombobox.set_active(0)

        self.yawHeadPosLabel.set_text("%.1f" % self.__yawPos)
        self.pitchHeadPosLabel.set_text("%.1f" % self.__pitchPos)
