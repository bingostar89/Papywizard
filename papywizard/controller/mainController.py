# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2009 Frédéric Mantegazza

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
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import thread
import os.path
import webbrowser
import types

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.presetManager import PresetManager
from papywizard.common.exception import HardwareError
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.messageController import ErrorMessageController, WarningMessageController, \
                                                    YesNoMessageController, ExceptionMessageController
from papywizard.controller.loggerController import LoggerController
from papywizard.controller.helpAboutController import HelpAboutController
from papywizard.controller.totalFovController import TotalFovController
from papywizard.controller.nbPictsController import NbPictsController
from papywizard.controller.configController import ConfigController
from papywizard.controller.shootController import ShootController
from papywizard.controller.spy import Spy


class MainController(AbstractController):
    """ Main controller object.
    """
    def __init__(self, model, serializer, logStream):
        """ Init the controller.

        @param serializer: object used to serialize toolkit events
        @type serializer: {Serializer}
        """
        super(MainController, self).__init__(None, model, serializer)
        self.__logStream = logStream

        # Try to autoconnect to real hardware
        if ConfigManager().getBoolean('Preferences', 'HARDWARE_AUTO_CONNECT'):
            self.hardwareConnect.setChecked(True)

    def _init(self):
        self._uiFile = "mainWindow.ui"

        self.__keyPressedDict = {'FullScreen': False,
                                 'Right': False,
                                 'Left': False,
                                 'Up': False,
                                 'Down': False,
                                 'Home': False,
                                 'End': False,
                                 'Tab': False,
                                 'space': False,
                                 'Return': False,
                                 'Escape': False,
                             }
        self.__key = {'FullScreen': QtCore.Qt.Key_F6,
                      'Right': QtCore.Qt.Key_Right,
                      'Left': QtCore.Qt.Key_Left,
                      'Up': QtCore.Qt.Key_Up,
                      'Down': QtCore.Qt.Key_Down,
                      'Home': QtCore.Qt.Key_Home,
                      'End': QtCore.Qt.Key_End,
                      'Tab': QtCore.Qt.Key_Tab,
                      'space': QtCore.Qt.Key_Space,
                      'Return': QtCore.Qt.Key_Return,
                      'Escape': QtCore.Qt.Key_Escape,
                      }

        self.__yawPos = 0
        self.__pitchPos = 0
        self.__connectStatus = None
        self.__connectErrorMessage = None
        self.__mosaicInputParam = 'startEnd'
        self.__manualSpeed = 'normal'

    def _initWidgets(self):
        def hasHeightForWidth(self):
            return True

        def heightForWidth(self, width):
            return width

        # Status bar
        # Manual speed
        self._view.manualSpeedLabel = QtGui.QLabel()
        self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_fwd.png").scaled(22, 22))
        self._view.statusBar().addPermanentWidget(self._view.manualSpeedLabel)

        # Connect button
        self._view.connectLabel = QtGui.QLabel()
        self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_no.png").scaled(22, 22))
        self._view.statusBar().addPermanentWidget(self._view.connectLabel)
        
        # Presets
        self.__populatePresetComboBox()

        # Force arrows layout as square (does not work)
        self._view.moveArrowsGridLayout.heightForWidth = types.MethodType(heightForWidth, self._view.moveArrowsGridLayout)
        self._view.moveArrowsGridLayout.hasHeightForWidth = types.MethodType(hasHeightForWidth, self._view.moveArrowsGridLayout)

        # Disable 'timelapse' tab
        self._view.tabWidget.setTabEnabled(2, False)
        
        # Keyboard behaviour
        self._view.grabKeyboard()

        if self.__fullScreen:
            self._view.setWindowState(self._view.windowState() | QtCore.Qt.WindowFullScreen)

        self._view.show()

    def _connectQtSignals(self):
        super(MainController, self)._connectQtSignals()

        # Menus
        QtCore.QObject.connect(self._view.actionFileLoadPreset, QtCore.SIGNAL("activated()"), self.__onActionFileLoadPresetActivated)
        #"on_fileLoadGtkrc_activate": self.__onFileLoadGtkrcActivate,
        #"on_quit_activate": gtk.main_quit,

        QtCore.QObject.connect(self._view.actionHardwareConnect, QtCore.SIGNAL("toggled(bool)"), self.__onActionHardwareConnectToggled)
        QtCore.QObject.connect(self._view.actionHardwareSetLimitYawMinus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitYawMinusActivated)
        QtCore.QObject.connect(self._view.actionHardwareSetLimitYawPlus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitYawPlusActivated)
        QtCore.QObject.connect(self._view.actionHardwareSetLimitPitchPlus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitPitchPlusActivated)
        QtCore.QObject.connect(self._view.actionHardwareSetLimitPitchMinus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitPitchMinusActivated)
        QtCore.QObject.connect(self._view.actionHardwareClearLimits, QtCore.SIGNAL("activated()"), self.__onActionHardwareClearLimitsActivated)
        QtCore.QObject.connect(self._view.actionHelpManual, QtCore.SIGNAL("activated()"), self.__onActionHelpManualActivated)
        QtCore.QObject.connect(self._view.actionHelpViewLog, QtCore.SIGNAL("activated()"), self.__onActionHelpViewLogActivated)
        QtCore.QObject.connect(self._view.actionHelpAboutPapywizard, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutPapywizardActivated)
        QtCore.QObject.connect(self._view.actionHelpAboutQt, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutQtActivated)

        # Widgets
        QtCore.QObject.connect(self._view.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.__onTabWidgetCurrentChanged)

        QtCore.QObject.connect(self._view.setYawStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawStartPushButtonClicked)
        QtCore.QObject.connect(self._view.setPitchStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchStartPushButtonClicked)
        QtCore.QObject.connect(self._view.setYawEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawEndPushButtonClicked)
        QtCore.QObject.connect(self._view.setPitchEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchEndPushButtonClicked)
        QtCore.QObject.connect(self._view.setStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetStartPushButtonClicked)
        QtCore.QObject.connect(self._view.setEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetEndPushButtonClicked)
        QtCore.QObject.connect(self._view.totalFovPushButton, QtCore.SIGNAL("clicked()"), self.__onTotalFovPushButtonClicked)
        QtCore.QObject.connect(self._view.nbPictsPushButton, QtCore.SIGNAL("clicked()"), self.__onNbPictsPushButtonClicked)

        QtCore.QObject.connect(self._view.presetComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onPresetComboBoxCurrentIndexChanged)

        QtCore.QObject.connect(self._view.setOriginToolButton, QtCore.SIGNAL("clicked()"), self.__onetOriginToolButtonClicked)
        QtCore.QObject.connect(self._view.yawMovePlusToolButton, QtCore.SIGNAL("pressed()"), self.__onYawMovePlusToolButtonPressed)
        QtCore.QObject.connect(self._view.yawMovePlusToolButton, QtCore.SIGNAL("released()"), self.__onYawMovePlusToolButtonReleased)
        QtCore.QObject.connect(self._view.pitchMovePlusToolButton, QtCore.SIGNAL("pressed()"), self.__onPitchMovePlusToolButtonPressed)
        QtCore.QObject.connect(self._view.pitchMovePlusToolButton, QtCore.SIGNAL("released()"), self.__onPitchMovePlusToolButtonReleased)
        QtCore.QObject.connect(self._view.yawMoveMinusToolButton, QtCore.SIGNAL("pressed()"), self.__onYawMoveMinusToolButtonPressed)
        QtCore.QObject.connect(self._view.yawMoveMinusToolButton, QtCore.SIGNAL("released()"), self.__onYawMoveMinusToolButtonReleased)
        QtCore.QObject.connect(self._view.pitchMoveMinusToolButton, QtCore.SIGNAL("pressed()"), self.__onPitchMoveMinusToolButtonPressed)
        QtCore.QObject.connect(self._view.pitchMoveMinusToolButton, QtCore.SIGNAL("released()"), self.__onPitchMoveMinusToolButtonReleased)

        QtCore.QObject.connect(self._view.configPushButton, QtCore.SIGNAL("clicked()"), self.__onConfigPushButtonClicked)
        QtCore.QObject.connect(self._view.shootPushButton, QtCore.SIGNAL("clicked()"), self.__onShootPushButtonClicked)

        self._view.keyPressEvent = self.__onKeyPressed
        self._view.keyReleaseEvent = self.__onKeyReleased

    def _connectSignals(self):
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
    def _onDelete(self, widget, event):
        Logger().trace("MainController._onDelete()")
        QtGui.QApplication.quit()

    def __onKeyPressed(self, event):
        Logger().trace("MainController.__onKeyPressed()")

        # 'FullScreen' key
        if event.key() == self.__key['FullScreen']:
            if not self.__keyPressedDict['FullScreen']:
                Logger().debug("MainController.__onKeyPressed(): 'FullScreen' key pressed")
                if self.__fullScreen:
                    Logger().debug("MainController.__onKeyPressed(): switch to fullscreen")
                    self._view.setWindowState(self._view.windowState() & ~QtCore.Qt.WindowFullScreen)
                    self.__fullScreen = False
                else:
                    Logger().debug("MainController.__onKeyPressed(): switch to normal")
                    self._view.setWindowState(self._view.windowState() | QtCore.Qt.WindowFullScreen)
                    self.__fullScreen = True
                self.__keyPressedDict['FullScreen'] = True
            return

        # 'Right' key
        if event.key() == self.__key['Right']:
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyPressed(): 'Right' key pressed; start 'yaw' axis dir '+'")
                self.__keyPressedDict['Right'] = True
                self._view.yawMovePlusToolButton.setDown(True)
                self._model.hardware.startAxis('yaw', '+')
            return

        # 'Left' key
        elif event.key() == self.__key['Left']:
            if not self.__keyPressedDict['Left'] and not self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyPressed(): 'Left' key pressed; start 'yaw' axis dir '-'")
                self.__keyPressedDict['Left'] = True
                self._view.yawMoveMinusToolButton.setDown(True)
                self._model.hardware.startAxis('yaw', '-')
            return

        # 'Up' key
        elif event.key() == self.__key['Up']:
            if not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyPressed(): 'Up' key pressed; start 'pitch' axis dir '+'")
                self.__keyPressedDict['Up'] = True
                self._view.pitchMovePlusToolButton.setDown(True)
                self._model.hardware.startAxis('pitch', '+')
            return

        # 'Down' key
        elif event.key() == self.__key['Down']:
            if not self.__keyPressedDict['Down'] and not self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyPressed(): 'Down' key pressed; start 'pitch' axis dir '-'")
                self.__keyPressedDict['Down'] = True
                self._view.pitchMoveMinusToolButton.setDown(True)
                self._model.hardware.startAxis('pitch', '-')
            return

        # 'Home' key
        elif event.key() == self.__key['Home']:
            if not self.__keyPressedDict['Home'] and \
               not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                self.__keyPressedDict['Home'] = True
                if self.__manualSpeed == 'normal':
                    self.__manualSpeed = 'slow'
                    Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; select slow speed")
                    self._model.hardware.setManualSpeed('slow')
                    self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_play.png").scaled(22, 22))
                    self.setStatusbarMessage(_("Manual speed set to slow"), 10)
                elif self.__manualSpeed == 'fast':
                    self.__manualSpeed = 'normal'
                    Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; select normal speed")
                    self._model.hardware.setManualSpeed('normal')
                    self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_fwd.png").scaled(22, 22))
                    self.setStatusbarMessage(_("Manual speed set to normal"), 10)
            return

        # 'End' key
        elif event.key() == self.__key['End']:
            if not self.__keyPressedDict['End'] and not self.__keyPressedDict['Home'] and \
               not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                self.__keyPressedDict['End'] = True
                if self.__manualSpeed == 'slow':
                    self.__manualSpeed = 'normal'
                    Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; select normal speed")
                    self._model.hardware.setManualSpeed('normal')
                    self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_fwd.png").scaled(22, 22))
                    self.setStatusbarMessage(_("Manual speed set to normal"), 10)
                elif self.__manualSpeed == 'normal':
                    controller = WarningMessageController(_("Fast manual speed"),
                                                          _("Manual speed set to 'fast'\nThis can be dangerous for the hardware!"))
                    self._view.releaseKeyboard()
                    controller.exec_()
                    self._view.grabKeyboard()
                    controller.shutdown()
                    self.__manualSpeed = 'fast'
                    Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; select fast speed")
                    self._model.hardware.setManualSpeed('fast')
                    self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/messagebox_warning.png").scaled(22, 22))
                    self.setStatusbarMessage(_("Manual speed set to fast"), 10)
            return

        ## 'Tab' key
        #elif event.key() == self.__key['Tab']:
            #if not self.__keyPressedDict['Tab']:
                #Logger().debug("MainController.__onKeyPressed(): 'Tab' key pressed; blocked")
                #self.__keyPressedDict['Tab'] = True
            #return

        ## 'space' key
        #elif event.key() == self.__key['space']:
            #if not self.__keyPressedDict['space']:
                #Logger().debug("MainController.__onKeyPressed(): 'space' key pressed; blocked")
                #self.__keyPressedDict['space'] = True
            #return

        # 'Return' key
        elif event.key() == self.__key['Return']:
            if not self.__keyPressedDict['Return']:
                Logger().debug("MainController.__onKeyPressed(): 'Return' key pressed; open shoot dialog")
                self.__keyPressedDict['Return'] = True
            self.__openShootdialog()
            return

        # 'Escape' key
        elif event.key() == self.__key['Escape']:
            if not self.__keyPressedDict['Escape']:
                Logger().debug("MainController.__onKeyPressed(): 'Escape' key pressed")
                self.__keyPressedDict['Escape'] = True
            controller = YesNoMessageController(_("About to Quit"),
                                                _("Are you sure you want to quit Papywizard?"))
            self._view.releaseKeyboard()
            response = controller.exec_()
            self._view.grabKeyboard()
            controller.shutdown()
            if response == QtGui.QMessageBox.Yes:
                QtGui.QApplication.quit()
            return

        else:
            Logger().warning("MainController.__onKeyPressed(): unbind '%s' key" % event.key())
            #self._view.keyPressEvent(event)

    def __onKeyReleased(self, event):
        Logger().trace("MainController.__onKeyReleased()")

        # 'FullScreen' key
        if event.key() == self.__key['FullScreen']:
            if self.__keyPressedDict['FullScreen']:
                Logger().debug("MainController.__onKeyReleased(): 'FullScreen' key released")
                self.__keyPressedDict['FullScreen'] = False
            return

        # 'Right' key
        if event.key() == self.__key['Right']:
            if self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyReleased(): 'Right' key released; stop 'yaw' axis")
                self._model.hardware.stopAxis('yaw')
                self._model.hardware.waitStopAxis('yaw')
                self.__keyPressedDict['Right'] = False
                self._view.yawMovePlusToolButton.setDown(False)
            return

        # 'Left' key
        elif event.key() == self.__key['Left']:
            if self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyReleased(): 'Left' key released; stop 'yaw' axis")
                self._model.hardware.stopAxis('yaw')
                self._model.hardware.waitStopAxis('yaw')
                self.__keyPressedDict['Left'] = False
                self._view.yawMoveMinusToolButton.setDown(False)
            return

        # 'Up' key
        elif event.key() == self.__key['Up']:
            if self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyReleased(): 'Up' key released; stop 'pitch' axis")
                self._model.hardware.stopAxis('pitch')
                self._model.hardware.waitStopAxis('pitch')
                self.__keyPressedDict['Up'] = False
                self._view.pitchMovePlusToolButton.setDown(False)
            return

        # 'Down' key
        elif event.key() == self.__key['Down']:
            if self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyReleased(): 'Down' key released; stop 'pitch' axis")
                self._model.hardware.stopAxis('pitch')
                self._model.hardware.waitStopAxis('pitch')
                self.__keyPressedDict['Down'] = False
                self._view.pitchMoveMinusToolButton.setDown(False)
            return

        # 'Home' key
        elif event.key() == self.__key['Home']:
            if self.__keyPressedDict['Home']:
                Logger().debug("MainController.__onKeyReleased(): 'Home' key released")
                self.__keyPressedDict['Home'] = False
            return

        # 'End' key
        elif event.key() == self.__key['End']:
            if self.__keyPressedDict['End']:
                Logger().debug("MainController.__onKeyReleased(): 'End' key released")
                self.__keyPressedDict['End'] = False
            return

        ## 'Tab' key
        #elif event.key() == self.__key['Tab']:
            #if self.__keyPressedDict['Tab']:
                #Logger().debug("MainController.__onKeyReleased(): 'Tab' key released")
                #self.__keyPressedDict['Tab'] = False
            #return

        ## 'space' key
        #elif event.key() == self.__key['space']:
            #if self.__keyPressedDict['space']:
                #Logger().debug("MainController.__onKeyReleased(): 'space' key released")
                #self.__keyPressedDict['space'] = False
            #return

        # 'Escape' key
        elif event.key() == self.__key['Escape']:
            if self.__keyPressedDict['Escape']:
                Logger().debug("MainController.__onKeyReleased(): 'Escape' key released")
                self.__keyPressedDict['Escape'] = False
            return

        else:
            Logger().warning("MainController.__onKeyReleased(): unbind '%s' key" % event.key())
            #self._view.keyPressEvent(event)
            print self._view.__class__.__base__
            self._view.__class__.__base__.keyPressEvent(event)

    def __onActionFileLoadPresetActivated(self):
        Logger().trace("MainController.__onActionFileLoadPresetActivated()")
        fileName =  QtGui.QFileDialog.getOpenFileName(self._view,
                                                      _("Load Preset file"),
                                                      os.path.join(config.HOME_DIR, config.PRESET_FILE),
                                                      _("XML files (*.xml);;All files (*)"))
        if fileName:
            self.__importPresetFile(fileName)

    def __onActionHardwareConnectToggled(self, checked):
        Logger().debug("MainController.__onActionHardwareConnectToggled(%s)" % checked)
        if checked:
            self.__connectToHardware()
        else:
            self.__goToSimulationMode()

    def __onActionHardwareSetLimitYawMinusActivated(self):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('yaw', '-', yaw)
        Logger().debug("MainController.__onActionHardwareSetLimitYawMinusActivated(): yaw minus limit set to %.1f" % yaw)
        self.setStatusbarMessage(_("Yaw - limit set"), 10)

    def __onActionHardwareSetLimitYawPlusActivated(self):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('yaw', '+', yaw)
        Logger().debug("MainController.__onActionHardwareSetLimitYawPlusActivated(): yaw plus limit set to %.1f" % yaw)
        self.setStatusbarMessage(_("Yaw + limit set"), 10)

    def __onActionHardwareSetLimitPitchPlusActivated(self):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('pitch', '+', pitch)
        Logger().debug("MainController.__onActionHardwareSetLimitPitchPlusActivated(): pitch plus limit set to %.1f" % pitch)
        self.setStatusbarMessage(_("Pitch + limit set"), 10)

    def __onActionHardwareSetLimitPitchMinusActivated(self):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('pitch', '-', pitch)
        Logger().debug("MainController.__onActionHardwareSetLimitPitchMinusActivated(): pitch minus limit set to %.1f" % pitch)
        self.setStatusbarMessage(_("Pitch - limit set"), 10)

    def __onActionHardwareClearLimitsActivated(self):
        Logger().trace("MainController.__onActionHardwareClearLimitsActivated()")
        self._model.hardware.clearLimits()
        self.setStatusbarMessage(_("Limits cleared"), 10)

    def __onActionHelpManualActivated(self):
        Logger().trace("MainController.__onActionHelpManualActivated()")
        webbrowser.open(config.USER_GUIDE_URL)

    def __onActionHelpWhatsThisActivated(self):
        Logger().trace("MainController.__onActionHelpWhatsThisActivated()")
        Logger().warning("Not yet implemented")

    def __onActionHelpViewLogActivated(self):
        Logger().trace("MainController.__onActionHelpViewLogActivated()")
        controller = LoggerController(self, self._model, self._serializer)
        controller.appendHtml(self.__logStream.getHtml())
        self._view.releaseKeyboard()
        controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()

    def __onActionHelpAboutPapywizardActivated(self):
        Logger().trace("MainController.__onActionHelpAboutPapywizardActivated()")
        controller = HelpAboutController(self, self._model, self._serializer)
        self._view.releaseKeyboard()
        controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()

    def __onActionHelpAboutQtActivated(self):
        Logger().trace("MainController.__onActionHelpAboutQtActivated()")
        QtGui.QMessageBox.aboutQt(self._view)

    def __onTabWidgetCurrentChanged(self, index):
        Logger().trace("MainController.__onTabWidgetCurrentChanged()")
        if index == 0:
            self._model.mode = 'mosaic'
        elif index == 1:
            self._model.mode = 'preset'
        else:
            Logger().warning("MainController.__onTabWidgetCurrentChanged(): 'timelapse' shooting mode not yet available")
        Logger().debug("MainController.__onTabWidgetCurrentChanged(): shooting mode set to '%s'" % self._model.mode)

    def __onSetYawStartPushButtonClicked(self):
        Logger().trace("MainController.__onSetYawStartPushButtonClicked()")
        self._model.mosaic.yawStart = self.__yawPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Yaw start set from current position"), 10)

    def __onSetPitchStartPushButtonClicked(self):
        Logger().trace("MainController.__onSetPitchStartPushButtonClicked()")
        self._model.mosaic.pitchStart = self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Pitch start set from current position"), 10)

    def __onSetYawEndPushButtonClicked(self):
        Logger().trace("MainController.__onSetYawEndPushButtonClicked()")
        self._model.mosaic.yawEnd = self.__yawPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Yaw end set from current position"), 10)

    def __onSetPitchEndPushButtonClicked(self):
        Logger().trace("MainController.__onSetEndPitchButtonClicked()")
        self._model.mosaic.pitchEnd = self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(_("Pitch end set from current position"), 10)

    def __onSetStartPushButtonClicked(self):
        Logger().trace("MainController.__onSetStartPushButtonClicked()")
        self.__setYawPitchStartPosition()

    def __onSetEndPushButtonClicked(self):
        Logger().trace("MainController.__onSetEndPushButtonClicked()")
        self.__setYawPitchEndPosition()

    def __onTotalFovPushButtonClicked(self):
        Logger().trace("MainController.__onTotalFovPushButtonClicked()")
        self.__openTotalFovDialog()

    def __onNbPictsPushButtonClicked(self):
        Logger().trace("MainController.__onNbPictsPushButtonClicked()")
        self.__openNbPictsDialog()

    def __onPresetComboBoxCurrentIndexChanged(self, widget):
        presets = PresetManager().getPresets()
        try:
            preset = presets.getByIndex(self._view.presetComboBox.currentIndex())
            self._model.preset.name = preset.getName()
            self.refreshView()
        except ValueError:
            #Logger().exception("MainController.__onPresetComboBoxCurrentIndexChanged()", debug=True)
            pass

    def __onetOriginToolButtonClicked(self):
        Logger().trace("MainController.onHardwareSetOriginButtonClicked()")
        Logger().info("Set hardware origin")
        self._model.hardware.setOrigin()
        self.setStatusbarMessage(_("Origin set at current position"), 10)

    def __onYawMovePlusToolButtonPressed(self):
        Logger().trace("MainController.__yawMovePlusToolButtonPressed()")
        self._model.hardware.startAxis('yaw', '+')

    def __onYawMovePlusToolButtonReleased(self):
        Logger().trace("MainController.__yawMovePlusToolButtonReleased()")
        self._model.hardware.stopAxis('yaw')
        self._model.hardware.waitStopAxis('yaw')
        #self._view.yawMovePlusToolButton.setDown(False)
        self.refreshView()

    def __onPitchMovePlusToolButtonPressed(self):
        Logger().trace("MainController.__pitchMovePlusToolButtonPressed()")
        self._model.hardware.startAxis('pitch', '+')

    def __onPitchMovePlusToolButtonReleased(self):
        Logger().trace("MainController.__pitchMovePlusToolButtonReleased()")
        self._model.hardware.stopAxis('pitch')
        self._model.hardware.waitStopAxis('pitch')
        #self._view.pitchMovePlusToolButton.setDown(False)
        self.refreshView()

    def __onPitchMoveMinusToolButtonPressed(self):
        Logger().trace("MainController.__onPitchMoveMinusToolButtonPressed()")
        self._model.hardware.startAxis('pitch', '-')

    def __onPitchMoveMinusToolButtonReleased(self):
        Logger().trace("MainController.__onPitchMoveMinusToolButtonReleased()")
        self._model.hardware.stopAxis('pitch')
        self._model.hardware.waitStopAxis('pitch')
        #self._view.pitchMoveMinusToolButton.setDown(False)
        self.refreshView()

    def __onYawMoveMinusToolButtonPressed(self):
        Logger().trace("MainController.__onYawMoveMinusToolButtonPressed()")
        self._model.hardware.startAxis('yaw', '-')

    def __onYawMoveMinusToolButtonReleased(self):
        Logger().trace("MainController.__onYawMoveMinusToolButtonReleased()")
        self._model.hardware.stopAxis('yaw')
        self._model.hardware.waitStopAxis('yaw')
        #self._view.yawMoveMinusToolButton.setDown(False)
        self.refreshView()

    def __onConfigPushButtonClicked(self):
        Logger().trace("MainController.__onConfigPushButtonClicked()")
        self.__openConfigDialog()

    def __onShootPushButtonClicked(self):
        Logger().trace("MainController.__onShootPushButtonClicked()")
        self.__openShootdialog()

    def __switchToRealHardwareCallback(self, flag, message=""):
        Logger().debug("MainController.__switchToRealHardwareCallback(): flag=%s" % flag)
        self.__connectStatus = flag
        self.__connectErrorMessage = message

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
        self._view.releaseKeyboard()
        response = controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()
        if response:
            self.__mosaicInputParam = 'fov'
            self.refreshView()
            self.setStatusbarMessage(_("Field of view set to user value"), 10)

    def __openNbPictsDialog(self):
        """
        """
        controller = NbPictsController(self, self._model)
        self._view.releaseKeyboard()
        response = controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()
        if response:
            self.__mosaicInputParam = 'nbPicts'
            self.refreshView()
            self.setStatusbarMessage(_("Number of pictures set to user value"), 10)

    def __openConfigDialog(self):
        """
        """
        try:
            #self._view.configPushButton.setEnabled(False)
            self.setStatusbarMessage(_("Opening configuration dialog. Please wait..."))
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            controller = ConfigController(self, self._model, self._serializer)
        finally:
            #self._view.configPushButton.setEnabled(True)
            self.clearStatusBar()
        self._view.releaseKeyboard()
        response = controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()
 
        if response:
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
        try:
            #self._view.shootPushButton.setEnabled(False)
            self.setStatusbarMessage(_("Opening shoot dialog. Please wait..."))
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            controller = ShootController(self, self._model, self._serializer)
            if self.__fullScreen:
                controller._view.setWindowState(self._view.windowState() | QtCore.Qt.WindowFullScreen)
        finally:
            #self._view.shootPushButton.setEnabled(True)
            self.clearStatusBar()
        self._view.releaseKeyboard()
        controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()

    def __populatePresetComboBox(self):
        """
        """
        self._view.presetComboBox.clear()
        presets = PresetManager().getPresets()
        i = 0
        while True:
            try:
                preset = presets.getByIndex(i)
                name = preset.getName()
                self._view.presetComboBox.addItem(name)
                i += 1
            except ValueError:
                #Logger().exception("MainController.__populatePresetComboBox()", debug=True)
                break

    def __importPresetFile(self, presetFileName):
        """ Import the presets from given file.

        @param presetFileName: name of the preset xml file
        @type presetFileName: str
        """
        Logger().debug("MainController.__importPresetFile(): preset file=%s" % presetFileName)
        try:
            PresetManager().importPresetFile(presetFileName)
            self.__populatePresetComboBox()
            self.refreshView()
        except Exception, msg:
            Logger().exception("MainController.__importPresetFile()")
            controller = ExceptionMessageController(_("Can't import preset file"), str(msg))
            self._view.releaseKeyboard()
            controller.exec_()
            self._view.grabKeyboard()

    def __connectToHardware(self):
        """ Connect to real hardware.
        """
        Logger().info("Connecting to real hardware...")
        self.setStatusbarMessage(_("Connecting to real hardware..."))
        self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_creating.png").scaled(22, 22))
        self.__connectStatus = None

        # Launch connexion thread
        thread.start_new_thread(self._model.switchToRealHardware, ())

        # Wait for end of connection
        while self.__connectStatus is None:
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            time.sleep(0.05)

        # Check connection status
        if self.__connectStatus:
            Spy().setRefreshRate(config.SPY_SLOW_REFRESH)
            self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_established.png").scaled(22, 22))
            Logger().info("Now connected to real hardware")
            self.setStatusbarMessage(_("Now connected to real hardware"), 10)
        else:
            Logger().error("Can't connect to hardware\n%s" % self.__connectErrorMessage)
            #self._view.connectLabel.setIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/connect_no.png").scaled(22, 22)))
            self.setStatusbarMessage(_("Connect to hardware failed"), 10)
            controller = ErrorMessageController(_("Can't connect to hardware"), self.__connectErrorMessage)
            self._view.releaseKeyboard()
            controller.exec_()
            self._view.grabKeyboard()
            controller.shutdown()
            self._view.actionHardwareConnect.setChecked(False)

    def __goToSimulationMode(self):
        """ Connect to simulated hardware.
        """
        Logger().info("Go to simulation mode")
        self._model.switchToSimulatedHardware()
        Spy().setRefreshRate(config.SPY_FAST_REFRESH)
        self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_no.png").scaled(22, 22))
        self.setStatusbarMessage(_("Now in simulation mode"), 10)

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
    def exec_(self):
        #QtCore.QCoreApplication.exec_()
        pass
        
    def setStatusbarMessage(self, message=None, timeout=0):
        """ Display a message on the statusbar.

        @param message: message to display. If None, clear statusbar (use a clearStatusBar() method)
        @type message: str

        @param timeout: display message duration, in s (0 means forever)
        @type timeout: int
        """
        self.clearStatusBar()
        if message is not None:
            self._view.statusBar().showMessage(message, timeout * 1000)

    def clearStatusBar(self):
        """ Clear the statusbar.
        """
        self._view.statusBar().clearMessage()

    def refreshView(self):
        if self._model.mode == 'mosaic':
            self._view.tabWidget.setCurrentIndex(0)
            self._view.setYawStartPushButton.setText("%.1f" % self._model.mosaic.yawStart)
            self._view.setPitchStartPushButton.setText("%.1f" % self._model.mosaic.pitchStart)
            self._view.setYawEndPushButton.setText("%.1f" % self._model.mosaic.yawEnd)
            self._view.setPitchEndPushButton.setText("%.1f" % self._model.mosaic.pitchEnd)
            self._view.yawFovLabel.setText("%.1f" % self._model.mosaic.yawFov)
            self._view.pitchFovLabel.setText("%.1f" % self._model.mosaic.pitchFov)
            self._view.yawNbPictsLabel.setText("%d" % self._model.mosaic.yawNbPicts)
            self._view.pitchNbPictsLabel.setText("%d" % self._model.mosaic.pitchNbPicts)
            self._view.yawRealOverlapLabel.setText("%d" % int(round(100 * self._model.mosaic.yawRealOverlap)))
            self._view.pitchRealOverlapLabel.setText("%d" % int(round(100 * self._model.mosaic.pitchRealOverlap)))
            self._view.yawResolutionLabel.setText("%d" % round(self._model.mosaic.getYawResolution()))
            self._view.pitchResolutionLabel.setText("%d" % round(self._model.mosaic.getPitchResolution()))
        else:
            self._view.tabWidget.setCurrentIndex(1)
            self._view.tabWidget.setTabEnabled(0, self._model.cameraOrientation != 'custom')

        presets = PresetManager().getPresets()
        try:
            index = presets.nameToIndex(self._model.preset.name)
        except ValueError:
            Logger().warning("Previously selected '%s' preset not found" % self._model.preset.name)
            index = 0
            self._model.preset.name = presets.getByIndex(index).getName()
        self._view.presetComboBox.setCurrentIndex(index)
        self._view.presetInfoPlainTextEdit.clear()
        preset = presets.getByIndex(index)
        tooltip = preset.getTooltip()
        self._view.presetInfoPlainTextEdit.setPlainText(tooltip)

        self._view.yawHeadPosLabel.setText("%.1f" % self.__yawPos)
        self._view.pitchHeadPosLabel.setText("%.1f" % self.__pitchPos)
