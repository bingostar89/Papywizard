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

- ShootController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
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
from papywizard.controller.spy import Spy
from papywizard.view.shootingScene import ShootingView, MosaicShootingScene, PresetShootingScene


class ShootController(AbstractModalDialogController):
    """ Shoot controller object.
    """
    def _init(self):
        self._uiFile = "shootDialog.ui"

        self.__keyPressedDict = {'Right': False,
                                 'Left': False,
                                 'Up': False,
                                 'Down': False,
                             }
        self.__key = {'Right': QtCore.Qt.Key_Right,
                      'Left': QtCore.Qt.Key_Left,
                      'Up': QtCore.Qt.Key_Up,
                      'Down': QtCore.Qt.Key_Down,
                      'Return': QtCore.Qt.Key_Return,
                      'Escape': QtCore.Qt.Key_Escape
                      }

        self.__thread = None
        self.__shootingElapseTimer = QtCore.QTimer()
        QtCore.QCoreApplication.connect(self.__shootingElapseTimer, QtCore.SIGNAL("timeout()"), self.__updateShootingElapsedTime)

    def _initWidgets(self):

        # Let the dialog be managed as a window so it can
        # be displayed fullscreen on Nokia N8x0 devices
        self._view.setWindowFlags(QtCore.Qt.Window)

        if self._model.timerRepeatEnable:
            self._view.repeatLabel.setText("--/%d" % self._model.timerRepeat)
        else:
            self._view.repeatLabel.setText("")

        # Init text view
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
                                                       60,
                                                       60)

        # Assign shooting scene to view
        self._view.shootingGraphicsView.setScene(self.__shootingScene)

        # Populate shooting scene with preview positions
        self._model.scan.generatePositions()
        while True:
            try:
                index, (yaw, pitch) = self._model.scan.getCurrentPosition()
                if isinstance(index, tuple):
                    index, yawIndex, pitchIndex = index
                self.__shootingScene.addPicture(index, yaw, pitch, 'preview')
                self._model.scan.index += 1
            except IndexError:
                Logger().exception("ShootController._initWidgets()", debug=True)
                break

        # Connect picture clicked signal
        self.connect(self.__shootingScene, QtCore.SIGNAL("pictureClicked"), self.__onPictureClicked)

        # Refresh head position
        yaw, pitch = self._model.hardware.readPosition()
        self.__shootingScene.setHeadPosition(yaw, pitch)

        # Select next picture position
        self.__shootingScene.selectNextPicture(1)

        # Keyboard behaviour
        self._view.grabKeyboard()

    def _connectQtSignals(self):
        super(ShootController, self)._connectQtSignals()

        self.connect(self._view.shootingStackPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onShootingStackPushButtonToggled)
        self.connect(self._view.rewindPushButton, QtCore.SIGNAL("clicked()"), self.__onRewindPushButtonClicked)
        self.connect(self._view.forwardPushButton, QtCore.SIGNAL("clicked()"), self.__onForwardPushButtonClicked)

        self.connect(self._view.dataPushButton, QtCore.SIGNAL("clicked()"), self.__onDataPushButtonClicked)
        self.connect(self._view.timerPushButton, QtCore.SIGNAL("clicked()"), self.__onTimerPushButtonClicked)
        self.connect(self._view.stepByStepPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onStepByStepPushButtonToggled)

        self.connect(self._view.startPushButton, QtCore.SIGNAL("clicked()"), self.__onStartPushButtonClicked)
        self.connect(self._view.pauseResumePushButton, QtCore.SIGNAL("clicked()"), self.__onPauseResumePushButtonClicked)
        self.connect(self._view.stopPushButton, QtCore.SIGNAL("clicked()"), self.__onStopPushButtonClicked)

    def _connectSignals(self):
        self.connect(Spy(), QtCore.SIGNAL("update"), self.__onUpdatePosition, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("started"), self.__shootingStarted, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("paused"), self.__shootingPaused, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("resumed"), self.__shootingResumed, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("stopped"), self.__shootingStopped, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("waiting"), self.__shootingWaiting, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("progress"), self.__shootingProgress, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("repeat"), self.__shootingRepeat, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("update"), self.__shootingUpdate, QtCore.Qt.BlockingQueuedConnection)
        self.connect(self._model, QtCore.SIGNAL("sequence"), self.__shootingSequence, QtCore.Qt.BlockingQueuedConnection)

        self._view.keyPressEvent = self.__onKeyPressed
        self._view.keyReleaseEvent = self.__onKeyReleased

    def _disconnectSignals(self):
        self.disconnect(Spy(), QtCore.SIGNAL("update"), self.__onUpdatePosition)
        self.disconnect(self._model, QtCore.SIGNAL("started"), self.__shootingStarted)
        self.disconnect(self._model, QtCore.SIGNAL("paused"), self.__shootingPaused)
        self.disconnect(self._model, QtCore.SIGNAL("resumed"), self.__shootingResumed)
        self.disconnect(self._model, QtCore.SIGNAL("stopped"), self.__shootingStopped)
        self.disconnect(self._model, QtCore.SIGNAL("waiting"), self.__shootingWaiting)
        self.disconnect(self._model, QtCore.SIGNAL("progress"), self.__shootingProgress)
        self.disconnect(self._model, QtCore.SIGNAL("repeat"), self.__shootingRepeat)
        self.disconnect(self._model, QtCore.SIGNAL("update"), self.__shootingUpdate)
        self.disconnect(self._model, QtCore.SIGNAL("sequence"), self.__shootingSequence)

    # Callbacks Qt
    def _onCloseEvent(self, event):
        Logger().trace("ShootController._onCloseEvent()")
        if not self._model.isShooting():
            self.shutdown()
            event.accept()
        else:
            event.ignore()

    def __onKeyPressed(self, event):
        #Logger().debug("MainController.__onKeyPressed(): key='%s" % event.key())

        # 'Right' key
        if event.key() == self.__key['Right']:
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left']:
                if self._model.isPaused():
                    Logger().debug("MainController.__onKeyPressed(): 'Right' key pressed; forward shooting position")
                    self.__keyPressedDict['Right'] = True
                    self.__forwardShootingPosition()
            event.ignore()

        # 'Left' key
        elif event.key() == self.__key['Left']:
            if not self.__keyPressedDict['Left'] and not self.__keyPressedDict['Right']:
                if self._model.isPaused():
                    Logger().debug("MainController.__onKeyPressed(): 'Left' key pressed; rewind shooting position")
                    self.__keyPressedDict['Left'] = True
                    self.__rewindShootingPosition()
            event.ignore()

        # 'Up' key
        elif event.key() == self.__key['Up']:
            if not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                if self._model.isPaused():
                    Logger().debug("MainController.__onKeyPressed(): 'Up' key pressed; rewind shooting position")
                    self.__keyPressedDict['Up'] = True
                    self.__rewindShootingPosition()
            event.ignore()

        # 'Down' key
        elif event.key() == self.__key['Down']:
            if not self.__keyPressedDict['Down'] and not self.__keyPressedDict['Up']:
                if self._model.isPaused():
                    Logger().debug("MainController.__onKeyPressed(): 'Down' key pressed; forward shooting position")
                    self.__keyPressedDict['Down'] = True
                    self.__forwardShootingPosition()
            event.ignore()

        # 'Return' key
        if event.key() == self.__key['Return']:
            Logger().debug("shootController.__onKeyPressed(): 'Return' key pressed")

            # Pressing 'Return' while not shooting starts shooting
            if not self._model.isShooting():
                Logger().debug("shootController.__onKeyPressed(): start shooting")
                self.__startShooting()

            # Pressing 'Return' while shooting...
            else:

                # ...and not paused pauses shooting
                if not self._model.isPaused():
                    Logger().debug("shootController.__onKeyPressed(): pause shooting")
                    self.__pauseShooting()

                #... and paused resumes shooting
                else:
                    Logger().debug("shootController.__onKeyPressed(): resume shooting")
                    self.__resumeShooting()
            event.ignore()

        # 'Escape' key
        elif event.key() == self.__key['Escape']:
            Logger().debug("shootController.__onKeyPressed(): 'Escape' key pressed")

            # Pressing 'Escape' while not shooting exit shoot dialog
            if not self._model.isShooting():
                Logger().debug("shootController.__onKeyPressed(): close shooting dialog")
                self._view.reject()

            # Pressing 'Escape' while shooting stops shooting
            else:
                Logger().debug("shootController.__onKeyPressed(): stop shooting")
                self.__stopShooting()
            event.ignore()

        else:
            event.accept()

    def __onKeyReleased(self, event):
        #Logger().debug("MainController.__onKeyReleased(): key='%s" % event.key())

        # 'Right' key
        if event.key() == self.__key['Right']:
            if self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyReleased(): 'Right' key released")
                self.__keyPressedDict['Right'] = False
            event.ignore()

        # 'Left' key
        if event.key() == self.__key['Left']:
            if self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyReleased(): 'Left' key released")
                self.__keyPressedDict['Left'] = False
            event.ignore()

        # 'Up' key
        if event.key() == self.__key['Up']:
            if self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyReleased(): 'Up' key released;")
                self.__keyPressedDict['Up'] = False
            event.ignore()

        # 'Down' key
        if event.key() == self.__key['Down']:
            if self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyReleased(): 'Down' key released;")
                self.__keyPressedDict['Down'] = False
            event.ignore()

        else:
            event.accept()

    def __onMotionNotify(self, widget, event):
        #Logger().trace("ShootController.__onMotionNotify()")
        if self._model.isPaused():
            if event.is_hint:
                Logger().trace("ShootController.__onMotionNotify(): is_hint")
                x, y, state = event.window.get_pointer()
            else:
                x = event.x
                y = event.y
                state = event.state

            if state & gtk.gdk.BUTTON1_MASK:
                Logger().debug("ShootController.__onMotionNotify(): drag x=%d, y=%d" % (x, y))

    def __onShootingStackPushButtonToggled(self, checked):
        Logger().trace("ShootController.__onShootingStackPushButtonToggled()")
        if checked:
            self._view.shootingStackedWidget.setCurrentIndex(1)
        else:
            self._view.shootingStackedWidget.setCurrentIndex(0)

    def __onRewindPushButtonClicked(self):
        Logger().trace("ShootController.__onRewindPushButtonClicked()")
        self.__rewindShootingPosition()

    def __onForwardPushButtonClicked(self):
        Logger().trace("ShootController.__onForwardPushButtonClicked()")
        self.__forwardShootingPosition()

    def __onDataPushButtonClicked(self):
        Logger().trace("ShootController.__onDataPushButtonClicked()")
        controller = ConfigController(self, self._model)
        controller.selectTab(5, disable=True)
        response = controller.exec_()
        self.refreshView()

    def __onTimerPushButtonClicked(self):
        Logger().trace("ShootController.__onTimerPushButtonClicked()")
        controller = ConfigController(self, self._model)
        controller.selectTab(6, disable=True)
        response = controller.exec_()
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
        else:
            self._view.stepByStepPushButton.setIcon(QtGui.QIcon(":/icons/button_cancel.png"))

    def __onStartPushButtonClicked(self):
        Logger().trace("ShootController.__startPushButtonClicked()")
        self.__startShooting()

    def __onPauseResumePushButtonClicked(self):
        Logger().trace("ShootController.__onPauseResumePushButtonClicked()")
        if self._model.isShooting(): # Should always be true here, but...
            if not self._model.isPaused():
                self.__pauseShooting() # Not used
            else:
                self.__resumeShooting()

    def __onStopPushButtonClicked(self):
        Logger().trace("ShootController.__stopPushButtonClicked()")
        self.__stopShooting()

    def __onDonePushButtonClicked(self):
        Logger().trace("ShootController.__onDonePushButtonClicked()")
        self.shutdown()

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
    def __shootingStarted(self):
        Logger().trace("ShootController.__shootingStarted()")
        self.__shootingScene.clear()
        self._view.shootingProgressBar.setValue(0)
        self._view.totalProgressBar.setValue(0)
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
        self._view.dataPushButton.setEnabled(False)
        self._view.timerPushButton.setEnabled(False)
        self._view.startPushButton.setEnabled(False)
        self._view.pauseResumePushButton.setEnabled(True)
        self._view.stopPushButton.setEnabled(True)
        self._view.buttonBox.setEnabled(False)
        self._view.rewindPushButton.setEnabled(False)
        self._view.forwardPushButton.setEnabled(False)
        self.__shootingElapseTimer.start(1000)

    def __shootingPaused(self):
        Logger().trace("ShootController.__shootingPaused()")
        self._view.pauseResumePushButton.setEnabled(True)
        self._view.pauseResumePushButton.setText(_("Resume"))
        self._view.rewindPushButton.setEnabled(True)
        self._view.forwardPushButton.setEnabled(True)
        self._view.sequenceLabel.setText(_("Paused"))
        self._view.textNextLabel.setEnabled(True)
        self._view.nextIndexLabel.setEnabled(True)
        self._view.yawNextIndexLabel.setEnabled(True)
        self._view.pitchNextIndexLabel.setEnabled(True)

    def __shootingResumed(self):
        Logger().trace("ShootController.__shootingResumed()")
        self._view.pauseResumePushButton.setText(_("Pause"))
        self._view.rewindPushButton.setEnabled(False)
        self._view.forwardPushButton.setEnabled(False)
        self._view.textNextLabel.setEnabled(False)
        self._view.nextIndexLabel.setEnabled(False)
        self._view.yawNextIndexLabel.setEnabled(False)
        self._view.pitchNextIndexLabel.setEnabled(False)

    def __shootingStopped(self, status):
        Logger().debug("ShootController.__shootingStopped(): status=%s" % status)
        if status == 'ok':
            self._view.sequenceLabel.setText( _("Finished"))
        elif status == 'cancel':
            self._view.sequenceLabel.setText(_("Canceled"))
        elif status == 'fail':
            self._view.sequenceLabel.setText(_("Failed"))
        self._view.dataPushButton.setEnabled(True)
        self._view.timerPushButton.setEnabled(True)
        self._view.startPushButton.setEnabled(True)
        self._view.pauseResumePushButton.setEnabled(False)
        self._view.stopPushButton.setEnabled(False)
        self._view.buttonBox.setEnabled(True)

    def __shootingWaiting(self, wait):
        Logger().trace("ShootController.__shootingRepeat()")
        sequenceMessage = _("Waiting") + " %s" % sToHmsAsStr(wait)
        self._view.sequenceLabel.setText(sequenceMessage)

    def __shootingProgress(self, shootingProgress=None, totalProgress=None):
        Logger().trace("ShootController.__shootingProgress()")
        if shootingProgress is not None:
            self._view.shootingProgressBar.setValue(int(round(shootingProgress * 100)))
        if totalProgress is not None:
           self._view.totalProgressBar.setValue(int(round(totalProgress * 100)))

    def __shootingRepeat(self, repeat):
        Logger().trace("ShootController.__shootingRepeat()")
        self.__shootingScene.clear()
        if self._model.timerRepeatEnable:
            self._view.repeatLabel.setText("%d/%d" % (repeat, self._model.timerRepeat))

    def __shootingUpdate(self, index, yaw, pitch, state=None, next=None):
        Logger().trace("ShootController.__shootingUpdate()")

        # Update text area
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
        self._view.currentIndexLabel.setText("%d/%d" % (index, self._model.scan.totalNbPicts))
        self._view.nextIndexLabel.setText("%d/%d" % (index, self._model.scan.totalNbPicts))

        # Update graphical area
        if state is not None:
            self.__shootingScene.setPictureState(index, state)
        if next is True:
            self.__shootingScene.selectNextPicture(index)
        elif next is False:
            self.__shootingScene.selectNextPicture(index + 1)

    def __shootingSequence(self, sequence, bracket=None):
        Logger().trace("ShootController.__shootingSequence()")
        if sequence == 'moving':
            self._view.sequenceLabel.setText(_("Moving"))
        elif sequence == 'stabilization':
            self._view.sequenceLabel.setText(_("Stabilization"))
        elif sequence == 'mirror':
            self._view.sequenceLabel.setText(_("Mirror lockup"))
        elif sequence == 'shutter':
            totalNbPicts = self._model.camera.bracketingNbPicts
            self._view.sequenceLabel.setText(_("Shutter - Picture") + " %d/%d" % (bracket, totalNbPicts))

    def __onUpdatePosition(self, yaw, pitch):
        """ Refresh position according to new pos.

        @param yaw: yaw axis value
        @type yaw: float

        @param pitch: pitch axix value
        @type pitch: float
        """
        #Logger().trace("ShootController.__onUpdatePosition()")
        self.__shootingScene.setHeadPosition(yaw, pitch)

    # Helpers
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

        # Join previous thread, if any
        if self.__thread is not None:
            self.__thread.wait()

        # Start new shooting thread
        self.__thread = ShootingThread(self._model)
        self.__thread.start()

    def __pauseShooting(self):
        self._model.pause()
        self._view.pauseResumePushButton.setEnabled(False)

    def __resumeShooting(self):
        self._model.resume()

    def __stopShooting(self):
        self._model.stop()

    # Interface
    def shutdown(self):
        super(ShootController, self).shutdown()
        if self.__thread is not None:
            self.__thread.wait()

    def refreshView(self):
        dataFlag = ConfigManager().getBoolean('Preferences', 'DATA_FILE_ENABLE')
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
