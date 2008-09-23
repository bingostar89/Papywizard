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
from papywizard.controller.loggerController import LoggerController
from papywizard.controller.helpAboutController import HelpAboutController
from papywizard.controller.presetTemplateInfoController import PresetTemplateInfoController
from papywizard.controller.configController import ConfigController
from papywizard.controller.shootController import ShootController
from papywizard.controller.waitController import WaitController
from papywizard.controller.spy import Spy


class MainController(AbstractController):
    """ Main controller object.
    """
    def __init__(self, serializer, model, gtkLogStream):
        """ Init the controller.

        @param serializer: object used to serialize toolkit events
        @type serializer: {Serializer}
        """
        super(MainController, self).__init__(None, model)
        self.__serializer = serializer
        self.__gtkLogStream = gtkLogStream

        # Try to autoconnect to real hardware
        if ConfigManager().getBoolean('Hardware', 'AUTO_CONNECT'):
            self.hardwareConnectMenuitem.set_active(True)

    def _init(self):
        self._gladeFile = "mainWindow.glade"
        self._signalDict = {"on_quitMenuitem_activate": gtk.main_quit,
                            "on_hardwareConnectMenuitem_toggled": self.__onHardwareConnectMenuitemToggled,
                            "on_hardwareSetLimitYawMinusMenuitem_activate": self.__onHardwareSetLimitYawMinusMenuitemActivate,
                            "on_hardwareSetLimitYawPlusMenuitem_activate": self.__onHardwareSetLimitYawPlusMenuitemActivate,
                            "on_hardwareSetLimitPitchPlusMenuitem_activate": self.__onHardwareSetLimitPitchPlusMenuitemActivate,
                            "on_hardwareSetLimitPitchMinusMenuitem_activate": self.__onHardwareSetLimitPitchMinusMenuitemActivate,
                            "on_hardwareClearLimitsMenuitem_activate": self.__onHardwareClearLimitsMenuitemActivate,
                            "on_hardwareResetMenuitem_activate": self.__onHardwareResetMenuitemActivate,
                            "on_helpManualMenuitem_activate": self.__onHelpManualMenuitemActivate,
                            "on_helpWhatsThisMenuitem_activate": self.__onHelpWhatsThisMenuitemActivate,
                            "on_helpViewLogMenuitem_activate": self.__onHelpViewLogMenuitemActivate,
                            "on_helpAboutMenuitem_activate": self.__onHelpAboutMenuitemActivate,

                            "on_modeMosaicRadiobutton_toggled": self.__onModeMosaicRadiobuttonToggled,

                            "on_setYawStartButton_clicked": self.__onSetYawStartButtonClicked,
                            "on_setPitchStartButton_clicked": self.__onSetPitchStartButtonClicked,
                            "on_setYawEndButton_clicked": self.__onSetYawEndButtonClicked,
                            "on_setPitchEndButton_clicked": self.__onSetPitchEndButtonClicked,
                            "on_setStartTogglebutton_clicked": self.__onSetStartTogglebuttonClicked,
                            "on_setStartTogglebutton_released": self.__onSetStartTogglebuttonReleased,
                            "on_setEndTogglebutton_clicked": self.__onSetEndTogglebuttonClicked,
                            "on_setEndTogglebutton_released": self.__onSetEndTogglebuttonReleased,

                            "on_presetTemplateCombobox_changed": self.__onPresetTemplateComboboxChanged,
                            "on_presetTemplateInfoButton_clicked": self.__onPresetTemplateInfoButtonClicked,

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
                      'Return': gtk.keysyms.Return,
                      }

        # Nokia plateform stuff
        try:
            import hildon
            self.__key['Home'] = gtk.keysyms.F8
            self.__key['End'] = gtk.keysyms.F7
            self.window_in_fullscreen = False
        except ImportError:
            pass

        self.__yawPos = 0
        self.__pitchPos = 0

        self.__statusbarTimeoutEventId = None
        self.__connectStatus = None
        self.__connectErrorMessage = None

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
        self.yawFovLabel = self.wTree.get_widget("yawFovLabel")
        self.pitchFovLabel = self.wTree.get_widget("pitchFovLabel")
        self.yawNbPictsLabel = self.wTree.get_widget("yawNbPictsLabel")
        self.pitchNbPictsLabel = self.wTree.get_widget("pitchNbPictsLabel")
        self.yawRealOverlapLabel = self.wTree.get_widget("yawRealOverlapLabel")
        self.pitchRealOverlapLabel = self.wTree.get_widget("pitchRealOverlapLabel")
        self.presetFrame = self.wTree.get_widget("presetFrame")
        self.presetTemplateCombobox = self.wTree.get_widget("presetTemplateCombobox")
        listStore = gtk.ListStore(gobject.TYPE_STRING)
        self.presetTemplateCombobox.set_model(listStore)
        cell = gtk.CellRendererText()
        self.presetTemplateCombobox.pack_start(cell, True)
        #self.presetTemplateCombobox.add_attribute(cell, 'text', 0)
        presets = PresetManager().getPresets()
        i = 0
        while True:
            try:
                preset = presets.getByIndex(i)
                name = preset.getName()
                self.presetTemplateCombobox.append_text(name)
                i += 1
            except KeyError:
                break
        self.yawPosLabel = self.wTree.get_widget("yawPosLabel")
        self.pitchPosLabel = self.wTree.get_widget("pitchPosLabel")
        self.yawMovePlusTogglebutton = self.wTree.get_widget("yawMovePlusTogglebutton")
        self.pitchMovePlusTogglebutton = self.wTree.get_widget("pitchMovePlusTogglebutton")
        self.yawMoveMinusTogglebutton = self.wTree.get_widget("yawMoveMinusTogglebutton")
        self.pitchMoveMinusTogglebutton = self.wTree.get_widget("pitchMoveMinusTogglebutton")
        self.statusbar = self.wTree.get_widget("statusbar")
        self.statusbarContextId = self.statusbar.get_context_id("default")
        self.connectImage = self.wTree.get_widget("connectImage")

        # Font
        self.yawPosLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchPosLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.setYawStartButtonLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.setPitchStartButtonLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.setYawEndButtonLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.setPitchEndButtonLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawFovLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchFovLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawNbPictsLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchNbPictsLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.yawRealOverlapLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchRealOverlapLabel.modify_font(pango.FontDescription("Arial 10 Bold"))

        # Nokia plateform stuff
        try:
            import hildon

            self.app = hildon.Program()
            window = hildon.Window()
            window.set_title(self.dialog.get_title())
            self.window_in_fullscreen = False
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

    def _connectSignals(self):
        super(MainController, self)._connectSignals()

        self.dialog.connect("destroy", gtk.main_quit)
        self.dialog.connect("key-press-event", self.__onKeyPressed)
        self.dialog.connect("key-release-event", self.__onKeyReleased)
        #self.dialog.connect("window-state-event", self.__onWindowStateChanged)
        Spy().newPosSignal.connect(self.__refreshPos)
        self._model.switchToRealHardwareSignal.connect(self.__switchToRealHardwareCallback)

    # Callbacks
    def __onKeyPressed(self, widget, event, *args):
        Logger().trace("MainController.__onKeyPressed()")

        # 'FullScreen' key
        #if event.keyval == self.__key['FullScreen']:
            #if not self.__keyPressedDict['FullScreen']:
                #Logger().debug("MainController.__onKeyPressed(): 'FullScreen' key pressed")
                #if self.window_in_fullscreen:
                    #self.dialog.unfullscreen()
                #else:
                    #self.dialog.fullscreen()
                #self.__keyPressedDict['FullScreen'] = True
            #return True

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
                Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; store start position")
                self.__keyPressedDict['Home'] = True
                self.setStartTogglebutton.set_active(True)
                self._model.mosaic.yawStart, self._model.mosaic.pitchStart = self.__yawPos, self.__pitchPos
                self.refreshView()
            return True

        # 'End' key
        elif event.keyval == self.__key['End']:
            if not self.__keyPressedDict['End'] and not self.__keyPressedDict['Home'] and \
               not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; store end position")
                self.__keyPressedDict['End'] = True
                self.setEndTogglebutton.set_active(True)
                self._model.mosaic.yawEnd, self._model.mosaic.pitchEnd = self.__yawPos, self.__pitchPos
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
        #if event.keyval == self.__key['FullScreen']:
            #if self.__keyPressedDict['FullScreen']:
                #Logger().debug("MainController.__onKeyReleased(): 'FullScreen' key released")
                #self.__keyPressedDict['FullScreen'] = False
            #return True

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
                self.setStartTogglebutton.set_active(False)
            return True

        # 'End' key
        if event.keyval == self.__key['End']:
            if self.__keyPressedDict['End']:
                Logger().debug("MainController.__onKeyReleased(): 'End' key released")
                self.__keyPressedDict['End'] = False
                self.setEndTogglebutton.set_active(False)
            return True

        else:
            Logger().warning("MainController.__onKeyReleased(): unbind '%s' key" % event.keyval)

    #def __onWindowStateChanged(self, widget, event, *args):
        #Logger().debug("MainController.__onWindowStateChanged()")
        #if event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN:
            #self.window_in_fullscreen = True
        #else:
            #self.window_in_fullscreen = False

    def __onHardwareConnectMenuitemToggled(self, widget):
        switch = self.hardwareConnectMenuitem.get_active()
        Logger().trace("MainController.__onHardwareConnectMenuitemToggled(%s)" % switch)
        if switch:
            self.__connectToHardware()
        else:
            self.__goToSimulationMode()

    def __onHardwareSetLimitYawMinusMenuitemActivate(self, widget):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('yaw', '-', yaw)
        Logger().debug("MainController.__onHardwareSetLimitYawMinusMenuitemActivate() yaw minus limit set to %.1f" % yaw)
        self.setStatusbarMessage(_("Yaw - limit set"), 10)

    def __onHardwareSetLimitYawPlusMenuitemActivate(self, widget):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('yaw', '+', yaw)
        Logger().debug("MainController.__onHardwareSetLimitYawPlusMenuitemActivate(): yaw plus limit set to %.1f" % yaw)
        self.setStatusbarMessage(_("Yaw + limit set"), 10)

    def __onHardwareSetLimitPitchPlusMenuitemActivate(self, widget):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('pitch', '+', pitch)
        Logger().debug("MainController.__onHardwareSetLimitPitchPlusMenuitemActivate() pitch plus limit set to %.1f" % pitch)
        self.setStatusbarMessage(_("Pitch + limit set"), 10)

    def __onHardwareSetLimitPitchMinusMenuitemActivate(self, widget):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('pitch', '-', pitch)
        Logger().debug("MainController.__onHardwareSetLimitPitchMinusMenuitemActivate() pitch minus limit set to %.1f" % pitch)
        self.setStatusbarMessage(_("Pitch - limit set"), 10)

    def __onHardwareClearLimitsMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHardwareClearLimitsMenuitemActivate()")
        self._model.hardware.clearLimits()
        self.setStatusbarMessage(_("Limits cleared"), 10)

    def __onHardwareResetMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHardwareResetMenuitemActivate()")
        Logger().info("Reseting hardware")
        self._model.hardware.reset()
        self.setStatusbarMessage(_("Hardware has been reseted"), 10)

    def __onHelpManualMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHelpManualMenuitemActivate()")
        webbrowser.open(config.USER_GUIDE_URL)

    def __onHelpWhatsThisMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHelpWhatsThisMenuitemActivate()")
        Logger().warning("Not yet implemented")

    def __onHelpViewLogMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHelpViewLogMenuitemActivate()")
        controller = LoggerController(self)
        controller.setLogBuffer(self.__gtkLogStream)
        controller.run()
        controller.destroyView()

    def __onHelpAboutMenuitemActivate(self, widget):
        Logger().trace("MainController.__onHelpAboutMenuitemActivate()")
        helpAboutDialog = HelpAboutController(self)
        helpAboutDialog.run()
        helpAboutDialog.destroyView()

    def __onModeMosaicRadiobuttonToggled(self, widget):
        Logger().trace("MainController.__onModeMosaicRadiobuttonToggled()")
        modeMosaic = self.modeMosaicRadiobutton.get_active()
        self.mosaicFrame.set_sensitive(modeMosaic)
        self.presetFrame.set_sensitive(not modeMosaic)
        if modeMosaic:
            self._model.mode = 'mosaic'
        else:
            self._model.mode = 'preset'
        Logger().debug("MainController.__onModeMosaicRadiobuttonToggled(): shooting mode set to '%s'" % self._model.mode)

    def __onSetYawStartButtonClicked(self, widget):
        Logger().trace("MainController.__onSetYawStartButtonClicked()")
        self._model.mosaic.yawStart = self.__yawPos
        self.refreshView()
        self.setStatusbarMessage("Yaw start set from current position", 10)

    def __onSetPitchStartButtonClicked(self, widget):
        Logger().trace("MainController.__onSetPitchStartButtonClicked()")
        self._model.mosaic.pitchStart = self.__pitchPos
        self.refreshView()
        self.setStatusbarMessage("Pitch start set from current position", 10)

    def __onSetYawEndButtonClicked(self, widget):
        Logger().trace("MainController.__onSetYawEndButtonClicked()")
        self._model.mosaic.yawEnd = self.__yawPos
        self.refreshView()
        self.setStatusbarMessage("Yaw end set from current position", 10)

    def __onSetPitchEndButtonClicked(self, widget):
        Logger().trace("MainController.__onSetEndPitchButtonClicked()")
        self._model.mosaic.pitchEnd = self.__pitchPos
        self.refreshView()
        self.setStatusbarMessage("Pitch end set from current position", 10)

    def __onSetStartTogglebuttonClicked(self, widget):
        Logger().trace("MainController.__onSetStartTogglebuttonClicked()")
        self._model.mosaic.yawStart, self._model.mosaic.pitchStart = self.__yawPos, self.__pitchPos
        self.refreshView()
        self.setStatusbarMessage("Yaw/pitch start set from current position", 10)

    def __onSetStartTogglebuttonReleased(self, widget):
        Logger().trace("MainController.__onSetStartTogglebuttonReleased()")
        self.setStartTogglebutton.set_active(False)

    def __onSetEndTogglebuttonClicked(self, widget):
        Logger().trace("MainController.__onSetEndTogglebuttonClicked()")
        self._model.mosaic.yawEnd, self._model.mosaic.pitchEnd = self.__yawPos, self.__pitchPos
        self.refreshView()
        self.setStatusbarMessage("Yaw/pitch end position set from current position", 10)

    def __onSetEndTogglebuttonReleased(self, widget):
        Logger().trace("MainController.__onSetEndTogglebuttonReleased()")
        self.setEndTogglebutton.set_active(False)

    def __onPresetTemplateComboboxChanged(self, widget):
        presets = PresetManager().getPresets()
        preset = presets.getByIndex(self.presetTemplateCombobox.get_active())
        self._model.preset.template = preset.getName()
        tooltip = preset.getTooltip()
        self.presetTemplateCombobox.set_tooltip_text(tooltip)
        Logger().debug("MainController.__onPresetTemplateComboboxChanged(): new preset template='%s'" % self._model.preset.template)

    def __onPresetTemplateInfoButtonClicked(self, widget):
        Logger().trace("MainController.__onPresetTemplateInfoButtonClicked()")
        controller = PresetTemplateInfoController(self)
        controller.run()
        controller.destroyView()

    def __onHardwareSetOriginButtonClicked(self, widget):
        Logger().trace("MainController.onHardwareSetOriginButtonClicked()")
        Logger().info("Set hardware origin")
        self._model.hardware.setOrigin()
        self.setStatusbarMessage("Origin set at current position", 10)

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

    def __openConfigDialog(self):
        controller = ConfigController(self, self._model)
        response = controller.run()
        controller.destroyView()
        if response == 0:
            Logger().setLevel(ConfigManager().get('Logger', 'LOGGER_LEVEL'))
            self.refreshView()

    def __onConfigButtonClicked(self, widget):
        Logger().trace("MainController.__onConfigButtonClicked()")
        self.__openConfigDialog()

    def __openShootdialog(self):
        self._model.initProgress()
        controller = ShootController(self, self._model)
        controller.run()
        controller.destroyView()

    def __onShootButtonClicked(self, widget):
        Logger().trace("MainController.__onShootButtonClicked()")
        self.__openShootdialog()

    def __switchToRealHardwareCallback(self, flag, message=""):
        Logger().debug("MainController.__switchToRealHardwareCallback(): flag=%s" % flag)
        self.__connectStatus = flag
        self.__connectErrorMessage = message
        self.__waitController.closeBanner()

    # Real work
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
        self.__waitController = WaitController(self, self._model)
        self.__waitBanner = self.__waitController.waitBanner
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
            messageDialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
                                              message_format=_("Can't connect to hardware"))
            messageDialog.set_title(_("Error"))
            messageDialog.format_secondary_text(self.__connectErrorMessage)
            messageDialog.run()
            messageDialog.destroy()
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
        self.__serializer.apply(self.refreshView)

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
        self.modeMosaicRadiobutton.set_active(flag)
        self.modePresetRadiobutton.set_active(not flag)
        self.mosaicFrame.set_sensitive(flag)
        self.presetFrame.set_sensitive(not flag)
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
        presets = PresetManager().getPresets()
        try:
            self.presetTemplateCombobox.set_active(presets.nameToIndex(self._model.preset.template))
        except KeyError:
            Logger().warning("Previously selected '%s' preset template not found" % self._model.preset.template)
            self.presetTemplateCombobox.set_active(0)

        self.yawPosLabel.set_text("%.1f" % self.__yawPos)
        self.pitchPosLabel.set_text("%.1f" % self.__pitchPos)
