# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
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
import sys

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.common.presetManager import PresetManager
from papywizard.common.exception import HardwareError
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.loggerController import LoggerController
from papywizard.controller.helpAboutController import HelpAboutController
from papywizard.controller.totalFovController import TotalFovController
from papywizard.controller.nbPictsController import NbPictsController
from papywizard.controller.pluginsController import PluginsController
from papywizard.controller.configController import ConfigController
from papywizard.controller.shootController import ShootController
from papywizard.controller.pluginsStatusController import PluginsStatusController
from papywizard.plugins.pluginsConnector import PluginsConnector
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

        # Disable widgets
        self.__SetDisconnectedWidgetState()

    def _init(self):
        self._uiFile = "mainWindow.ui"

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
        self.__mosaicInputParam = 'corners'
        self.__manualSpeed = 'normal'
        self.__lastPluginsTabSelected = 0
        self.__lastConfigTabSelected = 0
        self.__pluginsStatus = None
        self.__pluginsConnected = False

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
        self.connect(self._view.actionHardwareGotoReference, QtCore.SIGNAL("activated()"), self.__onActionHardwareGotoReferenceActivated)
        self.connect(self._view.actionHardwareGotoInitial, QtCore.SIGNAL("activated()"), self.__onActionHardwareGotoInitialActivated)
        self.connect(self._view.actionHardwarePlugins, QtCore.SIGNAL("activated()"), self.__onActionHardwarePluginsActivated)

        self.connect(self._view.actionHelpManual, QtCore.SIGNAL("activated()"), self.__onActionHelpManualActivated)
        self.connect(self._view.actionHelpViewLog, QtCore.SIGNAL("activated()"), self.__onActionHelpViewLogActivated)
        self.connect(self._view.actionHelpAboutPapywizard, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutPapywizardActivated)
        self.connect(self._view.actionHelpAboutQt, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutQtActivated)

        # Widgets
        self.connect(self._view.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.__onTabWidgetCurrentChanged)

        self.connect(self._view.setCorner0PushButton, QtCore.SIGNAL("clicked()"), self.__onSetCorner0PushButtonClicked)
        self.connect(self._view.setYawCorner0PushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawCorner0PushButtonClicked)
        self.connect(self._view.setPitchCorner0PushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchCorner0PushButtonClicked)
        self.connect(self._view.setCorner1PushButton, QtCore.SIGNAL("clicked()"), self.__onSetCorner1PushButtonClicked)
        self.connect(self._view.setYawCorner1PushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawCorner1PushButtonClicked)
        self.connect(self._view.setPitchCorner1PushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchCorner1PushButtonClicked)
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
        self.disconnect(self._view.actionHardwareGotoReference, QtCore.SIGNAL("activated()"), self.__onActionHardwareGotoReferenceActivated)
        self.disconnect(self._view.actionHardwareGotoInitial, QtCore.SIGNAL("activated()"), self.__onActionHardwareGotoInitialActivated)
        self.disconnect(self._view.actionHardwarePlugins, QtCore.SIGNAL("activated()"), self.__onActionHardwarePluginsActivated)

        self.disconnect(self._view.actionHelpManual, QtCore.SIGNAL("activated()"), self.__onActionHelpManualActivated)
        self.disconnect(self._view.actionHelpViewLog, QtCore.SIGNAL("activated()"), self.__onActionHelpViewLogActivated)
        self.disconnect(self._view.actionHelpAboutPapywizard, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutPapywizardActivated)
        self.disconnect(self._view.actionHelpAboutQt, QtCore.SIGNAL("activated()"), self.__onActionHelpAboutQtActivated)

        # Widgets
        self.disconnect(self._view.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.__onTabWidgetCurrentChanged)

        self.disconnect(self._view.setCorner0PushButton, QtCore.SIGNAL("clicked()"), self.__onSetCorner0PushButtonClicked)
        self.disconnect(self._view.setYawCorner0PushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawCorner0PushButtonClicked)
        self.disconnect(self._view.setPitchCorner0PushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchCorner0PushButtonClicked)
        self.disconnect(self._view.setCorner1PushButton, QtCore.SIGNAL("clicked()"), self.__onSetCorner1PushButtonClicked)
        self.disconnect(self._view.setYawCorner1PushButton, QtCore.SIGNAL("clicked()"), self.__onSetYawCorner1PushButtonClicked)
        self.disconnect(self._view.setPitchCorner1PushButton, QtCore.SIGNAL("clicked()"), self.__onSetPitchCorner1PushButtonClicked)
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

        self._view.keyPressEvent = self._view._originalKeyPressEvent
        self._view.keyReleaseEvent = self._view._originalKeyReleaseEvent

    # Properties
    def __getFullScreenFlag(self):
        """
        """
        #return ConfigManager().getBoolean('FULLSCREEN')
        Logger().warning("MainController.__getFullScreenFlag(): fix fullScreenFlag property!!!")
        return False

    def __setFullScreenFlag(self, flag):
        """
        """
        ConfigManager().setBoolean('FULLSCREEN', flag)

    __fullScreen = property(__getFullScreenFlag, __setFullScreenFlag)

    # Callbacks
    def _onCloseEvent(self, event):
        Logger().trace("MainController._onCloseEvent()")
        self.__stopConnection()
        QtGui.QApplication.quit()

    def __onKeyPressed(self, event):
        Logger().debug("MainController.__onKeyPressed(): key='%s" % event.key())

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

        # 'Home' key
        elif event.key() == self.__key['Home'] and not event.isAutoRepeat():
            if self.__manualSpeed == 'normal':
                self.__manualSpeed = 'slow'
                Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; select slow speed")
                self._model.head.setManualSpeed('slow')
                self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_play.png").scaled(22, 22))
                self.setStatusbarMessage(self.tr("Manual speed set to slow"), 10)
            elif self.__manualSpeed == 'fast':
                self.__manualSpeed = 'normal'
                Logger().debug("MainController.__onKeyPressed(): 'Home' key pressed; select normal speed")
                self._model.head.setManualSpeed('normal')
                self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_fwd.png").scaled(22, 22))
                self.setStatusbarMessage(self.tr("Manual speed set to normal"), 10)
            event.ignore()

        # 'End' key
        elif event.key() == self.__key['End'] and not event.isAutoRepeat():
            if self.__manualSpeed == 'slow':
                self.__manualSpeed = 'normal'
                Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; select normal speed")
                self._model.head.setManualSpeed('normal')
                self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/player_fwd.png").scaled(22, 22))
                self.setStatusbarMessage(self.tr("Manual speed set to normal"), 10)
            elif self.__manualSpeed == 'normal':
                self.__manualSpeed = 'fast'
                Logger().debug("MainController.__onKeyPressed(): 'End' key pressed; select fast speed")
                self._model.head.setManualSpeed('fast')
                self._view.manualSpeedLabel.setPixmap(QtGui.QPixmap(":/icons/messagebox_warning.png").scaled(22, 22))
                self.setStatusbarMessage(self.tr("Manual speed set to fast"), 10)
            event.ignore()

        # 'Escape' key
        elif event.key() == self.__key['Escape'] and not event.isAutoRepeat():
            Logger().debug("MainController.__onKeyPressed(): 'Escape' key pressed")
            dialog = YesNoMessageDialog(self.tr("About to Quit"), self.tr("Are you sure you want to quit Papywizard?"))
            response = dialog.exec_()
            if response == QtGui.QMessageBox.Yes:
                self.__stopConnection()
                QtGui.QApplication.quit()
            event.ignore()

        else:
            event.accept()

    def __onKeyReleased(self, event):
        Logger().debug("MainController.__onKeyReleased(): key='%s" % event.key())
        event.accept()

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
            self.__startConnection()
        else:
            self.__stopConnection()

    def __onActionHardwareSetLimitYawMinusActivated(self):
        yaw, pitch = self._model.head.readPosition()
        self._model.head.setLimit('yaw', '-', yaw)
        Logger().debug("MainController.__onActionHardwareSetLimitYawMinusActivated(): yaw minus limit set to %.1f" % yaw)
        self.setStatusbarMessage(self.tr("Yaw - limit set"), 10)

    def __onActionHardwareSetLimitYawPlusActivated(self):
        yaw, pitch = self._model.head.readPosition()
        self._model.head.setLimit('yaw', '+', yaw)
        Logger().debug("MainController.__onActionHardwareSetLimitYawPlusActivated(): yaw plus limit set to %.1f" % yaw)
        self.setStatusbarMessage(self.tr("Yaw + limit set"), 10)

    def __onActionHardwareSetLimitPitchPlusActivated(self):
        yaw, pitch = self._model.head.readPosition()
        self._model.head.setLimit('pitch', '+', pitch)
        Logger().debug("MainController.__onActionHardwareSetLimitPitchPlusActivated(): pitch plus limit set to %.1f" % pitch)
        self.setStatusbarMessage(self.tr("Pitch + limit set"), 10)

    def __onActionHardwareSetLimitPitchMinusActivated(self):
        yaw, pitch = self._model.head.readPosition()
        self._model.head.setLimit('pitch', '-', pitch)
        Logger().debug("MainController.__onActionHardwareSetLimitPitchMinusActivated(): pitch minus limit set to %.1f" % pitch)
        self.setStatusbarMessage(self.tr("Pitch - limit set"), 10)

    def __onActionHardwareClearLimitsActivated(self):
        Logger().trace("MainController.__onActionHardwareClearLimitsActivated()")
        self._model.head.clearLimits()
        self.setStatusbarMessage(self.tr("Limits cleared"), 10)

    def __onActionHardwareGotoReferenceActivated(self):
        Logger().trace("MainController.__onActionHardwareGotoReferenceActivated()")
        self.setStatusbarMessage(self.tr("Goto reference position..."))
        self._model.head.gotoPosition(0., 0., wait=False)
        dialog = AbortMessageDialog(self.tr("Goto reference position"), self.tr("Please wait..."))
        dialog.show()
        while self._model.head.isAxisMoving():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)
            if dialog.result() == QtGui.QMessageBox.Abort:
                self._model.head.stopAxis()
                self.setStatusbarMessage(self.tr("Operation aborted"), 10)
                break
            time.sleep(0.01)
        else:
            self.setStatusbarMessage(self.tr("Reference position reached"), 10)
        dialog.hide()

    def __onActionHardwareGotoInitialActivated(self):
        Logger().trace("MainController.__onActionHardwareGotoInitialActivated()")
        self.setStatusbarMessage(self.tr("Goto initial position..."))
        while QtGui.QApplication.hasPendingEvents():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)
        self._model.head.gotoPosition(0., 0., useOffset=False, wait=False)
        dialog = AbortMessageDialog(self.tr("Goto initial position"), self.tr("Please wait..."))
        dialog.show()
        while self._model.head.isAxisMoving():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)
            if dialog.result() == QtGui.QMessageBox.Abort:
                self._model.head.stopAxis()
                self.setStatusbarMessage(self.tr("Operation aborted"), 10)
                break
            time.sleep(0.01)
        else:
            self.setStatusbarMessage(self.tr("Initial position reached"), 10)
        dialog.hide()

    def __onActionHardwarePluginsActivated(self):
        Logger().trace("MainController.__onActionHardwarePluginsActivated()")
        self.__openPluginsDialog()

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
        controller.exec_()
        controller.shutdown()

    def __onActionHelpAboutPapywizardActivated(self):
        Logger().trace("MainController.__onActionHelpAboutPapywizardActivated()")
        controller = HelpAboutController(self, self._model)
        controller.exec_()
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

    def __onSetCorner0PushButtonClicked(self):
        Logger().trace("MainController.__onSetCorner0PushButtonClicked()")
        self.__yawPos, self.__pitchPos = self._model.head.readPosition()
        self._model.mosaic.corners[0]['yaw'], self._model.mosaic.corners[0]['pitch'] = self.__yawPos, self.__pitchPos
        self.__mosaicInputParam = 'corners'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Yaw/pitch corner 0 set from current position"), 10)

    def __onSetYawCorner0PushButtonClicked(self):
        Logger().trace("MainController.__onSetYawStartPushButtonClicked()")
        self.__yawPos, self.__pitchPos = self._model.head.readPosition()
        self._model.mosaic.corners[0]['yaw'] = self.__yawPos
        self.__mosaicInputParam = 'corners'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Yaw corner 0 set from current position"), 10)

    def __onSetPitchCorner0PushButtonClicked(self):
        Logger().trace("MainController.__onSetPitchCorner0PushButtonClicked()")
        self.__yawPos, self.__pitchPos = self._model.head.readPosition()
        self._model.mosaic.corners[0]['pitch'] = self.__pitchPos
        self.__mosaicInputParam = 'corners'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Pitch corner 0 set from current position"), 10)

    def __onSetCorner1PushButtonClicked(self):
        Logger().trace("MainController.__onSetCorner1PushButtonClicked()")
        self.__yawPos, self.__pitchPos = self._model.head.readPosition()
        self._model.mosaic.corners[1]['yaw'], self._model.mosaic.corners[1]['pitch'] = self.__yawPos, self.__pitchPos
        self.__mosaicInputParam = 'corners'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Yaw/pitch corner 1 set from current position"), 10)

    def __onSetYawCorner1PushButtonClicked(self):
        Logger().trace("MainController.__onSetYawCorner1PushButtonClicked()")
        self.__yawPos, self.__pitchPos = self._model.head.readPosition()
        self._model.mosaic.corners[1]['yaw'] = self.__yawPos
        self.__mosaicInputParam = 'corners'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Yaw corner 1 set from current position"), 10)

    def __onSetPitchCorner1PushButtonClicked(self):
        Logger().trace("MainController.__onSetPitchCorner1PushButtonClicked()")
        self.__yawPos, self.__pitchPos = self._model.head.readPosition()
        self._model.mosaic.corners[1]['pitch'] = self.__pitchPos
        self.__mosaicInputParam = 'corners'
        self.refreshView()
        self.setStatusbarMessage(self.tr("Pitch corner 1 set from current position"), 10)

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
        self._model.head.setReference()
        self.setStatusbarMessage(self.tr("Reference set at current position"), 10)

    def __onYawMovePlusToolButtonPressed(self):
        Logger().trace("MainController.__yawMovePlusToolButtonPressed()")
        self._model.head.startAxis('yaw', '+')

    def __onYawMovePlusToolButtonReleased(self):
        Logger().trace("MainController.__yawMovePlusToolButtonReleased()")
        self._model.head.stopAxis('yaw')
        self.refreshView()

    def __onPitchMovePlusToolButtonPressed(self):
        Logger().trace("MainController.__pitchMovePlusToolButtonPressed()")
        self._model.head.startAxis('pitch', '+')

    def __onPitchMovePlusToolButtonReleased(self):
        Logger().trace("MainController.__pitchMovePlusToolButtonReleased()")
        self._model.head.stopAxis('pitch')
        self.refreshView()

    def __onPitchMoveMinusToolButtonPressed(self):
        Logger().trace("MainController.__onPitchMoveMinusToolButtonPressed()")
        self._model.head.startAxis('pitch', '-')

    def __onPitchMoveMinusToolButtonReleased(self):
        Logger().trace("MainController.__onPitchMoveMinusToolButtonReleased()")
        self._model.head.stopAxis('pitch')
        self.refreshView()

    def __onYawMoveMinusToolButtonPressed(self):
        Logger().trace("MainController.__onYawMoveMinusToolButtonPressed()")
        self._model.head.startAxis('yaw', '-')

    def __onYawMoveMinusToolButtonReleased(self):
        Logger().trace("MainController.__onYawMoveMinusToolButtonReleased()")
        self._model.head.stopAxis('yaw')
        self.refreshView()

    def __onConfigPushButtonClicked(self):
        Logger().trace("MainController.__onConfigPushButtonClicked()")
        self.__openConfigDialog()

    def __onShootPushButtonClicked(self):
        Logger().trace("MainController.__onShootPushButtonClicked()")
        self.__openShootdialog()

    # Helpers
    def __openTotalFovDialog(self):
        """ Open the Total Fov input dialog.
        """
        controller = TotalFovController(self, self._model)
        response = controller.exec_()
        controller.shutdown()
        if response:
            self.__mosaicInputParam = 'fov'
            self.refreshView()
            self.setStatusbarMessage(self.tr("Field of view set to user value"), 10)

    def __openNbPictsDialog(self):
        """ Open the Nb Picts input dialog.
        """
        controller = NbPictsController(self, self._model)
        response = controller.exec_()
        controller.shutdown()
        if response:
            self.__mosaicInputParam = 'nbPicts'
            self.refreshView()
            self.setStatusbarMessage(self.tr("Number of pictures set to user value"), 10)

    def __openPluginsDialog(self):
        """ Open the plugins dialog.
        """
        self.setStatusbarMessage(self.tr("Opening plugins dialog. Please wait..."))
        while QtGui.QApplication.hasPendingEvents():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            controller = PluginsController(self, self._model)
            controller.setSelectedTab(self.__lastPluginsTabSelected)
        finally:
            QtGui.qApp.restoreOverrideCursor()
            self.clearStatusBar()
        response = controller.exec_()
        self.__lastPluginsTabSelected = controller.getSelectedTab()
        controller.shutdown()

    def __openConfigDialog(self):
        """ Open the configuration dialog.
        """
        self.setStatusbarMessage(self.tr("Opening configuration dialog. Please wait..."))
        while QtGui.QApplication.hasPendingEvents():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            #self._view.configPushButton.setEnabled(False)
            controller = ConfigController(self, self._model)
            controller.setSelectedTab(self.__lastConfigTabSelected)
        finally:
            #self._view.configPushButton.setEnabled(True)
            QtGui.qApp.restoreOverrideCursor()
            self.clearStatusBar()
        response = controller.exec_()
        self.__lastConfigTabSelected = controller.getSelectedTab()
        controller.shutdown()

        if response:
            Logger().setLevel(ConfigManager().get('Configuration/LOGGER_LEVEL'))
            if self.__mosaicInputParam == 'corners':
                pass
            elif self.__mosaicInputParam == 'fov':
                yawFov = float(self._view.yawFovLabel.text())
                pitchFov = float(self._view.pitchFovLabel.text())
                self._model.setCornersFromFov(yawFov, pitchFov)
            elif self.__mosaicInputParam == 'nbPicts':
                yawNbPicts = int(self._view.yawNbPictsLabel.text())
                pitchNbPicts = int(self._view.pitchNbPictsLabel.text())
                self._model.setCornersFromNbPicts(yawNbPicts, pitchNbPicts)
            self.refreshView()

    def __openShootdialog(self):
        """ Open teh shooting dialog.
        """
        self.setStatusbarMessage(self.tr("Opening shoot dialog. Please wait..."))
        self._model.setStepByStep(False)
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        while QtGui.QApplication.hasPendingEvents():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)
        try:
            #self._view.shootPushButton.setEnabled(False)
            controller = ShootController(self, self._model)
            if self._view.windowState() & QtCore.Qt.WindowFullScreen:
                controller._view.showFullScreen()
        finally:
            #self._view.shootPushButton.setEnabled(True)
            QtGui.qApp.restoreOverrideCursor()
            self.clearStatusBar()
        controller.exec_()
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
            dialog = ExceptionMessageDialog(self.tr("Can't import preset file"), unicode(msg))
            dialog.exec_()

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
            dialog = ExceptionMessageDialog(self.tr("Can't load style sheet"), unicode(msg))
            dialog.exec_()

    def __SetConnectedWidgetState(self):
        """ Enable/disable widgets when connected.
        """
        self._view.actionHardwareSuspendSpy.setEnabled(True)
        self._view.menuSetLimit.setEnabled(True)
        self._view.actionHardwareClearLimits.setEnabled(True)
        self._view.actionHardwareGotoReference.setEnabled(True)
        self._view.actionHardwareGotoInitial.setEnabled(True)
        self._view.actionHardwarePlugins.setEnabled(False)

        self._view.setCorner0PushButton.setEnabled(True)
        self._view.setYawCorner0PushButton.setEnabled(True)
        self._view.setPitchCorner0PushButton.setEnabled(True)
        self._view.setCorner1PushButton.setEnabled(True)
        self._view.setYawCorner1PushButton.setEnabled(True)
        self._view.setPitchCorner1PushButton.setEnabled(True)
        self._view.totalFovPushButton.setEnabled(True)
        self._view.nbPictsPushButton.setEnabled(True)

        self._view.setReferenceToolButton.setEnabled(True)
        self._view.yawMovePlusToolButton.setEnabled(True)
        self._view.pitchMovePlusToolButton.setEnabled(True)
        self._view.yawMoveMinusToolButton.setEnabled(True)
        self._view.pitchMoveMinusToolButton.setEnabled(True)

        self._view.shootPushButton.setEnabled(True)

    def __SetDisconnectedWidgetState(self):
        """ Enable/disable widgets when disconnected.
        """
        self._view.actionHardwareSuspendSpy.setEnabled(False)
        self._view.menuSetLimit.setEnabled(False)
        self._view.actionHardwareClearLimits.setEnabled(False)
        self._view.actionHardwareGotoReference.setEnabled(False)
        self._view.actionHardwareGotoInitial.setEnabled(False)
        self._view.actionHardwarePlugins.setEnabled(True)

        self._view.setCorner0PushButton.setEnabled(False)
        self._view.setYawCorner0PushButton.setEnabled(False)
        self._view.setPitchCorner0PushButton.setEnabled(False)
        self._view.setCorner1PushButton.setEnabled(False)
        self._view.setYawCorner1PushButton.setEnabled(False)
        self._view.setPitchCorner1PushButton.setEnabled(False)
        self._view.totalFovPushButton.setEnabled(False)
        self._view.nbPictsPushButton.setEnabled(False)

        self._view.setReferenceToolButton.setEnabled(False)
        self._view.yawMovePlusToolButton.setEnabled(False)
        self._view.pitchMovePlusToolButton.setEnabled(False)
        self._view.yawMoveMinusToolButton.setEnabled(False)
        self._view.pitchMoveMinusToolButton.setEnabled(False)

        self._view.shootPushButton.setEnabled(False)

    def __startConnection(self):
        """ Connect to plugins.
        """
        Logger().info("Starting connection. Please wait...")
        self.setStatusbarMessage(self.tr("Starting connection. Please wait..."))
        self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_creating.png").scaled(22, 22))
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        while QtGui.QApplication.hasPendingEvents():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)

        pluginsConnector = PluginsConnector()
        try:
            self.__pluginsStatus = pluginsConnector.start()
        finally:
            self._view.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        # Check connection status
        if self.__pluginsStatus['yawAxis']['init'] and \
           self.__pluginsStatus['pitchAxis']['init'] and \
           self.__pluginsStatus['shutter']['init']:
            if not self._view.actionHardwareSuspendSpy.isChecked():
                Spy().resume()
            else:
                yaw, pitch = self._model.head.readPosition()
                self.__onPositionUpdate(yaw, pitch)
            self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_established.png").scaled(22, 22))
            Logger().info("Connection started")
            self.setStatusbarMessage(self.tr("Connection started"), 10)
            self.__SetConnectedWidgetState()
            self.__pluginsConnected = True
        else:
            Logger().error("Connection failed to start")
            self.setStatusbarMessage(self.tr("Connection failed to start"), 10)
            controller = PluginsStatusController(self, self.__pluginsStatus)
            controller.exec_()
            controller.shutdown()
            self._view.actionHardwareConnect.setChecked(False)
            #self._view.actionHardwareConnect.emit(QtCore.SIGNAL("toggled(bool)"), False)

    def __stopConnection(self):
        """ Disconnect from plugins.
        """
        if self.__pluginsConnected:
            Logger().info("Stopping connection. Please wait...")
            self.setStatusbarMessage(self.tr("Stopping connection. Please wait..."))
            self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_creating.png").scaled(22, 22))
            while QtGui.QApplication.hasPendingEvents():
                QtGui.QApplication.processEvents()
            Spy().suspend()
        self._view.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        if self.__pluginsStatus is not None:
            pluginsConnector = PluginsConnector()
            pluginsConnector.stop(self.__pluginsStatus)

        if self.__pluginsConnected:
            Logger().info("Connection stopped")
            self.setStatusbarMessage(self.tr("Connection stopped"), 10)

        self._view.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self._view.connectLabel.setPixmap(QtGui.QPixmap(":/icons/connect_no.png").scaled(22, 22))
        self.__SetDisconnectedWidgetState()
        self.__pluginsConnected = False

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
        self._view.setYawCorner0PushButton.setText("%.1f" % self._model.mosaic.corners[0]['yaw'])
        self._view.setPitchCorner0PushButton.setText("%.1f" % self._model.mosaic.corners[0]['pitch'])
        self._view.setYawCorner1PushButton.setText("%.1f" % self._model.mosaic.corners[1]['yaw'])
        self._view.setPitchCorner1PushButton.setText("%.1f" % self._model.mosaic.corners[1]['pitch'])
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
