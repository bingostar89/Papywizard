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
from papywizard.controller.messageController import ErrorMessageController
from papywizard.controller.abstractController import AbstractModalDialogController
from papywizard.controller.configController import ConfigController
from papywizard.controller.spy import Spy
from papywizard.view.shootingArea import MosaicArea, PresetArea


class ShootController(AbstractModalDialogController):
    """ Shoot controller object.
    """
    def _init(self):
        self._uiFile = "shootDialog.ui"

        self.__keyPressedDict = {'Right': False,
                                 'Left': False,
                                 'Up': False,
                                 'Down': False,
                                 'Return': False,
                                 'Escape': False
                             }
        #self.__key = {'Right': gtk.keysyms.Right,
                      #'Left': gtk.keysyms.Left,
                      #'Up': gtk.keysyms.Up,
                      #'Down': gtk.keysyms.Down,
                      #'Return': gtk.keysyms.Return,
                      #'Escape': gtk.keysyms.Escape
                      #}

        self.__thread = None
        self.__shootingElapseTimer = QtCore.QTimer()
        QtCore.QCoreApplication.connect(self.__shootingElapseTimer, QtCore.SIGNAL("timeout()"), self.__updateShootingElapsedTime)

    def _initWidgets(self):
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

        # Load graphical shooting area and replace the text view
        #if self._model.mode == 'mosaic':
            #self.shootingArea = MosaicArea() # Use a factory
        #else:
            #self.shootingArea = PresetArea() # Use a factory
        #self.shootingFrame.remove(self.textShootingGridLayout)
        #self.shootingFrame.add(self.shootingArea)
        #self.shootingArea.show()

        # Populate shooting area with preview positions
        if self._model.mode == 'mosaic':

            ## todo: give args in shootingArea.__init__()
            #self.shootingArea.init(self._model.mosaic.yawStart, self._model.mosaic.yawEnd,
                                   #self._model.mosaic.pitchStart, self._model.mosaic.pitchEnd,
                                   #self._model.mosaic.yawFov, self._model.mosaic.pitchFov,
                                   #self._model.camera.getYawFov(self._model.cameraOrientation),
                                   #self._model.camera.getPitchFov(self._model.cameraOrientation),
                                   #self._model.mosaic.yawRealOverlap, self._model.mosaic.pitchRealOverlap)
            self._model.mosaic.generatePositions()
            #for (index, yawIndex, pitchIndex), (yaw, pitch) in self._model.mosaic.iterPositions():
                #self.shootingArea.add_pict(yaw, pitch, status='preview')
        else:
            #self.shootingArea.init(440., 220., # visible fov
                                    #30.,  30.) # camera fov
            self._model.preset.generatePositions()
            #for index, (yaw, pitch) in self._model.preset.iterPositions():
                #self.shootingArea.add_pict(yaw, pitch, status='preview')
        #yaw, pitch = self._model.hardware.readPosition()
        #self.shootingArea.set_current_head_position(yaw, pitch)

        # Set the shooting area size
        #width1, heigh1 = self.shootingArea.size_request()
        #width2, heigh2 = self.textShootingGridLayout.size_request()
        #width = max(width1, width2)
        #heigh = max(heigh1, heigh2)
        #self.shootingArea.set_size_request(width, heigh)
        #self.textShootingGridLayout.set_size_request(width, heigh)

    def _connectQtSignals(self):
        super(ShootController, self)._connectQtSignals()
        #self.shootingArea.connect("button-press-event", self.__onMousePushButtonPressed)
        #self.shootingArea.connect("motion-notify-event", self.__onMotionNotify)
        {"on_dialog_key_press_event": self.__onKeyPressed,
         "on_dialog_key_release_event": self.__onKeyReleased,

         "on_donePushButton_clicked": self.__onDonePushButtonClicked,
     }
        QtCore.QObject.connect(self._view.textViewPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onTextViewPushButtonToggled)
        QtCore.QObject.connect(self._view.rewindPushButton, QtCore.SIGNAL("clicked()"), self.__onRewindPushButtonClicked)
        QtCore.QObject.connect(self._view.forwardPushButton, QtCore.SIGNAL("clicked()"), self.__onForwardPushButtonClicked)

        QtCore.QObject.connect(self._view.dataPushButton, QtCore.SIGNAL("clicked()"), self.__onDataPushButtonClicked)
        QtCore.QObject.connect(self._view.timerPushButton, QtCore.SIGNAL("clicked()"), self.__onTimerPushButtonClicked)
        QtCore.QObject.connect(self._view.stepByStepPushButton, QtCore.SIGNAL("toggled(bool)"), self.__onStepByStepPushButtonToggled)

        QtCore.QObject.connect(self._view.startPushButton, QtCore.SIGNAL("clicked()"), self.__onStartPushButtonClicked)
        QtCore.QObject.connect(self._view.pauseResumePushButton, QtCore.SIGNAL("clicked()"), self.__onPauseResumePushButtonClicked)
        QtCore.QObject.connect(self._view.stopPushButton, QtCore.SIGNAL("clicked()"), self.__onStopPushButtonClicked)

    def _connectSignals(self):
        Spy().newPosSignal.connect(self.__refreshPos)
        self._model.startedSignal.connect(self.__shootingStarted)
        self._model.pausedSignal.connect(self.__shootingPaused)
        self._model.resumedSignal.connect(self.__shootingResumed)
        self._model.stoppedSignal.connect(self.__shootingStopped)
        self._model.waitingSignal.connect(self.__shootingWaiting)
        self._model.progressSignal.connect(self.__shootingProgress)
        self._model.repeatSignal.connect(self.__shootingRepeat)
        self._model.newPositionSignal.connect(self.__shootingNewPosition)
        self._model.sequenceSignal.connect(self.__shootingSequence)

    def _disconnectSignals(self):
        Spy().newPosSignal.disconnect(self.__refreshPos)
        self._model.startedSignal.disconnect(self.__shootingStarted)
        self._model.pausedSignal.disconnect(self.__shootingPaused)
        self._model.resumedSignal.disconnect(self.__shootingResumed)
        self._model.stoppedSignal.disconnect(self.__shootingStopped)
        self._model.waitingSignal.disconnect(self.__shootingWaiting)
        self._model.progressSignal.disconnect(self.__shootingProgress)
        self._model.repeatSignal.connect(self.__shootingRepeat)
        self._model.newPositionSignal.disconnect(self.__shootingNewPosition)
        self._model.sequenceSignal.disconnect(self.__shootingSequence)

    #def _onDelete(self, widget, event):
        #Logger().trace("ShootController.__onDelete()")
        #if not self._model.isShooting():
            #self.shutdown()
            #return False
        #return True

    # Callbacks GTK
    def __onKeyPressed(self, widget, event, *args):

        # 'Right' key
        if event.keyval == self.__key['Right']:
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left']:
                if self._model.isPaused():
                    Logger().debug("MainController.__onKeyPressed(): 'Right' key pressed; forward shooting position")
                    self.__keyPressedDict['Right'] = True
                    self.__forwardShootingPosition()
            return True

        # 'Left' key
        elif event.keyval == self.__key['Left']:
            if not self.__keyPressedDict['Left'] and not self.__keyPressedDict['Right']:
                if self._model.isPaused():
                    Logger().debug("MainController.__onKeyPressed(): 'Left' key pressed; rewind shooting position")
                    self.__keyPressedDict['Left'] = True
                    self.__rewindShootingPosition()
            return True

        # 'Up' key
        elif event.keyval == self.__key['Up']:
            if not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                if self._model.isPaused():
                    Logger().debug("MainController.__onKeyPressed(): 'Up' key pressed; rewind shooting position")
                    self.__keyPressedDict['Up'] = True
                    self.__rewindShootingPosition()
            return True

        # 'Down' key
        elif event.keyval == self.__key['Down']:
            if not self.__keyPressedDict['Down'] and not self.__keyPressedDict['Up']:
                if self._model.isPaused():
                    Logger().debug("MainController.__onKeyPressed(): 'Down' key pressed; forward shooting position")
                    self.__keyPressedDict['Down'] = True
                    self.__forwardShootingPosition()
            return True

        # 'Return' key
        if event.keyval == self.__key['Return']:
            if not self.__keyPressedDict['Return']:
                Logger().debug("shootController.__onKeyPressed(): 'Return' key pressed")
                self.__keyPressedDict['Return'] = True

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
                return True

        # 'Escape' key
        elif event.keyval == self.__key['Escape']:
           if not self.__keyPressedDict['Escape']:
               Logger().debug("shootController.__onKeyPressed(): 'Escape' key pressed")
               self.__keyPressedDict['Escape'] = True

               # Pressing 'Escape' while not shooting exit shoot dialog
               if not self._model.isShooting():
                   Logger().debug("shootController.__onKeyPressed(): close shooting dialog")
                   self.shutdown()

               # Pressing 'Escape' while shooting stops shooting
               else:
                   Logger().debug("shootController.__onKeyPressed(): stop shooting")
                   self.__stopShooting()
               return True

        else:
            Logger().warning("MainController.__onKeyPressed(): unbind '%s' key" % event.keyval)

    def __onKeyReleased(self, widget, event, *args):

        # 'Right' key
        if event.keyval == self.__key['Right']:
            if self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyReleased(): 'Right' key released")
                self.__keyPressedDict['Right'] = False
            return True

        # 'Left' key
        if event.keyval == self.__key['Left']:
            if self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyReleased(): 'Left' key released")
                self.__keyPressedDict['Left'] = False
            return True

        # 'Up' key
        if event.keyval == self.__key['Up']:
            if self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyReleased(): 'Up' key released;")
                self.__keyPressedDict['Up'] = False
            return True

        # 'Down' key
        if event.keyval == self.__key['Down']:
            if self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyReleased(): 'Down' key released;")
                self.__keyPressedDict['Down'] = False
            return True

        # 'Return' key
        if event.keyval == self.__key['Return']:
            if self.__keyPressedDict['Return']:
                Logger().debug("MainController.__onKeyReleased(): 'Return' key released")
                self.__keyPressedDict['Return'] = False
            return True

        # 'Escape' key
        if event.keyval == self.__key['Escape']:
            if self.__keyPressedDict['Escape']:
                Logger().debug("MainController.__onKeyReleased(): 'Escape' key released")
                self.__keyPressedDict['Escape'] = False
            return True

        else:
            Logger().warning("MainController.__onKeyReleased(): unbind '%s' key" % event.keyval)

    def __onMousePushButtonPressed(self, widget, event):
        Logger().trace("ShootController.__onMousePushButtonPressed()")
        if self._model.isPaused():
            if event.button == 1:
                #index = self._view.shootingArea.get_selected_image_index(event.x, event.y)
                if index is not None:
                    Logger().debug("ShootController.__onMousePushButtonPressed(): x=%d, y=%d, index=%d" % (event.x, event.y, index))
                    self._model.setNextPositionIndex(index)
                    self.__refreshNextPosition()

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

    def __onTextViewPushButtonToggled(self, checked):
        Logger().trace("ShootController.__onTextViewPushButtonToggled()")
        if checked:
            self._view.shootingFrame.remove(self._view.shootingArea)
            self._view.shootingFrame.add(self._view.textShootingGridLayout)
        else:
            self._view.shootingFrame.remove(self._view.textShootingGridLayout)
            self._view.shootingFrame.add(self._view.shootingArea)

    def __onRewindPushButtonClicked(self):
        Logger().trace("ShootController.__onRewindPushButtonClicked()")
        self.__rewindShootingPosition()

    def __onForwardPushButtonClicked(self):
        Logger().trace("ShootController.__onForwardPushButtonClicked()")
        self.__forwardShootingPosition()

    def __onDataPushButtonClicked(self):
        Logger().trace("ShootController.__onDataPushButtonClicked()")
        #controller = ConfigController(self, self._model, self._serializer)
        #controller.selectPage(5, disable=True)
        #response = controller.exec_()
        #self.refreshView()

    def __onTimerPushButtonClicked(self):
        Logger().trace("ShootController.__onTimerPushButtonClicked()")
        #controller = ConfigController(self, self._model, self._serializer)
        #controller.selectPage(6, disable=True)
        #response = controller.exec_()
        #if self._model.timerRepeatEnable:
            #self._view.repeatLabel.setText("--/%d" % self._model.timerRepeat)
        #else:
            #self._view.repeatLabel.setText("")
        #self.refreshView()

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

    def __updateShootingElapsedTime(self):
        Logger().trace("ShootController.__updateShootingElapsedTime()")
        if self._model.isShooting():
            shootingTime, elapsedTime = self._model.getShootingElapsedTime()
            self._view.shootingTimeLabel.setText("%s" % sToHmsAsStr(shootingTime))
            self._view.elapsedTimeLabel.setText("%s" % sToHmsAsStr(elapsedTime))
        else:
            self.__shootingElapseTimer.stop()

    # Callback model (all GUI calls must be done via the serializer)
    def __shootingStarted(self):
        Logger().trace("ShootController.__shootingStarted()")
        #self._serializer.addWork(self._view.shootingArea.clear)
        self._serializer.addWork(self._view.shootingProgressBar.setValue, 0)
        self._serializer.addWork(self._view.totalProgressBar.setValue, 0)
        if self._model.timerRepeatEnable:
            self._serializer.addWork(self._view.repeatLabel.setText,"--/%d" % self._model.timerRepeat)
        else:
            self._serializer.addWork(self._view.repeatLabel.setText, "")
        self._serializer.addWork(self._view.shootingTimeLabel.setText, "00:00:00")
        self._serializer.addWork(self._view.elapsedTimeLabel.setText,  "00:00:00")
        self._serializer.addWork(self._view.currentIndexLabel.setText, "--/%d" % self._model.scan.totalNbPicts)
        self._serializer.addWork(self._view.nextIndexLabel.setText, "--/%d" % self._model.scan.totalNbPicts)
        if self._model.mode == 'mosaic':
            self._serializer.addWork(self._view.yawCurrentIndexLabel.setText, "--/%d" % self._model.mosaic.yawNbPicts)
            self._serializer.addWork(self._view.pitchCurrentIndexLabel.setText, "--/%d" % self._model.mosaic.pitchNbPicts)
            self._serializer.addWork(self._view.yawNextIndexLabel.setText, "--/%d" % self._model.mosaic.yawNbPicts)
            self._serializer.addWork(self._view.pitchNextIndexLabel.setText, "--/%d" % self._model.mosaic.pitchNbPicts)
        else:
            self._serializer.addWork(self._view.yawCurrentIndexLabel.setText, "--")
            self._serializer.addWork(self._view.pitchCurrentIndexLabel.setText, "--")
            self._serializer.addWork(self._view.yawNextIndexLabel.setText, "--")
            self._serializer.addWork(self._view.pitchNextIndexLabel.setText, "--")
        self._serializer.addWork(self._view.dataPushButton.setEnabled, False)
        self._serializer.addWork(self._view.timerPushButton.setEnabled, False)
        self._serializer.addWork(self._view.startPushButton.setEnabled, False)
        self._serializer.addWork(self._view.pauseResumePushButton.setEnabled, True)
        self._serializer.addWork(self._view.stopPushButton.setEnabled, True)
        self._serializer.addWork(self._view.buttonBox.setEnabled, False)
        self._serializer.addWork(self._view.rewindPushButton.setEnabled, False)
        self._serializer.addWork(self._view.forwardPushButton.setEnabled, False)
        self._serializer.addWork(self.__shootingElapseTimer.start, 1000)

    def __shootingPaused(self):
        Logger().trace("ShootController.__shootingPaused()")
        self._view.pauseResumePushButton.setEnabled(True)
        self._serializer.addWork(self._view.pauseResumePushButton.setText, _("Resume"))
        self._serializer.addWork(self._view.rewindPushButton.setEnabled, True)
        self._serializer.addWork(self._view.forwardPushButton.setEnabled, True)
        self._serializer.addWork(self._view.sequenceLabel.setText, _("Paused"))
        self._serializer.addWork(self._view.textNextLabel.setEnabled, True)
        self._serializer.addWork(self._view.nextIndexLabel.setEnabled, True)
        self._serializer.addWork(self._view.yawNextIndexLabel.setEnabled, True)
        self._serializer.addWork(self._view.pitchNextIndexLabel.setEnabled, True)

    def __shootingResumed(self):
        Logger().trace("ShootController.__shootingResumed()")
        self._serializer.addWork(self._view.pauseResumePushButton.setText, _("Pause"))
        self._serializer.addWork(self._view.rewindPushButton.setEnabled, False)
        self._serializer.addWork(self._view.forwardPushButton.setEnabled, False)
        self._serializer.addWork(self._view.textNextLabel.setEnabled, False)
        self._serializer.addWork(self._view.nextIndexLabel.setEnabled, False)
        self._serializer.addWork(self._view.yawNextIndexLabel.setEnabled, False)
        self._serializer.addWork(self._view.pitchNextIndexLabel.setEnabled, False)

    def __shootingStopped(self, status):
        Logger().debug("ShootController.__shootingStopped(): status=%s" % status)
        if status == 'ok':
            self._serializer.addWork(self._view.sequenceLabel.setText, _("Finished"))
        elif status == 'cancel':
            self._serializer.addWork(self._view.sequenceLabel.setText, _("Canceled"))
        elif status == 'fail':
            self._serializer.addWork(self._view.sequenceLabel.setText, _("Failed"))
        self._serializer.addWork(self._view.dataPushButton.setEnabled, True)
        self._serializer.addWork(self._view.timerPushButton.setEnabled, True)
        self._serializer.addWork(self._view.startPushButton.setEnabled, True)
        self._serializer.addWork(self._view.pauseResumePushButton.setEnabled, False)
        self._serializer.addWork(self._view.stopPushButton.setEnabled, False)
        self._serializer.addWork(self._view.buttonBox.setEnabled, True)

    def __shootingWaiting(self, wait):
        Logger().trace("ShootController.__shootingRepeat()")
        sequenceMessage = _("Waiting") + " %s" % sToHmsAsStr(wait)
        self._serializer.addWork(self._view.sequenceLabel.setText, sequenceMessage)

    def __shootingProgress(self, shootingProgress=None, totalProgress=None):
        Logger().trace("ShootController.__shootingProgress()")
        if shootingProgress is not None:
            self._serializer.addWork(self._view.shootingProgressBar.setValue, int(round(shootingProgress * 100)))
        if totalProgress is not None:
            self._serializer.addWork(self._view.totalProgressBar.setValue, int(round(totalProgress * 100)))

    def __shootingRepeat(self, repeat):
        Logger().trace("ShootController.__shootingRepeat()")
        #self._serializer.addWork(self._view.shootingArea.clear)
        if self._model.timerRepeatEnable:
            self._serializer.addWork(self._view.repeatLabel.setText,"%d/%d" % (repeat, self._model.timerRepeat))

    def __shootingNewPosition(self, index, yaw, pitch, status=None, next=False):
        Logger().trace("ShootController.__shootingNewPosition()")

        # Update text area
        if isinstance(index, tuple):
            index, yawIndex, pitchIndex = index
            self._serializer.addWork(self._view.yawCurrentIndexLabel.setText, "%d/%d" % (yawIndex, self._model.mosaic.yawNbPicts))
            self._serializer.addWork(self._view.yawNextIndexLabel.setText, "%d/%d" % (yawIndex, self._model.mosaic.yawNbPicts))
            self._serializer.addWork(self._view.pitchCurrentIndexLabel.setText, "%d/%d" % (pitchIndex, self._model.mosaic.pitchNbPicts))
            self._serializer.addWork(self._view.pitchNextIndexLabel.setText, "%d/%d" % (pitchIndex, self._model.mosaic.pitchNbPicts))
        else:
            self._serializer.addWork(self._view.yawCurrentIndexLabel.setText, "%.1f" % yaw)
            self._serializer.addWork(self._view.yawNextIndexLabel.setText, "%.1f" % yaw)
            self._serializer.addWork(self._view.pitchCurrentIndexLabel.setText, "%.1f" % pitch)
            self._serializer.addWork(self._view.pitchNextIndexLabel.setText, "%.1f" % pitch)
        self._serializer.addWork(self._view.currentIndexLabel.setText, "%d/%d" % (index, self._model.scan.totalNbPicts))
        self._serializer.addWork(self._view.nextIndexLabel.setText, "%d/%d" % (index, self._model.scan.totalNbPicts))

        # Update graphical area
        #self._view.shootingArea.add_pict(yaw, pitch, status, next)
        #self._serializer.addWork(self._view.shootingArea.refresh)

    def __shootingSequence(self, sequence, **kwargs):
        Logger().trace("ShootController.__shootingSequence()")
        if sequence == 'moving':
            self._serializer.addWork(self._view.sequenceLabel.setText, _("Moving"))
        elif sequence == 'stabilization':
            self._serializer.addWork(self._view.sequenceLabel.setText, _("Stabilization"))
        elif sequence == 'mirror':
            self._serializer.addWork(self._view.sequenceLabel.setText, _("Mirror lockup"))
        elif sequence == 'shutter':
            bracket = kwargs['bracket']
            totalNbPicts = self._model.camera.bracketingNbPicts
            self._serializer.addWork(self._view.sequenceLabel.setText, _("Shutter - Picture") + " %d/%d" % (bracket, totalNbPicts))

    def __refreshPos(self, yaw, pitch):
        Logger().trace("ShootController.__refreshPos()")
        #self.shootingArea.set_current_head_position(yaw, pitch)
        #self._serializer.addWork(self._view.shootingArea.refresh)

    # Helpers
    def __refreshNextPosition(self):
        index = self._model.getShootingIndex() # getNexPositionIndex()
        index, (yaw, pitch) = self._model.scan.getPositionAtIndex(index)

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
        #self._view.shootingArea.set_selected_image_index(index)

    def __rewindShootingPosition(self):
        """
        """
        index = self._model.getShootingIndex()
        Logger().debug("ShootController.__rewindShootingPosition(): old index=%d" % index)
        try:
            self._model.setNextPositionIndex(index - 1)
            self.__refreshNextPosition()
            Logger().debug("ShootController.__rewindShootingPosition():new index=%d" % (index - 1))
        except IndexError:
            Logger().exception("ShootController.__rewindShootingPosition()", debug=True)

    def __forwardShootingPosition(self):
        """
        """
        index = self._model.getShootingIndex()
        Logger().debug("ShootController.__forwardShootingPosition(): old index=%d" % index)
        try:
            self._model.setNextPositionIndex(index + 1)
            self.__refreshNextPosition()
            Logger().debug("ShootController.__forwardShootingPosition(): new index=%d" % (index + 1))
        except IndexError:
            Logger().exception("ShootController.__forwardShootingPosition()", debug=True)

    def __startShooting(self):

        # Join previous thread, if any
        if self.__thread is not None:
            self.__thread.join()

        # Start new shooting thread
        self.__thread = threading.Thread(target=self._model.start, name="Shooting")
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
            self.__thread.join()

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
