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
from papywizard.controller.loggerController import LoggerController
from papywizard.controller.helpAboutController import HelpAboutController
from papywizard.controller.totalFovController import TotalFovController
from papywizard.controller.nbPictsController import NbPictsController
from papywizard.controller.configController import ConfigController
from papywizard.controller.shootController import ShootController
from papywizard.controller.spy import Spy
from papywizard.view.messageDialog import WarningMessageDialog, ErrorMessageDialog, \
                                          ExceptionMessageDialog, YesNoMessageDialog, \
                                          AbortMessageDialog


class MainController(AbstractController):
    """ Main controller object.
    """
    def __init__(self, model, logStream):
        """ Init the controller.
        """
        AbstractController.__init__(self, None, model)
        self.__logStream = logStream

        # Try to autoconnect to real hardware
        if ConfigManager().getBoolean('Preferences', 'HARDWARE_AUTO_CONNECT'):
            self._view.actionHardwareConnect.setChecked(True)

    def _init(self):
        self._uiFile = "mainWindow.ui"

        self.__keyPressedDict = {'Right': False,
                                 'Left': False,
                                 'Up': False,
                                 'Down': False,
                             }
        self.__key = {'FullScreen': QtCore.Qt.Key_F11,
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

        # Nokia plateform stuff
        try:
            import hildon
            self.__key['FullScreen'] = QtCore.Qt.Key_F6
            self.__key['Home'] = QtCore.Qt.Key_F8
            self.__key['End'] =  QtCore.Qt.Key_F7
        except ImportError:
            pass

        self.__yawPos = 0
        self.__pitchPos = 0
        self.__connectStatus = None
        self.__connectErrorMessage = None
        self.__mosaicInputParam = 'startEnd'
        self.__manualSpeed = 'normal'
        self.__lastConfigTabSelected = 0

    def _initWidgets(self):
        def hasHeightForWidth(self):
            return True

        def heightForWidth(self, width):
            return width

        # Status bar
        # Manual speed and connect button
        self._view.manualSpeedLabel = QtGui.QLabel()
        self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_fwd.png").scaled(22, 22))
        self._view.statusBar().addPermanentWidget(self._view.manualSpeedLabel)
        self._view.connectLabel = QtGui.QLabel()
        self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_no.png").scaled(22, 22))
        self._view.statusBar().addPermanentWidget(self._view.connectLabel)
        self._view.statusBar().show()

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
            #self._view.setWindowState(self._view.windowState() | QtCore.Qt.WindowFullScreen)
            Logger().debug("MainController._initWidgets(): start in fullscreen mode")
            self._view.showFullScreen()

        self._view.show()

    def _connectSignals(self):
        AbstractController._connectSignals(self)

        # Menus
        self.connect(self._view.actionFileImportPreset, QtCore.SIGNAL("activated()"), self.__onActionFileImportPresetActivated)
        self.connect(self._view.actionFileLoadStyleSheet, QtCore.SIGNAL("activated()"), self.__onActionFileLoadStyleSheetActivated)

        self.connect(self._view.actionHardwareConnect, QtCore.SIGNAL("toggled(bool)"), self.__onActionHardwareConnectToggled)
        self.connect(self._view.actionHardwareSetLimitYawMinus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitYawMinusActivated)
        self.connect(self._view.actionHardwareSetLimitYawPlus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitYawPlusActivated)
        self.connect(self._view.actionHardwareSetLimitPitchPlus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitPitchPlusActivated)
        self.connect(self._view.actionHardwareSetLimitPitchMinus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitPitchMinusActivated)
        self.connect(self._view.actionHardwareClearLimits, QtCore.SIGNAL("activated()"), self.__onActionHardwareClearLimitsActivated)
        self.connect(self._view.actionHardwareGotoHome, QtCore.SIGNAL("activated()"), self.__onActionHardwareGotoHomeActivated)
        self.connect(self._view.actionHardwareGotoInitial, QtCore.SIGNAL("activated()"), self.__onActionHardwareGotoInitialActivated)

        self.connect(self._view.actionHelpManual, QtCore.SIGNAL("activated()"), self.__onActionHelpManualActivated)
        self.connect(self._view.actionHelpViewLog, QtCore.SIGNAL("activated()"), self.__onActionHelpViewLogActivated)
        self.connect(self._view.actionHelpAboutPapywizard, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutPapywizardActivated)
        self.connect(self._view.actionHelpAboutQt, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutQtActivated)

        # Widgets
        self.connect(self._view.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.__onTabWidgetCurrentChanged)

        self.connect(self._view.setYawStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawStartPushButtonClicked)
        self.connect(self._view.setPitchStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchStartPushButtonClicked)
        self.connect(self._view.setYawEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawEndPushButtonClicked)
        self.connect(self._view.setPitchEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchEndPushButtonClicked)
        self.connect(self._view.setStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetStartPushButtonClicked)
        self.connect(self._view.setEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetEndPushButtonClicked)
        self.connect(self._view.totalFovPushButton, QtCore.SIGNAL("clicked()"), self.__onTotalFovPushButtonClicked)
        self.connect(self._view.nbPictsPushButton, QtCore.SIGNAL("clicked()"), self.__onNbPictsPushButtonClicked)

        self.connect(self._view.presetComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onPresetComboBoxCurrentIndexChanged)

        self.connect(self._view.setReferenceToolButton, QtCore.SIGNAL("clicked()"), self.__onSetReferenceToolButtonClicked)
        self.connect(self._view.yawMovePlusToolButton, QtCore.SIGNAL("pressed()"), self.__onYawMovePlusToolButtonPressed)
        self.connect(self._view.yawMovePlusToolButton, QtCore.SIGNAL("released()"), self.__onYawMovePlusToolButtonReleased)
        self.connect(self._view.pitchMovePlusToolButton, QtCore.SIGNAL("pressed()"), self.__onPitchMovePlusToolButtonPressed)
        self.connect(self._view.pitchMovePlusToolButton, QtCore.SIGNAL("released()"), self.__onPitchMovePlusToolButtonReleased)
        self.connect(self._view.yawMoveMinusToolButton, QtCore.SIGNAL("pressed()"), self.__onYawMoveMinusToolButtonPressed)
        self.connect(self._view.yawMoveMinusToolButton, QtCore.SIGNAL("released()"), self.__onYawMoveMinusToolButtonReleased)
        self.connect(self._view.pitchMoveMinusToolButton, QtCore.SIGNAL("pressed()"), self.__onPitchMoveMinusToolButtonPressed)
        self.connect(self._view.pitchMoveMinusToolButton, QtCore.SIGNAL("released()"), self.__onPitchMoveMinusToolButtonReleased)

        self.connect(self._view.configPushButton, QtCore.SIGNAL("clicked()"), self.__onConfigPushButtonClicked)
        self.connect(self._view.shootPushButton, QtCore.SIGNAL("clicked()"), self.__onShootPushButtonClicked)

        self.connect(Spy(), QtCore.SIGNAL("update"), self.__onPositionUpdate, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("hardwareConnected"), self.__onHardwareConnected, QtCore.Qt.BlockingQueuedConnection)

        self._view.grabKeyboard()
        self._view._originalKeyPressEvent = self._view.keyPressEvent
        self._view.keyPressEvent = self.__onKeyPressed
        self._view._originalKeyReleaseEvent = self._view.keyReleaseEvent
        self._view.keyReleaseEvent = self.__onKeyReleased

    def _disconnectSignals(self):
        AbstractController._disconnectSignals(self)

        # Menus
        self.disconnect(self._view.actionFileImportPreset, QtCore.SIGNAL("activated()"), self.__onActionFileImportPresetActivated)
        self.disconnect(self._view.actionFileLoadStyleSheet, QtCore.SIGNAL("activated()"), self.__onActionFileLoadStyleSheetActivated)

        self.disconnect(self._view.actionHardwareConnect, QtCore.SIGNAL("toggled(bool)"), self.__onActionHardwareConnectToggled)
        self.disconnect(self._view.actionHardwareSetLimitYawMinus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitYawMinusActivated)
        self.disconnect(self._view.actionHardwareSetLimitYawPlus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitYawPlusActivated)
        self.disconnect(self._view.actionHardwareSetLimitPitchPlus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitPitchPlusActivated)
        self.disconnect(self._view.actionHardwareSetLimitPitchMinus, QtCore.SIGNAL("activated()"), self.__onActionHardwareSetLimitPitchMinusActivated)
        self.disconnect(self._view.actionHardwareClearLimits, QtCore.SIGNAL("activated()"), self.__onActionHardwareClearLimitsActivated)
        self.disconnect(self._view.actionHardwareGotoHome, QtCore.SIGNAL("activated()"), self.__onActionHardwareGotoHomeActivated)
        self.disconnect(self._view.actionHardwareGotoInitial, QtCore.SIGNAL("activated()"), self.__onActionHardwareGotoInitialActivated)

        self.disconnect(self._view.actionHelpManual, QtCore.SIGNAL("activated()"), self.__onActionHelpManualActivated)
        self.disconnect(self._view.actionHelpViewLog, QtCore.SIGNAL("activated()"), self.__onActionHelpViewLogActivated)
        self.disconnect(self._view.actionHelpAboutPapywizard, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutPapywizardActivated)
        self.disconnect(self._view.actionHelpAboutQt, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutQtActivated)

        # Widgets
        self.disconnect(self._view.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.__onTabWidgetCurrentChanged)

        self.disconnect(self._view.setYawStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawStartPushButtonClicked)
        self.disconnect(self._view.setPitchStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchStartPushButtonClicked)
        self.disconnect(self._view.setYawEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawEndPushButtonClicked)
        self.disconnect(self._view.setPitchEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchEndPushButtonClicked)
        self.disconnect(self._view.setStartPushButton, QtCore.SIGNAL("clicked()"), self.__onSetStartPushButtonClicked)
        self.disconnect(self._view.setEndPushButton, QtCore.SIGNAL("clicked()"), self.__onSetEndPushButtonClicked)
        self.disconnect(self._view.totalFovPushButton, QtCore.SIGNAL("clicked()"), self.__onTotalFovPushButtonClicked)
        self.disconnect(self._view.nbPictsPushButton, QtCore.SIGNAL("clicked()"), self.__onNbPictsPushButtonClicked)

        self.disconnect(self._view.presetComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onPresetComboBoxCurrentIndexChanged)

        self.disconnect(self._view.setReferenceToolButton, QtCore.SIGNAL("clicked()"), self.__onSetReferenceToolButtonClicked)
        self.disconnect(self._view.yawMovePlusToolButton, QtCore.SIGNAL("pressed()"), self.__onYawMovePlusToolButtonPressed)
        self.disconnect(self._view.yawMovePlusToolButton, QtCore.SIGNAL("released()"), self.__onYawMovePlusToolButtonReleased)
        self.disconnect(self._view.pitchMovePlusToolButton, QtCore.SIGNAL("pressed()"), self.__onPitchMovePlusToolButtonPressed)
        self.disconnect(self._view.pitchMovePlusToolButton, QtCore.SIGNAL("released()"), self.__onPitchMovePlusToolButtonReleased)
        self.disconnect(self._view.yawMoveMinusToolButton, QtCore.SIGNAL("pressed()"), self.__onYawMoveMinusToolButtonPressed)
        self.disconnect(self._view.yawMoveMinusToolButton, QtCore.SIGNAL("released()"), self.__onYawMoveMinusToolButtonReleased)
        self.disconnect(self._view.pitchMoveMinusToolButton, QtCore.SIGNAL("pressed()"), self.__onPitchMoveMinusToolButtonPressed)
        self.disconnect(self._view.pitchMoveMinusToolButton, QtCore.SIGNAL("released()"), self.__onPitchMoveMinusToolButtonReleased)

        self.disconnect(self._view.configPushButton, QtCore.SIGNAL("clicked()"), self.__onConfigPushButtonClicked)
        self.disconnect(self._view.shootPushButton, QtCore.SIGNAL("clicked()"), self.__onShootPushButtonClicked)

        self.disconnect(Spy(), QtCore.SIGNAL("update"), self.__onPositionUpdate)
        self.disconnect(self._model, QtCore.SIGNAL("hardwareConnected"), self.__onHardwareConnected)

        self._view.releaseKeyboard()
        self._view.keyPressEvent = self._view._originalKeyPressEvent
        self._view.keyReleaseEvent = self._view._originalKeyReleaseEvent

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
    def _onCloseEvent(self, event):
        Logger().trace("MainController._onCloseEvent()")
        QtGui.QApplication.quit()

    def __onKeyPressed(self, event):
        #Logger().debug("MainController.__onKeyPressed(): key='%s" % event.key())

        # 'FullScreen' key
        if event.key() == self.__key['FullScreen'] and not event.isAutoRepeat():
            Logger().debug("MainController.__onKeyPressed(): 'FullScreen' key pressed")
            if self._view.windowState() & QtCore.Qt.WindowFullScreen:
                Logger().debug("MainController.__onKeyPressed(): switch to normal")
                self._view.showNormal()
            else:
                Logger().debug("MainController.__onKeyPressed(): switch to fullscreen")
                self._view.showFullScreen()
            event.ignore()

        # 'Right' key
        if event.key() == self.__key['Right'] and not event.isAutoRepeat():
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyPressed(): 'Right' key pressed; start 'yaw' axis dir '+'")
                self.__keyPressedDict['Right'] = True
                self._view.yawMovePlusToolButton.setDown(True)
                self._model.hardware.startAxis('yaw', '+')
            event.ignore()

        # 'Left' key
        elif event.key() == self.__key['Left'] and not event.isAutoRepeat():
            if not self.__keyPressedDict['Left'] and not self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyPressed(): 'Left' key pressed; start 'yaw' axis dir '-'")
                self.__keyPressedDict['Left'] = True
                self._view.yawMoveMinusToolButton.setDown(True)
                self._model.hardware.startAxis('yaw', '-')
            event.ignore()

        # 'Up' key
        elif event.key() == self.__key['Up'] and not event.isAutoRepeat():
            if not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyPressed(): 'Up' key pressed; start 'pitch' axis dir '+'")
                self.__keyPressedDict['Up'] = True
                self._view.pitchMovePlusToolButton.setDown(True)
                self._model.hardware.startAxis('pitch', '+')
            event.ignore()

        # 'Down' key
        elif event.key() == self.__key['Down'] and not event.isAutoRepeat():
            if not self.__keyPressedDict['Down'] and not self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyPressed(): 'Down' key pressed; start 'pitch' axis dir '-'")
                self.__keyPressedDict['Down'] = True
                self._view.pitchMoveMinusToolButton.setDown(True)
                self._model.hardware.startAxis('pitch', '-')
            event.ignore()

        # 'Home' key
        elif event.key() == self.__key['Home'] and not event.isAutoRepeat():
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                if self.__manualSpeed == 'normal':
                    self.__manualSpeed = 'slow'
                    Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; select slow speed")
                    self._model.hardware.setManualSpeed('slow')
                    self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_play.png").scaled(22, 22))
                    self.setStatusbarMessage(self.tr("Manual speed set to slow"), 10)
                elif self.__manualSpeed == 'fast':
                    self.__manualSpeed = 'normal'
                    Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; select normal speed")
                    self._model.hardware.setManualSpeed('normal')
                    self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_fwd.png").scaled(22, 22))
                    self.setStatusbarMessage(self.tr("Manual speed set to normal"), 10)
            event.ignore()

        # 'End' key
        elif event.key() == self.__key['End'] and not event.isAutoRepeat():
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                if self.__manualSpeed == 'slow':
                    self.__manualSpeed = 'normal'
                    Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; select normal speed")
                    self._model.hardware.setManualSpeed('normal')
                    self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_fwd.png").scaled(22, 22))
                    self.setStatusbarMessage(self.tr("Manual speed set to normal"), 10)
                elif self.__manualSpeed == 'normal':
                    self._view.releaseKeyboard()
                    dialog = WarningMessageDialog(self.tr("Fast manual speed"), self.tr("This can be dangerous for the hardware!"))
                    dialog.exec_()
                    self._view.grabKeyboard()
                    self.__manualSpeed = 'fast'
                    Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; select fast speed")
                    self._model.hardware.setManualSpeed('fast')
                    self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/messagebox_warning.png").scaled(22, 22))
                    self.setStatusbarMessage(self.tr("Manual speed set to fast"), 10)
            event.ignore()

        # 'Tab' key
        #elif event.key() == self.__key['Tab']:
            #if not self.__keyPressedDict['Tab']:
                #Logger().debug("MainController.__onKeyPressed(): 'Tab' key pressed; blocked")
                #self.__keyPressedDict['Tab'] = True
            #event.accept()

        # 'Space' key. Activate the focuses widget
        #elif event.key() == self.__key['space']:
            #Logger().debug("MainController.__onKeyPressed(): 'space' key pressed; blocked")
            #widget = QtGui.QApplication.focusWidget()
            #self._view.releaseKeyboard()
            #widget.keyPressEvent(event)
            #self._view.grabKeyboard()
            #event.accept()

        # 'Return' key
        elif event.key() == self.__key['Return'] and not event.isAutoRepeat():
            Logger().debug("MainController.__onKeyPressed(): 'Return' key pressed; open shoot dialog")
            self.__openShootdialog()
            event.ignore()

        # 'Escape' key
        elif event.key() == self.__key['Escape'] and not event.isAutoRepeat():
            Logger().debug("MainController.__onKeyPressed(): 'Escape' key pressed")
            self._view.releaseKeyboard()
            dialog = YesNoMessageDialog(self.tr("About to Quit"), self.tr("Are you sure you want to quit Papywizard?"))
            response = dialog.exec_()
            self._view.grabKeyboard()
            if response == QtGui.QMessageBox.Yes:
                QtGui.QApplication.quit()
            event.ignore()

        else:
            event.accept()

    def __onKeyReleased(self, event):
        #Logger().debug("MainController.__onKeyReleased(): key='%s" % event.key())

        # 'Right' key
        if event.key() == self.__key['Right'] and not event.isAutoRepeat():
            if self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyReleased(): 'Right' key released; stop 'yaw' axis")
                self._model.hardware.stopAxis('yaw')
                self._model.hardware.waitStopAxis('yaw')
                self.__keyPressedDict['Right'] = False
                self._view.yawMovePlusToolButton.setDown(False)
            event.accept()

        # 'Left' key
        elif event.key() == self.__key['Left'] and not event.isAutoRepeat():
            if self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyReleased(): 'Left' key released; stop 'yaw' axis")
                self._model.hardware.stopAxis('yaw')
                self._model.hardware.waitStopAxis('yaw')
                self.__keyPressedDict['Left'] = False
                self._view.yawMoveMinusToolButton.setDown(False)
            event.accept()

        # 'Up' key
        elif event.key() == self.__key['Up'] and not event.isAutoRepeat():
            if self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyReleased(): 'Up' key released; stop 'pitch' axis")
                self._model.hardware.stopAxis('pitch')
                self._model.hardware.waitStopAxis('pitch')
                self.__keyPressedDict['Up'] = False
                self._view.pitchMovePlusToolButton.setDown(False)
            event.accept()

        # 'Down' key
        elif event.key() == self.__key['Down'] and not event.isAutoRepeat():
            if self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyReleased(): 'Down' key released; stop 'pitch' axis")
                self._model.hardware.stopAxis('pitch')
                self._model.hardware.waitStopAxis('pitch')
                self.__keyPressedDict['Down'] = False
                self._view.pitchMoveMinusToolButton.setDown(False)
            event.accept()

        else:
            event.ignore()

    def __onActionFileImportPresetActivated(self):
        Logger().trace("MainController.__onActionFileImportPresetActivated()")
        fileName =  QtGui.QFileDialog.getOpenFileName(self._view,
                                                      self.tr("Import Preset File"),
                                                      os.path.join(config.HOME_DIR, config.PRESET_FILE),
                                                      self.tr("XML files (*.xml);;All files (*)"))
        if fileName:
            self.__importPresetFile(fileName)

    def __onActionFileLoadStyleSheetActivated(self):
        Logger().trace("MainController.__onActionFileLoadStyleSheetActivated()")
        fileName =  QtGui.QFileDialog.getOpenFileName(self._view,
                                                      self.tr("Load Style Sheet"),
                                                      os.path.join(config.HOME_DIR, config.STYLESHEET_FILE),
                                                      self.tr("CSS files (*.css);;All files (*)"))
        if fileName:
            self.__loadStyleSheet(fileName)

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
        self.setStatusbarMessage(self.tr("Yaw - limit set"), 10)

    def __onActionHardwareSetLimitYawPlusActivated(self):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('yaw', '+', yaw)
        Logger().debug("MainController.__onActionHardwareSetLimitYawPlusActivated(): yaw plus limit set to %.1f" % yaw)
        self.setStatusbarMessage(self.tr("Yaw + limit set"), 10)

    def __onActionHardwareSetLimitPitchPlusActivated(self):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('pitch', '+', pitch)
        Logger().debug("MainController.__onActionHardwareSetLimitPitchPlusActivated(): pitch plus limit set to %.1f" % pitch)
        self.setStatusbarMessage(self.tr("Pitch + limit set"), 10)

    def __onActionHardwareSetLimitPitchMinusActivated(self):
        yaw, pitch = self._model.hardware.readPosition()
        self._model.hardware.setLimit('pitch', '-', pitch)
        Logger().debug("MainController.__onActionHardwareSetLimitPitchMinusActivated(): pitch minus limit set to %.1f" % pitch)
        self.setStatusbarMessage(self.tr("Pitch - limit set"), 10)

    def __onActionHardwareClearLimitsActivated(self):
        Logger().trace("MainController.__onActionHardwareClearLimitsActivated()")
        self._model.hardware.clearLimits()
        self.setStatusbarMessage(self.tr("Limits cleared"), 10)

    def __onActionHardwareGotoHomeActivated(self):
        Logger().trace("MainController.__onActionHardwareGotoHomeActivated()")
        self.setStatusbarMessage(self.tr("Goto home position..."))
        self._model.hardware.gotoPosition(0., 0., wait=False)
        dialog = AbortMessageDialog(self.tr("Goto home position"), self.tr("Please wait..."))
        self._view.releaseKeyboard()
        dialog.show()
        while self._model.hardware.isAxisMoving():
            QtGui.QApplication.processEvents() #QtCore.QEventLoop.ExcludeUserInputEvents)
            if dialog.result() == QtGui.QMessageBox.Abort:
                self._model.hardware.stopAxis()
                self.setStatusbarMessage(self.tr("Operation aborted"), 10)
                break
            time.sleep(0.01)
        else:
            self.setStatusbarMessage(self.tr("Home position reached"), 10)
        dialog.hide()
        self._view.grabKeyboard()

    def __onActionHardwareGotoInitialActivated(self):
        Logger().trace("MainController.__onActionHardwareGotoInitialActivated()")
        self.setStatusbarMessage(self.tr("Goto initial position..."))
        QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        self._model.hardware.gotoPosition(0., 0., useOffset=False, wait=False)
        dialog = AbortMessageDialog(self.tr("Goto initial position"), self.tr("Please wait..."))
        self._view.releaseKeyboard()
        dialog.show()
        while self._model.hardware.isAxisMoving():
            QtGui.QApplication.processEvents() #QtCore.QEventLoop.ExcludeUserInputEvents)
            if dialog.result() == QtGui.QMessageBox.Abort:
                self._model.hardware.stopAxis()
                self.setStatusbarMessage(self.tr("Operation aborted"), 10)
                break
            time.sleep(0.01)
        else:
            self.setStatusbarMessage(self.tr("Initial position reached"), 10)
        dialog.hide()
        self._view.grabKeyboard()

    def __onActionHelpManualActivated(self):
        Logger().trace("MainController.__onActionHelpManualActivated()")
        webbrowser.open(config.USER_GUIDE_URL)

    def __onActionHelpWhatsThisActivated(self):
        Logger().trace("MainController.__onActionHelpWhatsThisActivated()")
        Logger().warning("Not yet implemented")

    def __onActionHelpViewLogActivated(self):
        Logger().trace("MainController.__onActionHelpViewLogActivated()")
        controller = LoggerController(self, self._model)
        controller.setBuffer(self.__logStream)
        self._view.releaseKeyboard()
        controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()

    def __onActionHelpAboutPapywizardActivated(self):
        Logger().trace("MainController.__onActionHelpAboutPapywizardActivated()")
        controller = HelpAboutController(self, self._model)
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
            self._refreshMosaicPage()
        elif index == 1:
            self._model.mode = 'preset'
        #elif index == 2
            #selF._model.mode = 'timelapse'
        Logger().debug("MainController.__onTabWidgetCurrentChanged(): shooting mode set to '%s'" % self._model.mode)

    def __onSetYawStartPushButtonClicked(self):
        Logger().trace("MainController.__onSetYawStartPushButtonClicked()")
        self._model.mosaic.yawStart = self.__yawPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Yaw start set from current position"), 10)

    def __onSetPitchStartPushButtonClicked(self):
        Logger().trace("MainController.__onSetPitchStartPushButtonClicked()")
        self._model.mosaic.pitchStart = self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Pitch start set from current position"), 10)

    def __onSetYawEndPushButtonClicked(self):
        Logger().trace("MainController.__onSetYawEndPushButtonClicked()")
        self._model.mosaic.yawEnd = self.__yawPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Yaw end set from current position"), 10)

    def __onSetPitchEndPushButtonClicked(self):
        Logger().trace("MainController.__onSetEndPitchButtonClicked()")
        self._model.mosaic.pitchEnd = self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Pitch end set from current position"), 10)

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
            Logger().exception("MainController.__onPresetComboBoxCurrentIndexChanged()", debug=True)
            pass

    def __onSetReferenceToolButtonClicked(self):
        Logger().trace("MainController.__onSetReferenceToolButtonClicked()")
        Logger().info("Set hardware reference")
        self._model.hardware.setReference()
        self.setStatusbarMessage(self.tr("Reference set at current position"), 10)

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

    def __onHardwareConnected(self, flag, message=""):
        Logger().debug("MainController.__onHardwareConnected(): flag=%s" % flag)
        self.__connectStatus = flag
        self.__connectErrorMessage = message

    # Helpers
    def __setYawPitchStartPosition(self):
        """ Set yaw/pitch end from current position.
        """
        self._model.mosaic.yawStart, self._model.mosaic.pitchStart = self.__yawPos, self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Yaw/pitch start set from current position"), 10)

    def __setYawPitchEndPosition(self):
        """ Set yaw/pitch start from current position.
        """
        self._model.mosaic.yawEnd, self._model.mosaic.pitchEnd = self.__yawPos, self.__pitchPos
        self.__mosaicInputParam = 'startEnd'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Yaw/pitch end set from current position"), 10)

    def __openTotalFovDialog(self):
        """ Open the Total Fov input dialog.
        """
        controller = TotalFovController(self, self._model)
        self._view.releaseKeyboard()
        response = controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()
        if response:
            self.__mosaicInputParam = 'fov'
            self.refreshView()
            self.setStatusbarMessage(self.tr("Field of view set to user value"), 10)

    def __openNbPictsDialog(self):
        """ Open the Nb Picts input dialog.
        """
        controller = NbPictsController(self, self._model)
        self._view.releaseKeyboard()
        response = controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()
        if response:
            self.__mosaicInputParam = 'nbPicts'
            self.refreshView()
            self.setStatusbarMessage(self.tr("Number of pictures set to user value"), 10)

    def __openConfigDialog(self):
        """ Open the configuration dialog.
        """
        try:
            #self._view.configPushButton.setEnabled(False)
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.setStatusbarMessage(self.tr("Opening configuration dialog. Please wait..."))
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            controller = ConfigController(self, self._model)
            controller.setSelectedTab(self.__lastConfigTabSelected)
        finally:
            #self._view.configPushButton.setEnabled(True)
            QtGui.qApp.restoreOverrideCursor()
            self.clearStatusBar()
        self._view.releaseKeyboard()
        response = controller.exec_()
        self._view.grabKeyboard()
        self.__lastConfigTabSelected = controller.getSelectedTab()
        controller.shutdown()
 
        if response:
            Logger().setLevel(ConfigManager().get('Preferences', 'LOGGER_LEVEL'))
            if self.__mosaicInputParam == 'startEnd':
                pass
            elif self.__mosaicInputParam == 'fov':
                yawFov = float(self._view.yawFovLabel.text())
                pitchFov = float(self._view.pitchFovLabel.text())
                self._model.setStartEndFromFov(yawFov, pitchFov)
            elif self.__mosaicInputParam == 'nbPicts':
                yawNbPicts = int(self._view.yawNbPictsLabel.text())
                pitchNbPicts = int(self._view.pitchNbPictsLabel.text())
                self._model.setStartEndFromNbPicts(yawNbPicts, pitchNbPicts)
            self.refreshView()

    def __openShootdialog(self):
        """ Open teh shooting dialog.
        """
        self._model.setStepByStep(False)
        try:
            #self._view.shootPushButton.setEnabled(False)
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.setStatusbarMessage(self.tr("Opening shoot dialog. Please wait..."))
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            controller = ShootController(self, self._model)
            if self._view.windowState() & QtCore.Qt.WindowFullScreen:
                controller._view.showFullScreen()
        finally:
            #self._view.shootPushButton.setEnabled(True)
            QtGui.qApp.restoreOverrideCursor()
            self.clearStatusBar()
        self._view.releaseKeyboard()
        controller.exec_()
        self._view.grabKeyboard()
        controller.shutdown()

    def __populatePresetComboBox(self):
        """ Populate the preset combo box.
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
            self._view.releaseKeyboard()
            dialog = ExceptionMessageDialog(self.tr("Can't import preset file"), unicode(msg))
            dialog.exec_()
            self._view.grabKeyboard()

    def __loadStyleSheet(self, styleSheetFileName):
        """ Load and apply the style sheet.

        @param styleSheetFileName: name of the style sheet
        @type styleSheetFileName: str
        """
        Logger().debug("MainController.__loadStyleSheet(): style sheet=%s" % styleSheetFileName)
        try:
            styleSheetFile = file(styleSheetFileName)
            QtGui.qApp.setStyleSheet(styleSheetFile.read())
            styleSheetFile.close()
        except Exception, msg:
            Logger().exception("MainController.__loadStyleSheet()")
            self._view.releaseKeyboard()
            dialog = ExceptionMessageDialog(self.tr("Can't load style sheet"), unicode(msg))
            dialog.exec_()
            self._view.grabKeyboard()

    def __connectToHardware(self):
        """ Connect to real hardware.

        # To be redesigned, so it can be canceled, and exceptions can be traced.
        """
        Logger().info("Connecting to real hardware...")
        self.setStatusbarMessage(self.tr("Connecting to real hardware..."))
        self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_creating.png").scaled(22, 22))
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.__connectStatus = None

        # Launch connexion thread
        thread.start_new_thread(self._model.switchToRealHardware, ())

        # Wait for end of connection
        while self.__connectStatus is None:
            QtGui.QApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            time.sleep(0.05)

        # Restore cursor
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        # Check connection status
        if self.__connectStatus:
            Spy().setRefreshRate(config.SPY_SLOW_REFRESH)
            self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_established.png").scaled(22, 22))
            Logger().info("Now connected to real hardware")
            self.setStatusbarMessage(self.tr("Now connected to real hardware"), 10)
        else:
            Logger().error("Can't connect to hardware\n%s" % self.__connectErrorMessage)
            #self._view.connectLabel.setIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/connect_no.png").scaled(22, 22)))
            self.setStatusbarMessage(self.tr("Connect to hardware failed"), 10)
            dialog = ErrorMessageDialog(self.tr("Can't connect to hardware"), self.__connectErrorMessage)
            self._view.releaseKeyboard()
            dialog.exec_()
            self._view.grabKeyboard()
            self._view.actionHardwareConnect.setChecked(False)

    def __goToSimulationMode(self):
        """ Connect to simulated hardware.
        """
        Logger().info("Go to simulation mode")
        self._model.switchToSimulatedHardware()
        Spy().setRefreshRate(config.SPY_FAST_REFRESH)
        self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_no.png").scaled(22, 22))
        self.setStatusbarMessage(self.tr("Now in simulation mode"), 10)

    def __onPositionUpdate(self, yaw, pitch):
        """ Refresh position according to new pos.

        @param yaw: yaw axis value
        @type yaw: float

        @param pitch: pitch axix value
        @type pitch: float
        """
        #Logger().trace("MainController.__onPositionUpdate()")
        self.__yawPos = yaw
        self.__pitchPos = pitch
        self._view.yawHeadPosLabel.setText("%.1f" % self.__yawPos)
        self._view.pitchHeadPosLabel.setText("%.1f" % self.__pitchPos)

    # Interface
    def exec_(self):
        return QtGui.qApp.exec_()

    def shutdown(self):
        AbstractController.shutdown(self)
        print bool(self._view.windowState() & QtCore.Qt.WindowFullScreen)
        if self._view.windowState() & QtCore.Qt.WindowFullScreen:
            self.__fullScreen = True
        else:
            self.__fullScreen = False

    def setStatusbarMessage(self, message, timeout=0):
        """ Display a message on the statusbar.

        @param message: message to display
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

    def _refreshMosaicPage(self):
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

    def refreshView(self):
        if self._model.mode == 'mosaic':
            self._view.tabWidget.setCurrentIndex(0)
            self._refreshMosaicPage()
        else:
            self._view.tabWidget.setCurrentIndex(1)
            flag = self._model.cameraOrientation != 'custom' and self._model.camera.lens.type_ != 'fisheye'
            self._view.tabWidget.setTabEnabled(0, flag)

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
