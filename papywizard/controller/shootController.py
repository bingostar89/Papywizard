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

import os.path
import time
import threading

import pygtk
pygtk.require("2.0")
import gtk
import gtk.gdk
import gobject

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.controller.messageController import ErrorMessageController
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.generalInfoController import GeneralInfoController
from papywizard.controller.spy import Spy
from papywizard.view.shootingArea import MosaicArea, PresetArea
from papywizard.controller.spy import Spy


class ShootController(AbstractController):
    """ Shoot controller object.
    """
    def _init(self):
        self._gladeFile = "shootDialog.glade"
        self._signalDict = {"on_rewindButton_clicked": self.__onRewindButtonclicked,
                            "on_forwardButton_clicked": self.__onForwardButtonclicked,
                            "on_manualShootCheckbutton_toggled": self.__onManualShootCheckbuttonToggled,
                            "on_dataFileEnableCheckbutton_toggled": self.__onDataFileEnableCheckbuttonToggled,
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

        hbox = self.wTree.get_widget("hbox")
        drawingarea = self.wTree.get_widget("drawingarea")
        drawingarea.destroy()
        if self._model.mode == 'mosaic':
            self.shootingArea = MosaicArea()
        else:
            self.shootingArea = PresetArea()
        hbox.pack_start(self.shootingArea)
        hbox.reorder_child(self.shootingArea, 1)
        self.shootingArea.set_size_request(450, 150)
        if self._model.mode == 'mosaic':

            # todo: give args in shootingArea.__init__()
            self.shootingArea.init(self._model.mosaic.yawStart, self._model.mosaic.yawEnd,
                                   self._model.mosaic.pitchStart, self._model.mosaic.pitchEnd,
                                   self._model.mosaic.yawFov, self._model.mosaic.pitchFov,
                                   self._model.camera.getYawFov(self._model.cameraOrientation),
                                   self._model.camera.getPitchFov(self._model.cameraOrientation),
                                   self._model.mosaic.yawRealOverlap, self._model.mosaic.pitchRealOverlap)
            self._model.mosaic.generatePositions()
            for index, (yaw, pitch) in self._model.mosaic.iterPositions():
                self.shootingArea.add_pict(yaw, pitch, status='preview')
        else:
            self.shootingArea.init(440., 220., # visible fov
                                    16.,  16.) # camera fov
            self._model.preset.generatePositions()
            for index, (yaw, pitch) in self._model.preset.iterPositions():
                self.shootingArea.add_pict(yaw, pitch, status='preview')
        yaw, pitch = self._model.hardware.readPosition()
        self.shootingArea.set_current_position(yaw, pitch)
        self.shootingArea.show()

        self.rewindButton = self.wTree.get_widget("rewindButton")
        self.forwardButton = self.wTree.get_widget("forwardButton")
        self.progressbar = self.wTree.get_widget("progressbar")
        self.manualShootCheckbutton = self.wTree.get_widget("manualShootCheckbutton")
        self.dataFileEnableCheckbutton = self.wTree.get_widget("dataFileEnableCheckbutton")
        self.startButton = self.wTree.get_widget("startButton")
        self.pauseResumeButton = self.wTree.get_widget("pauseResumeButton")
        self.pauseResumeLabel = self.wTree.get_widget("pauseResumeLabel")
        self.pauseResumeImage = self.wTree.get_widget("pauseResumeImage")
        self.stopButton = self.wTree.get_widget("stopButton")
        self.doneButton = self.wTree.get_widget("doneButton")

    def _connectSignals(self):
        super(ShootController, self)._connectSignals()

        self.dialog.connect("key-press-event", self.__onKeyPressed)
        self.dialog.connect("key-release-event", self.__onKeyReleased)
        self.dialog.connect("delete-event", self.__onDelete)

        self.shootingArea.connect("button-press-event", self.__onButtonPressed)
        #self.shootingArea.connect("motion-notify-event", self.__onMotionNotify)

        Spy().newPosSignal.connect(self.__refreshPos)
        self._model.newPictSignal.connect(self.__shootingAddPicture)
        self._model.startedSignal.connect(self.__shootingStarted)
        self._model.pausedSignal.connect(self.__shootingPaused)
        self._model.resumedSignal.connect(self.__shootingResumed)
        self._model.stoppedSignal.connect(self.__shootingStopped)
        self._model.updateInfoSignal.connect(self.__shootingUpdateInfo)

    # Callbacks GTK
    def __onKeyPressed(self, widget, event, *args):

        # 'Right' key
        if event.keyval == self.__key['Right']:
            if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyPressed(): 'Right' key pressed; forward shooting position")
                self.__keyPressedDict['Right'] = True
                self.__forwardShootingPosition()
            return True

        # 'Left' key
        elif event.keyval == self.__key['Left']:
            if not self.__keyPressedDict['Left'] and not self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyPressed(): 'Left' key pressed; rewind shooting position")
                self.__keyPressedDict['Left'] = True
                self.__rewindShootingPosition()
            return True

        # 'Up' key
        elif event.keyval == self.__key['Up']:
            if not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyPressed(): 'Up' key pressed; rewind shooting position")
                self.__keyPressedDict['Up'] = True
                self.__rewindShootingPosition()
            return True

        # 'Down' key
        elif event.keyval == self.__key['Down']:
            if not self.__keyPressedDict['Down'] and not self.__keyPressedDict['Up']:
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
        self.__stopShooting()

    def __onButtonPressed(self, widget, event):
        Logger().trace("ShootController.__onButtonPressed()")
        if self._model.isPaused():
            if event.button == 1:
                index = self.shootingArea.get_selected_image_index(event.x, event.y)
                if index is not None:
                    Logger().debug("ShootController.__onButtonPressed(): x=%d, y=%d, index=%d" % (event.x, event.y, index))
                    self._model.setShootingIndex(index)

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

    def __onRewindButtonclicked(self, widget):
        Logger().trace("ShootController.__onRewindButtonclicked()")
        self.__rewindShootingPosition()

    def __onForwardButtonclicked(self, widget):
        Logger().trace("ShootController.__onForwardButtonclicked()")
        self.__forwardShootingPosition()

    def __onManualShootCheckbuttonToggled(self, widget):
        Logger().trace("ShootController.____onManualShootCheckbuttonToggled()")
        switch = self.manualShootCheckbutton.get_active()
        self._model.setManualShoot(switch)

    def __onDataFileEnableCheckbuttonToggled(self, widget):
        Logger().trace("ShootController.__onDataFileEnableCheckbuttonToggled()")
        switch = self.dataFileEnableCheckbutton.get_active()
        ConfigManager().setBoolean('Data', 'DATA_FILE_ENABLE', self.dataFileEnableCheckbutton.get_active())
        if switch:
            controller = GeneralInfoController(self, self._model)
            controller.run()
            controller.shutdown()

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
    def __shootingAddPicture(self, yaw, pitch, status=None, next=False):
        Logger().trace("ShootController.__shootingAddPicture()")
        self.shootingArea.add_pict(yaw, pitch, status, next)
        self._serializer.addWork(self.shootingArea.refresh)

    def __shootingStarted(self):
        Logger().trace("ShootController.__shootingStarted()")
        self._serializer.addWork(self.shootingArea.clear)
        self._serializer.addWork(self.dataFileEnableCheckbutton.set_sensitive, False)
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
        self._serializer.addWork(self.dataFileEnableCheckbutton.set_sensitive, True)
        self._serializer.addWork(self.startButton.set_sensitive, True)
        #self._serializer.addWork(self.pauseResumeLabel.set_text, _("Pause"))
        self._serializer.addWork(self.pauseResumeButton.set_sensitive, False)
        self._serializer.addWork(self.stopButton.set_sensitive, False)
        self._serializer.addWork(self.doneButton.set_sensitive, True)
        #self._serializer.addWork(self.rewindButton.set_sensitive, False)
        #self._serializer.addWork(self.forwardButton.set_sensitive, False)

    def __shootingUpdateInfo(self, info):
        Logger().debug("ShootController.__shootingUpdateInfo(): info=%s" % info)
        if info.has_key('sequence'):
            self._serializer.addWork(self.progressbar.set_text, info['sequence'])
        elif info.has_key('progress'):
            self._serializer.addWork(self.progressbar.set_fraction, info['progress'])

    def __refreshPos(self, yaw, pitch):
        """ Refresh position according to new pos.

        @param yaw: yaw axis value
        @type yaw: float

        @param pitch: pitch axix value
        @type pitch: float
        """
        Logger().trace("ShootController.__refreshPos()")
        self.shootingArea.set_current_position(yaw, pitch)
        self._serializer.addWork(self.shootingArea.refresh)

    # Helpers
    def __rewindShootingPosition(self):
        """
        """
        index = self._model.getShootingIndex()
        Logger().debug("ShootController.__rewindShootingPosition(): old index=%d" % index)
        try:
            self._model.setShootingIndex(index - 1)
            self.shootingArea.set_selected_image_index(index - 1)
            Logger().debug("ShootController.__rewindShootingPosition():new index=%d" % (index - 1))
        except IndexError:
            Logger().exception("ShootController.__rewindShootingPosition()", debug=True)
        
    def __forwardShootingPosition(self):
        """
        """
        index = self._model.getShootingIndex()
        Logger().debug("ShootController.__forwardShootingPosition(): old index=%d" % index)
        try:
            self._model.setShootingIndex(index + 1)
            self.shootingArea.set_selected_image_index(index + 1)
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
        self._model.newPictSignal.disconnect(self.__shootingAddPicture)
        self._model.startedSignal.disconnect(self.__shootingStarted)
        self._model.pausedSignal.disconnect(self.__shootingPaused)
        self._model.resumedSignal.disconnect(self.__shootingResumed)
        self._model.stoppedSignal.disconnect(self.__shootingStopped)
        self._model.updateInfoSignal.disconnect(self.__shootingUpdateInfo)

    def refreshView(self):
        self.dataFileEnableCheckbutton.set_active(ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE'))
