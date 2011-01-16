# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2010 Frédéric Mantegazza

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

- ShootController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path
import time
import threading

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.common.helpers import sToHmsAsStr
from papywizard.common.configManager import ConfigManager
from papywizard.controller.abstractController import AbstractModalDialogController
from papywizard.controller.configController import ConfigController
from papywizard.controller.counterController import CounterController
from papywizard.controller.spy import Spy
from papywizard.view.shootingScene import ShootingView, MosaicShootingScene, PresetShootingScene


class ShootController(AbstractModalDialogController):
    """ Shoot controller object.
    """
    def _init(self):
        self._uiFile = "shootDialog.ui"

        self.__key = {'Right': QtCore.Qt.Key_Right,
                      'Left': QtCore.Qt.Key_Left,
                      'Up': QtCore.Qt.Key_Up,
                      'Down': QtCore.Qt.Key_Down,
                      'Return': QtCore.Qt.Key_Return,
                      'Escape': QtCore.Qt.Key_Escape
                      }

        self.__thread = None
        self.__shootingElapseTimer = QtCore.QTimer()
        self.connect(self.__shootingElapseTimer, QtCore.SIGNAL("timeout()"), self.__updateShootingElapsedTime)

        # Generate positions
        self._model.scan.generatePositions()

        # Manage spy
        Spy().resume()

    def _initWidgets(self):

        # Let the dialog be managed as a window so it can
        # be displayed fullscreen on Nokia N8x0 devices
        self._view.setWindowFlags(QtCore.Qt.Window)

        # Init state of some widgets
        self.__initWidgetsState()

        # Create graphical shooting view and scene
        self._view.shootingGraphicsView = ShootingView()
        self._view.shootingStackedWidget.insertWidget(0, self._view.shootingGraphicsView)
        self._view.shootingStackedWidget.setCurrentIndex(0)
        if self._model.mode == 'mosaic':  # Use a factory
            self.__shootingScene = MosaicShootingScene(self._model.mosaic.yawStart, self._model.mosaic.yawEnd,
                                                       self._model.mosaic.pitchStart, self._model.mosaic.pitchEnd,
                                                       self._model.mosaic.yawFov, self._model.mosaic.pitchFov,
                                                       self._model.camera.getYawFov(self._model.cameraOrientation),
                                                       self._model.camera.getPitchFov(self._model.cameraOrientation))

        else:
            self.__shootingScene = PresetShootingScene(0, 360,
                                                       -90, 90,
                                                       360, 180,
                                                       30,
                                                       30)

        # Assign shooting scene to view
        self._view.shootingGraphicsView.setScene(self.__shootingScene)

        # Populate shooting scene with preview positions
        self.__generatePreviews()

        # Connect picture clicked signal
        self.connect(self.__shootingScene, QtCore.SIGNAL("pictureClicked"), self.__onPictureClicked)

        # Refresh head position
        yaw, pitch = self._model.head.readPosition()
        self.__shootingScene.setHeadPosition(yaw, pitch)

    def _connectSignals(self):
        AbstractModalDialogController._connectSignals(self)

        self.connect(self._view.shootingStackPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onShootingStackPushButtonToggled)
        #self.connect(self._view.reverseDirectionPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onReverseDirectionPushButtonToggled)
        self.connect(self._view.rewindPushButton, QtCore.SIGNAL("clicked()"), self.__onRewindPushButtonClicked)
        self.connect(self._view.forwardPushButton, QtCore.SIGNAL("clicked()"), self.__onForwardPushButtonClicked)

        self.connect(self._view.dataPushButton, QtCore.SIGNAL("clicked()"), self.__onDataPushButtonClicked)
        self.connect(self._view.timerPushButton, QtCore.SIGNAL("clicked()"), self.__onTimerPushButtonClicked)
        self.connect(self._view.stepByStepPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onStepByStepPushButtonToggled)

        self.connect(self._view.startPushButton, QtCore.SIGNAL("clicked()"), self.__onStartPushButtonClicked)
        self.connect(self._view.pauseResumeStepPushButton, QtCore.SIGNAL("clicked()"), self.__onPauseResumeStepPushButtonClicked)
        self.connect(self._view.stopFinishPushButton, QtCore.SIGNAL("clicked()"), self.__onStopFinishPushButtonClicked)

        self.connect(Spy(), QtCore.SIGNAL("update"), self.__onPositionUpdate, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("started"), self.__onShootingStarted, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("paused"), self.__onShootingPaused, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("resumed"), self.__onShootingResumed, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("stopped"), self.__onShootingStopped, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("waiting"), self.__onShootingWaiting, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("progress"), self.__onShootingProgress, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("repeat"), self.__onShootingRepeat, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("update"), self.__onShootingUpdate, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("sequence"), self.__onShootingSequence, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("beforeRepeat"), self.__onShootingBeforeRepeat, QtCore.Qt.BlockingQueuedConnection)

        self._view._originalKeyPressEvent = self._view.keyPressEvent
        self._view.keyPressEvent = self.__onKeyPressed
        self._view._originalKeyReleaseEvent = self._view.keyReleaseEvent
        self._view.keyReleaseEvent = self.__onKeyReleased

    def _disconnectSignals(self):
        AbstractModalDialogController._disconnectSignals(self)

        self.disconnect(self._view.shootingStackPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onShootingStackPushButtonToggled)
        #self.disconnect(self._view.reverseDirectionPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onReverseDirectionPushButtonToggled)
        self.disconnect(self._view.rewindPushButton, QtCore.SIGNAL("clicked()"), self.__onRewindPushButtonClicked)
        self.disconnect(self._view.forwardPushButton, QtCore.SIGNAL("clicked()"), self.__onForwardPushButtonClicked)

        self.disconnect(self._view.dataPushButton, QtCore.SIGNAL("clicked()"), self.__onDataPushButtonClicked)
        self.disconnect(self._view.timerPushButton, QtCore.SIGNAL("clicked()"), self.__onTimerPushButtonClicked)
        self.disconnect(self._view.stepByStepPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onStepByStepPushButtonToggled)

        self.disconnect(self._view.startPushButton, QtCore.SIGNAL("clicked()"), self.__onStartPushButtonClicked)
        self.disconnect(self._view.pauseResumeStepPushButton, QtCore.SIGNAL("clicked()"), self.__onPauseResumeStepPushButtonClicked)
        self.disconnect(self._view.stopFinishPushButton, QtCore.SIGNAL("clicked()"), self.__onStopFinishPushButtonClicked)

        self.disconnect(Spy(), QtCore.SIGNAL("update"), self.__onPositionUpdate)
        self.disconnect(self._model, QtCore.SIGNAL("started"), self.__onShootingStarted)
        self.disconnect(self._model, QtCore.SIGNAL("paused"), self.__onShootingPaused)
        self.disconnect(self._model, QtCore.SIGNAL("resumed"), self.__onShootingResumed)
        self.disconnect(self._model, QtCore.SIGNAL("stopped"), self.__onShootingStopped)
        self.disconnect(self._model, QtCore.SIGNAL("waiting"), self.__onShootingWaiting)
        self.disconnect(self._model, QtCore.SIGNAL("progress"), self.__onShootingProgress)
        self.disconnect(self._model, QtCore.SIGNAL("repeat"), self.__onShootingRepeat)
        self.disconnect(self._model, QtCore.SIGNAL("update"), self.__onShootingUpdate)
        self.disconnect(self._model, QtCore.SIGNAL("sequence"), self.__onShootingSequence)
        self.disconnect(self._model, QtCore.SIGNAL("beforeRepeat"), self.__onShootingBeforeRepeat)

        self._view.keyPressEvent = self._view._originalKeyPressEvent
        self._view.keyReleaseEvent = self._view._originalKeyReleaseEvent

    # Callbacks Qt
    def _onCloseEvent(self, event):
        Logger().trace("ShootController._onCloseEvent()")
        if not self._model.isShooting():
            self.shutdown()
            event.accept()
        else:
            event.ignore()

    def __onKeyPressed(self, event):
        Logger().debug("MainController.__onKeyPressed(): key='%s" % event.key())

        # 'Escape' key
        if event.key() == self.__key['Escape']:
            Logger().debug("shootController.__onKeyPressed(): 'Escape' key pressed")

            # Pressing 'Escape' while not shooting exit shoot dialog
            if not self._model.isShooting():
                Logger().debug("shootController.__onKeyPressed(): close shooting dialog")
                self._view.reject()

            # Pressing 'Escape' while shooting stops shooting
            #else:
                #Logger().debug("shootController.__onKeyPressed(): stop/finish shooting")
                #self.__stopFinishShooting()
            event.ignore()

        else:
            event.accept()

    def __onKeyReleased(self, event):
        Logger().debug("MainController.__onKeyReleased(): key='%s" % event.key())
        event.accept()

    def __onShootingStackPushButtonToggled(self, checked):
        Logger().debug("ShootController.__onShootingStackPushButtonToggled(): checked=%s" % checked)
        if checked:
            self._view.shootingStackedWidget.setCurrentIndex(1)
        else:
            self._view.shootingStackedWidget.setCurrentIndex(0)

    #def __onReverseDirectionPushButtonToggled(self, checked):
        #Logger().debug("ShootController.__onShootingStackPushButtonToggled(): checked=%s" % checked)
        #self._model.scan.reverseDirection(checked)
        #self.__shootingScene.clear()
        #self.__generatePreviews()  # Can be long!

    def __onRewindPushButtonClicked(self):
        Logger().trace("ShootController.__onRewindPushButtonClicked()")
        self.__rewindShootingPosition()

    def __onForwardPushButtonClicked(self):
        Logger().trace("ShootController.__onForwardPushButtonClicked()")
        self.__forwardShootingPosition()

    def __onDataPushButtonClicked(self):
        Logger().trace("ShootController.__onDataPushButtonClicked()")
        controller = ConfigController(self, self._model)
        controller.selectTab(4, disable=True)
        controller.exec_()
        self.refreshView()

    def __onTimerPushButtonClicked(self):
        Logger().trace("ShootController.__onTimerPushButtonClicked()")
        controller = ConfigController(self, self._model)
        controller.selectTab(5, disable=True)
        controller.exec_()
        if self._model.timerRepeatEnable:
            self._view.repeatLabel.setText("--/%d" % self._model.timerRepeat)
        else:
            self._view.repeatLabel.setText("")
        self.refreshView()

    def __onStepByStepPushButtonToggled(self, checked):
        Logger().trace("ShootController.__onStepByStepPushButtonToggled()")
        self._model.setStepByStep(checked)
        if checked:
            self._view.stepByStepPushButton.setIcon(QtGui.QIcon(":/icons/button_ok.png"))
            self._view.pauseResumeStepPushButton.setText(self.tr("Step"))
            self._view.pauseResumeStepPushButton.setIcon(QtGui.QIcon(":/icons/player_end.png"))
            if not self._model.isPaused():
                self._view.pauseResumeStepPushButton.setEnabled(False)
        else:
            self._view.stepByStepPushButton.setIcon(QtGui.QIcon(":/icons/button_cancel.png"))
            if self._model.isShooting():
                self._view.pauseResumeStepPushButton.setEnabled(True) # Should not be enabled if
                                                                      # a pause request has been asked
            if self._model.isPaused():
                self._view.pauseResumeStepPushButton.setText(self.tr("Resume"))
                self._view.pauseResumeStepPushButton.setIcon(QtGui.QIcon(":/icons/player_pause.png"))
            else:
                self._view.pauseResumeStepPushButton.setText(self.tr("Pause"))
                self._view.pauseResumeStepPushButton.setIcon(QtGui.QIcon(":/icons/player_pause.png"))

    def __onStartPushButtonClicked(self):
        Logger().trace("ShootController.__startPushButtonClicked()")
        self.__startShooting()

    def __onPauseResumeStepPushButtonClicked(self):
        Logger().trace("ShootController.__onPauseResumeStepPushButtonClicked()")
        if self._model.isShooting(): # Should always be true here, but...
            if not self._model.isPaused():
                self.__pauseShooting() # Not used
            else:
                self.__resumeShooting()
                # Use a stepShooting stuff

    def __onStopFinishPushButtonClicked(self):
        Logger().trace("ShootController.__onStopFinishPushButtonClicked()")
        self.__stopFinishShooting()

    def __onPictureClicked(self, index):
        Logger().trace("ShootController.__onPictureClicked(): index=%d" % index)
        if self._model.isPaused():
            self._model.scan.index = index
            self.__refreshNextPosition()
            self._model.forceNewPosition()

    def __updateShootingElapsedTime(self):
        #Logger().trace("ShootController.__updateShootingElapsedTime()")
        if self._model.isShooting():
            shootingTime, elapsedTime = self._model.getShootingElapsedTime()
            self._view.shootingTimeLabel.setText("%s" % sToHmsAsStr(shootingTime))
            self._view.elapsedTimeLabel.setText("%s" % sToHmsAsStr(elapsedTime))
        else:
            self.__shootingElapseTimer.stop()

    # Callback model
    def __onShootingStarted(self):
        Logger().trace("ShootController.__onShootingStarted()")
        self._view.dataPushButton.setEnabled(False)
        self._view.timerPushButton.setEnabled(False)
        self._view.startPushButton.setEnabled(False)
        if not self._view.stepByStepPushButton.isChecked():
            self._view.pauseResumeStepPushButton.setEnabled(True)
        self._view.stopFinishPushButton.setEnabled(True)
        self._view.buttonBox.setEnabled(False)
        self._view.reverseDirectionPushButton.setEnabled(False)
        self._view.rewindPushButton.setEnabled(False)
        self._view.forwardPushButton.setEnabled(False)
        self.__shootingElapseTimer.start(1000)

    def __onShootingPaused(self):
        Logger().trace("ShootController.__onShootingPaused()")
        self._view.pauseResumeStepPushButton.setEnabled(True)
        #if self._view.stepByStepPushButton.isChecked():
            #self._view.pauseResumeStepPushButton.setText(self.tr("Step"))
        #else:
        if not self._view.stepByStepPushButton.isChecked():
            self._view.pauseResumeStepPushButton.setText(self.tr("Resume"))
            self._view.pauseResumeStepPushButton.setIcon(QtGui.QIcon(":/icons/player_pause.png"))
        self._view.rewindPushButton.setEnabled(True)
        self._view.forwardPushButton.setEnabled(True)
        self._view.sequenceLabel.setText(self.tr("Paused"))
        self._view.textNextLabel.setEnabled(True)
        self._view.nextIndexLabel.setEnabled(True)
        self._view.yawNextIndexLabel.setEnabled(True)
        self._view.pitchNextIndexLabel.setEnabled(True)

    def __onShootingResumed(self):
        Logger().trace("ShootController.__onShootingResumed()")
        if not self._view.stepByStepPushButton.isChecked():
            self._view.pauseResumeStepPushButton.setText(self.tr("Pause"))
            self._view.pauseResumeStepPushButton.setIcon(QtGui.QIcon(":/icons/player_pause.png"))
        self._view.rewindPushButton.setEnabled(False)
        self._view.forwardPushButton.setEnabled(False)
        self._view.textNextLabel.setEnabled(False)
        self._view.nextIndexLabel.setEnabled(False)
        self._view.yawNextIndexLabel.setEnabled(False)
        self._view.pitchNextIndexLabel.setEnabled(False)

    def __onShootingStopped(self, status):
        Logger().debug("ShootController.__onShootingStopped(): status=%s" % status)
        if status == 'ok':
            self._view.sequenceLabel.setText( self.tr("Finished"))
        elif status == 'cancel':
            self._view.sequenceLabel.setText(self.tr("Canceled"))
        elif status == 'fail':
            self._view.sequenceLabel.setText(self.tr("Failed"))
        self._view.pauseResumeStepPushButton.setEnabled(False)
        self._view.stopFinishPushButton.setText(self.tr("Finish"))
        self._view.stopFinishPushButton.setIcon(QtGui.QIcon(":/icons/player_eject.png"))

    def __onShootingWaiting(self, wait):
        Logger().trace("ShootController.__onShootingRepeat()")
        sequenceMessage = self.tr("Waiting") + " %s" % sToHmsAsStr(wait)
        self._view.sequenceLabel.setText(sequenceMessage)

    def __onShootingProgress(self, shootingProgress=None, totalProgress=None):
        Logger().trace("ShootController.__onShootingProgress()")
        if shootingProgress is not None:
            self._view.shootingProgressBar.setValue(int(round(shootingProgress * 100)))
        if totalProgress is not None:
           self._view.totalProgressBar.setValue(int(round(totalProgress * 100)))

    def __onShootingRepeat(self, repeat):
        Logger().trace("ShootController.__onShootingRepeat()")
        self.__shootingScene.resetState()
        if self._model.timerRepeatEnable:
            self._view.repeatLabel.setText("%d/%d" % (repeat, self._model.timerRepeat))

    def __onShootingUpdate(self, index, yaw, pitch, state=None, next=None):
        Logger().debug("ShootController.__onShootingUpdate(): index=%s, yaw=%.1f, pitch=%.1f, state=%s, next=%s" % (index, yaw, pitch, state, next))

        # Update text area -> make test on state/next, as for graphical view!
        if isinstance(index, tuple):
            index, yawIndex, pitchIndex = index
            self._view.yawCurrentIndexLabel.setText("%d/%d" % (yawIndex, self._model.mosaic.yawNbPicts))
            self._view.yawNextIndexLabel.setText("%d/%d" % (yawIndex, self._model.mosaic.yawNbPicts))
            self._view.pitchCurrentIndexLabel.setText("%d/%d" % (pitchIndex, self._model.mosaic.pitchNbPicts))
            self._view.pitchNextIndexLabel.setText("%d/%d" % (pitchIndex, self._model.mosaic.pitchNbPicts))
        else:
            self._view.yawCurrentIndexLabel.setText("%.1f" % yaw)
            self._view.yawNextIndexLabel.setText("%.1f" % yaw)
            self._view.pitchCurrentIndexLabel.setText("%.1f" % pitch)
            self._view.pitchNextIndexLabel.setText("%.1f" % pitch)
        if index <= self._model.scan.totalNbPicts:  # Hugly!
            self._view.currentIndexLabel.setText("%d/%d" % (index, self._model.scan.totalNbPicts))
            self._view.nextIndexLabel.setText("%d/%d" % (index, self._model.scan.totalNbPicts))

        # Update graphical area
        if state is not None:
            self.__shootingScene.setPictureState(index, state)
        if next:
            self.__shootingScene.selectNextPicture(index)
        elif next is not None:
            self.__shootingScene.selectNextPicture(index + 1)  # No picture will be selected

    def __onShootingSequence(self, sequence, bracket=None):
        Logger().debug("ShootController.__onShootingSequence(): sequence=%s" % sequence)
        if sequence == 'moving':
            self._view.sequenceLabel.setText(self.tr("Moving"))
        elif sequence == 'stabilization':
            self._view.sequenceLabel.setText(self.tr("Stabilization"))
        elif sequence == 'mirror':
            self._view.sequenceLabel.setText(self.tr("Mirror lockup"))
        elif sequence == 'shutter':
            totalNbPicts = self._model.shutter.bracketingNbPicts
            self._view.sequenceLabel.setText(self.tr("Shutter - Picture") + " %d/%d" % (bracket, totalNbPicts))

    def __onShootingBeforeRepeat(self):
        Logger().trace("ShootController.__onShootingBeforeRepeat()")
        #if self._model.timerReverseDirection:
            #self._model.scan.reverseDirection()
            #self.__shootingScene.clear()
            #self.__generatePreviews()  # Can be long!

    def __onPositionUpdate(self, yaw, pitch):
        """ Refresh position according to new pos.

        @param yaw: yaw axis value
        @type yaw: float

        @param pitch: pitch axix value
        @type pitch: float
        """
        #Logger().trace("ShootController.__onPositionUpdate()")
        self.__shootingScene.setHeadPosition(yaw, pitch)

    # Helpers
    def __generatePreviews(self):
        """ Generate the previews according to scan positions.
        """
        for index, (yaw, pitch) in self._model.scan.getAllPositions():
            if isinstance(index, tuple):
                index, yawIndex, pitchIndex = index
            if self._model.head.isPositionValid(yaw, pitch):
                self.__shootingScene.addPicture(index, yaw, pitch, 'preview')
            else:
                self.__shootingScene.addPicture(index, yaw, pitch, 'invalid')

        # Select next picture position
        self.__shootingScene.selectNextPicture(1)

    def __initWidgetsState(self):
        """ Init widget state.
        """
        self._view.shootingProgressBar.setValue(0)
        self._view.totalProgressBar.setValue(0)
        self._view.sequenceLabel.setText(self.tr("Idle"))
        if self._model.timerRepeatEnable:
            self._view.repeatLabel.setText("--/%d" % self._model.timerRepeat)
        else:
            self._view.repeatLabel.setText("")
        self._view.shootingTimeLabel.setText("00:00:00")
        self._view.elapsedTimeLabel.setText("00:00:00")
        self._view.currentIndexLabel.setText("--/%d" % self._model.scan.totalNbPicts)
        self._view.nextIndexLabel.setText("--/%d" % self._model.scan.totalNbPicts)
        if self._model.mode == 'mosaic':
            self._view.yawCurrentIndexLabel.setText("--/%d" % self._model.mosaic.yawNbPicts)
            self._view.pitchCurrentIndexLabel.setText("--/%d" % self._model.mosaic.pitchNbPicts)
            self._view.yawNextIndexLabel.setText("--/%d" % self._model.mosaic.yawNbPicts)
            self._view.pitchNextIndexLabel.setText("--/%d" % self._model.mosaic.pitchNbPicts)
        else:
            self._view.yawCurrentIndexLabel.setText("--")
            self._view.pitchCurrentIndexLabel.setText("--")
            self._view.yawNextIndexLabel.setText("--")
            self._view.pitchNextIndexLabel.setText("--")

    def __refreshNextPosition(self):
        index, (yaw, pitch) = self._model.scan.getCurrentPosition()

        # Update text area
        if isinstance(index, tuple):
            index, yawIndex, pitchIndex = index
            self._view.yawNextIndexLabel.setText("%d/%d" % (yawIndex, self._model.mosaic.yawNbPicts))
            self._view.pitchNextIndexLabel.setText("%d/%d" % (pitchIndex, self._model.mosaic.pitchNbPicts))
        else:
            self._view.yawNextIndexLabel.setText("%.1f" % yaw)
            self._view.pitchNextIndexLabel.setText("%.1f" % pitch)
        self._view.nextIndexLabel.setText("%d/%d" % (index, self._model.scan.totalNbPicts))

        # Update graphical area
        self.__shootingScene.selectNextPicture(index)

    def __rewindShootingPosition(self):
        """
        """
        Logger().debug("ShootController.__rewindShootingPosition(): old index=%d" % self._model.scan.index)
        try:
            self._model.scan.index -= 1
            self.__refreshNextPosition()
            self._model.forceNewPosition()
            Logger().debug("ShootController.__rewindShootingPosition(): new index=%d" % self._model.scan.index)
        except IndexError:
            Logger().exception("ShootController.__rewindShootingPosition()", debug=True)

    def __forwardShootingPosition(self):
        """
        """
        Logger().debug("ShootController.__forwardShootingPosition(): old index=%d" % self._model.scan.index)
        try:
            self._model.scan.index += 1
            self.__refreshNextPosition()
            self._model.forceNewPosition()
            Logger().debug("ShootController.__forwardShootingPosition(): new index=%d" % self._model.scan.index)
        except IndexError:
            Logger().exception("ShootController.__forwardShootingPosition()", debug=True)

    def __startShooting(self):

        # Show current shooting counter if needed
        if self._model.showShootingCounter:
            Logger().info("Show shooting counter")

            controller = CounterController(self, self._model)
            if self._view.windowState() & QtCore.Qt.WindowFullScreen:
                controller._view.showFullScreen()
            response = controller.exec_()
            controller.shutdown()

        if not self._model.showShootingCounter or response:

            # Join previous thread, if any
            if self.__thread is not None:
                self.__thread.wait()

            # Start new shooting thread
            self.__thread = ShootingThread(self._model)
            self.__thread.start()

    def __pauseShooting(self):
        self._model.pause()
        self._view.pauseResumeStepPushButton.setEnabled(False)

    def __resumeShooting(self):
        if self._view.stepByStepPushButton.isChecked():
            self._view.pauseResumeStepPushButton.setEnabled(False)
        self._model.resume()

    def __stopFinishShooting(self):
        if self._model.isShooting():
            self._model.stop()
        else:
            self.__initWidgetsState()
            if self._model.mode == 'mosaic' and self._model.mosaic.startFrom == 'nearest-corner':
                self._model.scan.generatePositions()
                self.__shootingScene.clear()
                self.__generatePreviews()
            else:
                self.__shootingScene.resetState()

            self._view.dataPushButton.setEnabled(True)
            self._view.timerPushButton.setEnabled(True)
            self._view.startPushButton.setEnabled(True)
            self._view.pauseResumeStepPushButton.setEnabled(False)
            self._view.stopFinishPushButton.setText(self.tr("Stop"))
            self._view.stopFinishPushButton.setIcon(QtGui.QIcon(":/icons/player_stop.png"))
            self._view.stopFinishPushButton.setEnabled(False)
            self._view.buttonBox.setEnabled(True)
            self._view.reverseDirectionPushButton.setEnabled(True)

    # Interface
    def shutdown(self):
        AbstractModalDialogController.shutdown(self)
        if self.__thread is not None:
            self.__thread.wait()

    def refreshView(self):
        dataFlag = ConfigManager().getBoolean('Configuration/DATA_FILE_ENABLE')
        if dataFlag:
            self._view.dataPushButton.setIcon(QtGui.QIcon(":/icons/button_ok.png"))
        else:
            self._view.dataPushButton.setIcon(QtGui.QIcon(":/icons/button_cancel.png"))

        timerFlag = self._model.timerAfterEnable or self._model.timerRepeatEnable
        if timerFlag:
            self._view.timerPushButton.setIcon(QtGui.QIcon(":/icons/button_ok.png"))
        else:
            self._view.timerPushButton.setIcon(QtGui.QIcon(":/icons/button_cancel.png"))


class ShootingThread(QtCore.QThread):
    """ Special thread starting shooting.
    """
    def __init__(self, model, parent=None):
        """ Init the shooting thread.
        """
        QtCore.QThread.__init__(self, parent)
        self.__model = model

    def run(self):
        threading.currentThread().setName("Shooting")
        self.__model.start()
