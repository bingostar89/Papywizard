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
import gobject

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.spy import Spy
from papywizard.view.shootingArea import MosaicArea, PresetArea


class ShootController(AbstractController):
    """ Shoot controller object.
    """
    def _init(self):
        self._gladeFile = "shootDialog.glade"
        self._signalDict = {"on_manualShootCheckbutton_toggled": self.__onManualShootCheckbuttonToggled,
                            "on_dataFileEnableCheckbutton_toggled": self.__onDataFileEnableCheckbuttonToggled,
                            "on_startButton_clicked": self.__onStartButtonClicked,
                            "on_suspendResumeButton_clicked": self.__onSuspendResumeButtonClicked,
                            "on_stopButton_clicked": self.__onStopButtonClicked,
                            "on_doneButton_clicked": self.__onDoneButtonClicked,
                        }

        self.__keyPressedDict = {'Return': False,
                                 'Escape': False
                             }
        self.__key = {'Return': gtk.keysyms.Return,
                      'Escape': gtk.keysyms.Escape
                      }

    def _retreiveWidgets(self):
        super(ShootController, self)._retreiveWidgets()
        
        vbox = self.wTree.get_widget("vbox")
        drawingarea = self.wTree.get_widget("drawingarea")
        drawingarea.destroy()
        if self._model.mode == 'mosaic':
            self.shootingArea = MosaicArea()
        else:
            self.shootingArea = PresetArea()
        vbox.pack_start(self.shootingArea)
        vbox.reorder_child(self.shootingArea, 0)
        if self._model.mode == 'mosaic':
            
            # todo: give args in shootingArea.__init__()
            self.shootingArea.init(self._model.mosaic.yawStart, self._model.mosaic.yawEnd,
                                   self._model.mosaic.pitchStart, self._model.mosaic.pitchEnd,
                                   self._model.mosaic.yawFov, self._model.mosaic.pitchFov,
                                   self._model.camera.getYawFov(self._model.mosaic.cameraOrientation),
                                   self._model.camera.getPitchFov(self._model.mosaic.cameraOrientation),
                                   self._model.mosaic.yawRealOverlap, self._model.mosaic.pitchRealOverlap)
        else:
            self.shootingArea.init(440., 220., # visible fov
                                    16.,  16.) # camera fov
        self.shootingArea.show()
        self.progressbar = self.wTree.get_widget("progressbar")
        self.manualShootCheckbutton = self.wTree.get_widget("manualShootCheckbutton")
        self.dataFileEnableCheckbutton = self.wTree.get_widget("dataFileEnableCheckbutton")
        self.startButton = self.wTree.get_widget("startButton")
        self.suspendResumeButton = self.wTree.get_widget("suspendResumeButton")
        self.suspendResumeLabel = self.wTree.get_widget("suspendResumeLabel")
        self.stopButton = self.wTree.get_widget("stopButton")
        self.doneButton = self.wTree.get_widget("doneButton")
        
        self.suspendResumeButton.set_sensitive(False)
        self.stopButton.set_sensitive(False)

    def _connectSignals(self):
        super(ShootController, self)._connectSignals()
        
        self.dialog.connect("key-press-event", self.__onKeyPressed)
        self.dialog.connect("key-release-event", self.__onKeyReleased)
        self.dialog.connect("delete-event", self.__onDelete)
        
        self._model.newPictSignal.connect(self.__addPicture)

    # Callbacks
    def __onDelete(self, widget, event):
        Logger().trace("ShootController.__onDelete()")
        self.__stopShooting()

    def __onKeyPressed(self, widget, event, *args):

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
    
                    # ...and not suspended suspends shooting
                    if not self._model.isSuspended():
                        Logger().debug("shootController.__onKeyPressed(): suspend shooting")
                        self.__suspendShooting()
    
                    #... and suspended resumes shooting
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

    def __onManualShootCheckbuttonToggled(self, widget):
        Logger().trace("ShootController.____onManualShootCheckbuttonToggled()")
        switch = self.manualShootCheckbutton.get_active()
        self._model.setManualShoot(switch)

    def __onDataFileEnableCheckbuttonToggled(self, widget):
        Logger().trace("ShootController.__onDataFileEnableCheckbuttonToggled()")
        switch = self.dataFileEnableCheckbutton.get_active()
        ConfigManager().setBoolean('Data', 'DATA_FILE_ENABLE', self.dataFileEnableCheckbutton.get_active())

    def __onStartButtonClicked(self, widget):
        Logger().trace("ShootController.__startButtonClicked()")
        self.__startShooting()

    def __onSuspendResumeButtonClicked(self, widget):
        Logger().trace("ShootController.__suspendResumeButtonClicked()")
        if self._model.isShooting(): # Should always be true here, but...
            if not self._model.isSuspended():
                self.__suspendShooting()
            else:
                self.__resumeShooting()

    def __onStopButtonClicked(self, widget):
        Logger().trace("ShootController.__stopButtonClicked()")
        self.__stopShooting()

    def __onDoneButtonClicked(self, widget):
        Logger().trace("ShootController.__onDoneButtonClicked()")
        self.dialog.response(0)

    def __addPicture(self, yaw, pitch, status):
        Logger().trace("ShootController.__addPicture()")
        self.shootingArea.add_pict(yaw, pitch, status)

    # Real work
    def __startShooting(self):
        def monitorShooting():
            Logger().trace("ShootController.__startShooting().monitorShooting()")

            # Check if model suspended (manual shoot mode)
            if self._model.isSuspended():
                self.suspendResumeLabel.set_text("Resume")
            else:
                self.suspendResumeLabel.set_text("Suspend")

            # Check end of shooting
            if not self._model.isShooting():
                Logger().debug("monitorShooting(): model not shooting anymore")

                # Check status
                #if self._model.error:
                    #messageDialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
                                                      #message_format="Internal error while shooting")
                    #messageDialog.format_secondary_text("Please report bug (include logs)")
                    #messageDialog.run()
                    #messageDialog.destroy()

                self.dataFileEnableCheckbutton.set_sensitive(True)
                self.startButton.set_sensitive(True)
                self.suspendResumeLabel.set_text("Suspend")
                self.suspendResumeButton.set_sensitive(False)
                self.stopButton.set_sensitive(False)
                self.doneButton.set_sensitive(True)
                self.refreshView()
                thread.join()
                Logger().debug("ShootController.__startShooting().monitorShooting(): model thread over")

                return False # Stop execution by Gtk timeout

            self.refreshView() # Can conflict with Spy?

            return True

        self.shootingArea.clear()
        self.dataFileEnableCheckbutton.set_sensitive(False)
        self.startButton.set_sensitive(False)
        self.suspendResumeButton.set_sensitive(True)
        self.stopButton.set_sensitive(True)
        self.doneButton.set_sensitive(False)

        thread = threading.Thread(target=self._model.start)
        thread.start()
        #self._model.startEvent.wait() # Does not work under Nokia
        time.sleep(0.2)

        # Monitor shooting process
        gobject.timeout_add(200, monitorShooting)

    def __suspendShooting(self):
        self._model.suspend()
        #self.suspendResumeLabel.set_text("Resume")

    def __resumeShooting(self):
        self._model.resume()
        #self.suspendResumeLabel.set_text("Suspend")

    def __stopShooting(self):
        self._model.stop()

        # Wait for shooting really stops
        # todo: use condition
        while self._model.isShooting():
            time.sleep(0.1)

    def refreshView(self):
        self.progressbar.set_fraction(self._model.progress)
        self.progressbar.set_text(self._model.sequence)
        self.dataFileEnableCheckbutton.set_active(ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE'))
