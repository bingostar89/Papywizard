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

- ShootController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path
import time
import threading

import pygtk
pygtk.require("2.0")
import gtk
import gtk.gdk
import gobject
import pango

from papywizard.common.loggingServices import Logger
from papywizard.common.helpers import sToHmsAsStr
from papywizard.common.configManager import ConfigManager
from papywizard.controller.messageController import ErrorMessageController
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.configController import ConfigController
from papywizard.controller.spy import Spy
from papywizard.view.shootingArea import MosaicArea, PresetArea

if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "common")
else:
    path = os.path.dirname(__file__)


class ShootController(AbstractController):
    """ Shoot controller object.
    """
    def _init(self):
        self._gladeFile = "shootDialog.glade"
        self._signalDict = {"on_textViewTogglebutton_toggled": self.__onTextViewTogglebuttonToggled,
                            "on_rewindButton_clicked": self.__onRewindButtonclicked,
                            "on_forwardButton_clicked": self.__onForwardButtonclicked,
                            "on_stepByStepCheckbutton_toggled": self.__onStepByStepCheckbuttonToggled,
                            "on_dataFileButton_clicked": self.__onDataFileButtonclicked,
                            "on_timerButton_clicked": self.__onTimerButtonClicked,
                            "on_startButton_clicked": self.__onStartButtonClicked,
                            "on_pauseResumeButton_clicked": self.__onPauseResumeButtonClicked,
                            "on_stopButton_clicked": self.__onStopButtonClicked,
                            "on_doneButton_clicked": self.__onDoneButtonClicked,
                        }

        self.__keyPressedDict = {'Right': False,
                                 'Left': False,
                                 'Up': False,
                                 'Down': False,
                                 'Return': False,
                                 'Escape': False
                             }
        self.__key = {'Right': gtk.keysyms.Right,
                      'Left': gtk.keysyms.Left,
                      'Up': gtk.keysyms.Up,
                      'Down': gtk.keysyms.Down,
                      'Return': gtk.keysyms.Return,
                      'Escape': gtk.keysyms.Escape
                      }

        self.__thread = None

    def _retreiveWidgets(self):
        super(ShootController, self)._retreiveWidgets()

        self.viewport = self.wTree.get_widget("viewport")
        self.textShootingArea = self.wTree.get_widget("table")
        self.currentIndexLabel = self.wTree.get_widget("currentIndexLabel")
        self.nextIndexLabel = self.wTree.get_widget("nextIndexLabel")
        self.yawCurrentIndexLabel = self.wTree.get_widget("yawCurrentIndexLabel")
        self.pitchCurrentIndexLabel = self.wTree.get_widget("pitchCurrentIndexLabel")
        self.yawNextIndexLabel = self.wTree.get_widget("yawNextIndexLabel")
        self.pitchNextIndexLabel = self.wTree.get_widget("pitchNextIndexLabel")
        self.repeatLabel = self.wTree.get_widget("repeatLabel")
        self.rewindButton = self.wTree.get_widget("rewindButton")
        self.forwardButton = self.wTree.get_widget("forwardButton")
        self.progressbar = self.wTree.get_widget("progressbar")
        self.stepByStepCheckbutton = self.wTree.get_widget("stepByStepCheckbutton")
        self.dataFileButton = self.wTree.get_widget("dataFileButton")
        self.dataFileButtonImage = self.wTree.get_widget("dataFileButtonImage")
        self.timerButton = self.wTree.get_widget("timerButton")
        self.timerButtonImage = self.wTree.get_widget("timerButtonImage")
        self.startButton = self.wTree.get_widget("startButton")
        self.pauseResumeButton = self.wTree.get_widget("pauseResumeButton")
        self.pauseResumeLabel = self.wTree.get_widget("pauseResumeLabel")
        #self.pauseResumeImage = self.wTree.get_widget("pauseResumeImage")
        self.stopButton = self.wTree.get_widget("stopButton")
        self.doneButton = self.wTree.get_widget("doneButton")

    def _initWidgets(self):

        # Font
        #for i in xrange(1, 7):
            #label = self.wTree.get_widget("textLabel%d" % i)
            #self._setFontParams(label, scale=0.8)
        scale = 1.4
        self._setFontParams(self.currentIndexLabel, scale=scale, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.nextIndexLabel, scale=scale, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.repeatLabel, scale=scale, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.yawCurrentIndexLabel, scale=scale, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.pitchCurrentIndexLabel, scale=scale, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.yawNextIndexLabel, scale=scale, weight=pango.WEIGHT_BOLD)
        self._setFontParams(self.pitchNextIndexLabel, scale=scale, weight=pango.WEIGHT_BOLD)

        # Init text view
        self.currentIndexLabel.set_text(_("--/%d") % self._model.scan.totalNbPicts)
        self.nextIndexLabel.set_text(_("--/%d") % self._model.scan.totalNbPicts)
        if self._model.timerRepeatEnable:
            self.repeatLabel.set_text(_("--/%d") % self._model.timerRepeat)
        else:
            self.repeatLabel.set_text("")
        if self._model.mode == 'mosaic':
            self.yawCurrentIndexLabel.set_text(_("--/%d") % self._model.mosaic.yawNbPicts)
            self.pitchCurrentIndexLabel.set_text(_("--/%d") % self._model.mosaic.pitchNbPicts)
            self.yawNextIndexLabel.set_text(_("--/%d") % self._model.mosaic.yawNbPicts)
            self.pitchNextIndexLabel.set_text(_("--/%d") % self._model.mosaic.pitchNbPicts)
        else:
            self.yawCurrentIndexLabel.set_text("")
            self.pitchCurrentIndexLabel.set_text("")
            self.yawNextIndexLabel.set_text("")
            self.pitchNextIndexLabel.set_text("")

        # Load graphical shooting area and replace the text view
        if self._model.mode == 'mosaic':
            self.shootingArea = MosaicArea() # Use a factory
        else:
            self.shootingArea = PresetArea() # Use a factory
        self.viewport.remove(self.textShootingArea)
        self.viewport.add(self.shootingArea)
        self.shootingArea.show()

        # Populate shooting area with preview positions
        if self._model.mode == 'mosaic':

            # todo: give args in shootingArea.__init__()
            self.shootingArea.init(self._model.mosaic.yawStart, self._model.mosaic.yawEnd,
                                   self._model.mosaic.pitchStart, self._model.mosaic.pitchEnd,
                                   self._model.mosaic.yawFov, self._model.mosaic.pitchFov,
                                   self._model.camera.getYawFov(self._model.cameraOrientation),
                                   self._model.camera.getPitchFov(self._model.cameraOrientation),
                                   self._model.mosaic.yawRealOverlap, self._model.mosaic.pitchRealOverlap)
            self._model.mosaic.generatePositions()
            for (index, yawIndex, pitchIndex), (yaw, pitch) in self._model.mosaic.iterPositions():
                self.shootingArea.add_pict(yaw, pitch, status='preview')
        else:
            self.shootingArea.init(440., 220., # visible fov
                                    16.,  16.) # camera fov
            self._model.preset.generatePositions()
            for index, (yaw, pitch) in self._model.preset.iterPositions():
                self.shootingArea.add_pict(yaw, pitch, status='preview')
        yaw, pitch = self._model.hardware.readPosition()
        self.shootingArea.set_current_head_position(yaw, pitch)

    def _connectSignals(self):
        super(ShootController, self)._connectSignals()

        self.dialog.connect("key-press-event", self.__onKeyPressed)
        self.dialog.connect("key-release-event", self.__onKeyReleased)
        self.dialog.connect("delete-event", self.__onDelete)

        self.shootingArea.connect("button-press-event", self.__onMouseButtonPressed)
        #self.shootingArea.connect("motion-notify-event", self.__onMotionNotify)

        Spy().newPosSignal.connect(self.__refreshPos)
        self._model.startedSignal.connect(self.__shootingStarted)
        self._model.pausedSignal.connect(self.__shootingPaused)
        self._model.resumedSignal.connect(self.__shootingResumed)
        self._model.stoppedSignal.connect(self.__shootingStopped)
        self._model.waitingSignal.connect(self.__shootingWaiting)
        self._model.beginShootSignal.connect(self.__shootingBeginShoot)
        self._model.progressSignal.connect(self.__shootingProgress)
        self._model.repeatSignal.connect(self.__shootingRepeat)
        self._model.newPositionSignal.connect(self.__shootingNewPosition)
        self._model.sequenceSignal.connect(self.__shootingSequence)

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
                   self.dialog.response(0)

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

    def __onDelete(self, widget, event):
        Logger().trace("ShootController.__onDelete()")
        self.__stopShooting() # Freeze if shooting!
        return True

    def __onMouseButtonPressed(self, widget, event):
        Logger().trace("ShootController.__onMouseButtonPressed()")
        if self._model.isPaused():
            if event.button == 1:
                index = self.shootingArea.get_selected_image_index(event.x, event.y)
                if index is not None:
                    Logger().debug("ShootController.__onMouseButtonPressed(): x=%d, y=%d, index=%d" % (event.x, event.y, index))
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

    def __onTextViewTogglebuttonToggled(self, widget):
        Logger().trace("ShootController.__onTextViewTogglebuttonToggled()")
        if widget.get_active():
            self.viewport.remove(self.shootingArea)
            self.viewport.add(self.textShootingArea)
        else:
            self.viewport.remove(self.textShootingArea)
            self.viewport.add(self.shootingArea)

    def __onRewindButtonclicked(self, widget):
        Logger().trace("ShootController.__onRewindButtonclicked()")
        self.__rewindShootingPosition()

    def __onForwardButtonclicked(self, widget):
        Logger().trace("ShootController.__onForwardButtonclicked()")
        self.__forwardShootingPosition()

    def __onStepByStepCheckbuttonToggled(self, widget):
        Logger().trace("ShootController.____onStepByStepCheckbuttonToggled()")
        switch = self.stepByStepCheckbutton.get_active()
        self._model.setManualShoot(switch)

    def __onDataFileButtonclicked(self, widget):
        Logger().trace("ShootController.__onDataFileButtonclicked()")
        controller = ConfigController(self, self._model, self._serializer)
        controller.selectPage(5, disable=True)
        response = controller.run()
        controller.shutdown()
        self.refreshView()

    def __onTimerButtonClicked(self, widget):
        Logger().trace("ShootController.__onTimerButtonClicked()")
        controller = ConfigController(self, self._model, self._serializer)
        controller.selectPage(6, disable=True)
        response = controller.run()
        controller.shutdown()
        #if self._model.timerRepeatEnable:
            #self.repeatLabel.set_text(_("--/%d") % self._model.timerRepeat)
        #else:
            #self.repeatLabel.set_text("")
        self.refreshView()

    def __onStartButtonClicked(self, widget):
        Logger().trace("ShootController.__startButtonClicked()")
        self.__startShooting()

    def __onPauseResumeButtonClicked(self, widget):
        Logger().trace("ShootController.__onPauseResumeButtonClicked()")
        if self._model.isShooting(): # Should always be true here, but...
            if not self._model.isPaused():
                self.__pauseShooting() # Not used
            else:
                self.__resumeShooting()

    def __onStopButtonClicked(self, widget):
        Logger().trace("ShootController.__stopButtonClicked()")
        self.__stopShooting()

    def __onDoneButtonClicked(self, widget):
        Logger().trace("ShootController.__onDoneButtonClicked()")

    # Callback model (all GUI calls must be done via the serializer)
    def __shootingStarted(self):
        Logger().trace("ShootController.__shootingStarted()")
        self._serializer.addWork(self.shootingArea.clear)
        self._serializer.addWork(self.progressbar.set_fraction, 0.)
        self._serializer.addWork(self.currentIndexLabel.set_text, _("--/%d") % self._model.scan.totalNbPicts)
        self._serializer.addWork(self.nextIndexLabel.set_text, _("--/%d") % self._model.scan.totalNbPicts)
        if self._model.timerRepeatEnable:
            self._serializer.addWork(self.repeatLabel.set_text, _("--/%d") % self._model.timerRepeat)
        else:
            self._serializer.addWork(self.repeatLabel.set_text, "")
        if self._model.mode == 'mosaic':
            self._serializer.addWork(self.yawCurrentIndexLabel.set_text, _("--/%d") % self._model.mosaic.yawNbPicts)
            self._serializer.addWork(self.pitchCurrentIndexLabel.set_text, _("--/%d") % self._model.mosaic.pitchNbPicts)
            self._serializer.addWork(self.yawNextIndexLabel.set_text, _("--/%d") % self._model.mosaic.yawNbPicts)
            self._serializer.addWork(self.pitchNextIndexLabel.set_text, _("--/%d") % self._model.mosaic.pitchNbPicts)
        else:
            self._serializer.addWork(self.yawCurrentIndexLabel.set_text, "")
            self._serializer.addWork(self.pitchCurrentIndexLabel.set_text, "")
            self._serializer.addWork(self.yawNextIndexLabel.set_text, "")
            self._serializer.addWork(self.pitchNextIndexLabel.set_text, "")
        self._serializer.addWork(self.dataFileButton.set_sensitive, False)
        self._serializer.addWork(self.timerButton.set_sensitive, False)
        self._serializer.addWork(self.startButton.set_sensitive, False)
        self._serializer.addWork(self.pauseResumeButton.set_sensitive, True)
        self._serializer.addWork(self.stopButton.set_sensitive, True)
        self._serializer.addWork(self.doneButton.set_sensitive, False)
        self._serializer.addWork(self.rewindButton.set_sensitive, False)
        self._serializer.addWork(self.forwardButton.set_sensitive, False)

    def __shootingPaused(self):
        Logger().trace("ShootController.__shootingPaused()")
        self.pauseResumeButton.set_sensitive(True)
        self._serializer.addWork(self.pauseResumeLabel.set_text, _("Resume"))
        self._serializer.addWork(self.rewindButton.set_sensitive, True)
        self._serializer.addWork(self.forwardButton.set_sensitive, True)
        self._serializer.addWork(self.progressbar.set_text, _("Idle"))

    def __shootingResumed(self):
        Logger().trace("ShootController.__shootingResumed()")
        self._serializer.addWork(self.pauseResumeLabel.set_text, _("Pause"))
        self._serializer.addWork(self.rewindButton.set_sensitive, False)
        self._serializer.addWork(self.forwardButton.set_sensitive, False)

    def __shootingStopped(self, status):
        Logger().debug("ShootController.__shootingStopped(): status=%s" % status)
        if status == 'ok':
            self._serializer.addWork(self.progressbar.set_text, _("Finished"))
        elif status == 'cancel':
            self._serializer.addWork(self.progressbar.set_text, _("Canceled"))
        elif status == 'fail':
            self._serializer.addWork(self.progressbar.set_text, _("Failed"))
        self._serializer.addWork(self.dataFileButton.set_sensitive, True)
        self._serializer.addWork(self.timerButton.set_sensitive, True)
        self._serializer.addWork(self.startButton.set_sensitive, True)
        self._serializer.addWork(self.pauseResumeButton.set_sensitive, False)
        self._serializer.addWork(self.stopButton.set_sensitive, False)
        self._serializer.addWork(self.doneButton.set_sensitive, True)

    def __shootingWaiting(self, wait):
        Logger().trace("ShootController.__shootingRepeat()")
        sequenceMessage = _("Waiting %s") % sToHmsAsStr(wait)
        self._serializer.addWork(self.progressbar.set_text, sequenceMessage)

    def __shootingBeginShoot(self):
        Logger().trace("ShootController.__shootingBeginShoot()")
        self._serializer.addWork(self.shootingArea.clear)

    def __shootingProgress(self, progress):
        Logger().trace("ShootController.__shootingProgress()")
        self._serializer.addWork(self.progressbar.set_fraction, progress)

    def __shootingRepeat(self, repeat):
        Logger().trace("ShootController.__shootingRepeat()")
        if self._model.timerRepeatEnable:
            self._serializer.addWork(self.repeatLabel.set_text, _("%d/%d") % (repeat, self._model.timerRepeat))

    def __shootingNewPosition(self, index, yaw, pitch, status=None, next=False):
        Logger().trace("ShootController.__shootingNewPosition()")

        # Update text area
        if isinstance(index, tuple):
            index, yawIndex, pitchIndex = index
            self._serializer.addWork(self.yawCurrentIndexLabel.set_text, _("%d/%d") % (yawIndex, self._model.mosaic.yawNbPicts))
            self._serializer.addWork(self.yawNextIndexLabel.set_text, _("%d/%d") % (yawIndex, self._model.mosaic.yawNbPicts))
            self._serializer.addWork(self.pitchCurrentIndexLabel.set_text, _("%d/%d") % (pitchIndex, self._model.mosaic.pitchNbPicts))
            self._serializer.addWork(self.pitchNextIndexLabel.set_text, _("%d/%d") % (pitchIndex, self._model.mosaic.pitchNbPicts))
        self._serializer.addWork(self.currentIndexLabel.set_text, _("%d/%d") % (index, self._model.scan.totalNbPicts))
        self._serializer.addWork(self.nextIndexLabel.set_text, _("%d/%d") % (index, self._model.scan.totalNbPicts))

        # Update graphical area
        self.shootingArea.add_pict(yaw, pitch, status, next)
        self._serializer.addWork(self.shootingArea.refresh)

    def __shootingSequence(self, sequence, **kwargs):
        Logger().trace("ShootController.__shootingSequence()")
        if sequence == 'moving':
            self._serializer.addWork(self.progressbar.set_text, _("Moving"))
        elif sequence == 'stabilization':
            self._serializer.addWork(self.progressbar.set_text, _("Stabilization"))
        elif sequence == 'mirror':
            self._serializer.addWork(self.progressbar.set_text, _("Mirror lockup"))
        elif sequence == 'shutter':
            bracket = kwargs['bracket']
            totalNbPicts = self._model.camera.bracketingNbPicts
            self._serializer.addWork(self.progressbar.set_text, _("Shutter - Picture %d/%d") % (bracket, totalNbPicts))

    def __refreshPos(self, yaw, pitch):
        Logger().trace("ShootController.__refreshPos()")
        self.shootingArea.set_current_head_position(yaw, pitch)
        self._serializer.addWork(self.shootingArea.refresh)

    # Helpers
    def __refreshNextPosition(self):
        index = self._model.getShootingIndex() # getNexPositionIndex()
        index, (yaw, pitch) = self._model.scan.getPositionAtIndex(index)

        # Update text area
        if isinstance(index, tuple):
            index, yawIndex, pitchIndex = index
            self.yawNextIndexLabel.set_text(_("%d/%d") % (yawIndex, self._model.mosaic.yawNbPicts))
            self.pitchNextIndexLabel.set_text(_("%d/%d") % (pitchIndex, self._model.mosaic.pitchNbPicts))
        self.nextIndexLabel.set_text(_("%d/%d") % (index, self._model.scan.totalNbPicts))

        # Update graphical area
        self.shootingArea.set_selected_image_index(index)

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
        self.pauseResumeButton.set_sensitive(False)

    def __resumeShooting(self):
        self._model.resume()

    def __stopShooting(self):
        self._model.stop()

    # Interface
    def shutdown(self):
        super(ShootController, self).shutdown()
        if self.__thread is not None:
            self.__thread.join()
        Spy().newPosSignal.disconnect(self.__refreshPos)
        self._model.startedSignal.disconnect(self.__shootingStarted)
        self._model.pausedSignal.disconnect(self.__shootingPaused)
        self._model.resumedSignal.disconnect(self.__shootingResumed)
        self._model.stoppedSignal.disconnect(self.__shootingStopped)
        self._model.waitingSignal.disconnect(self.__shootingWaiting)
        self._model.beginShootSignal.disconnect(self.__shootingBeginShoot)
        self._model.progressSignal.disconnect(self.__shootingProgress)
        self._model.repeatSignal.connect(self.__shootingRepeat)
        self._model.newPositionSignal.disconnect(self.__shootingNewPosition)
        self._model.sequenceSignal.disconnect(self.__shootingSequence)

    def refreshView(self):
        dataFileFlag = ConfigManager().getBoolean('Preferences', 'DATA_FILE_ENABLE')
        self.dataFileButtonImage.set_sensitive(dataFileFlag)
        timerFlag = self._model.timerAfterEnable or self._model.timerRepeatEnable
        self.timerButtonImage.set_sensitive(timerFlag)
