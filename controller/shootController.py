# -*- coding: iso-8859-1 -*-

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

import os
import time
import threading

import gtk
import gobject

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.spy import Spy
from papywizard.view.mosaicArea import MosaicArea
from papywizard.view.presetArea import PresetArea

path = os.path.dirname(__file__)


class ShootController(AbstractController):
    """ Shoot controller object.
    """
    def __init__(self, parent, model):
        """ Init the object.

        @param parent: parent controller
        @type parent: {Controller}

        @param model: model to use
        @type mode: {Shooting}
        """
        self.__parent = parent
        self.__model = model
        
        # Set the Glade file
        gladeFile = os.path.join(path, os.path.pardir, "view", "shootDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets(self.__model.mode)
        
        # Init shooting area
        if self.__model.mode == 'mosaic':
            self.shootingArea.init(self.__model.mosaic.yawStart, self.__model.mosaic.yawEnd,
                                   self.__model.mosaic.pitchStart, self.__model.mosaic.pitchEnd,
                                   self.__model.mosaic.yawFov, self.__model.mosaic.pitchFov,
                                   self.__model.camera.getYawFov(self.__model.mosaic.cameraOrientation),
                                   self.__model.camera.getPitchFov(self.__model.mosaic.cameraOrientation),
                                   self.__model.mosaic.yawRealOverlap, self.__model.mosaic.pitchRealOverlap)
        else:
            self.shootingArea.init(500., 250., # fov
                                   120., 120.) # camera fov

        # Connect signal/slots
        dic = {"on_manualShootCheckbutton_toggled": self.__onManualShootCheckbuttonToggled,
               "on_dataFileEnableCheckbutton_toggled": self.__onDataFileEnableCheckbuttonToggled,
               "on_startButton_clicked": self.__onStartButtonClicked,
               "on_suspendResumeButton_clicked": self.__onSuspendResumeButtonClicked,
               "on_stopButton_clicked": self.__onStopButtonClicked,
               "on_doneButton_clicked": self.__onDoneButtonClicked,
           }
        self.wTree.signal_autoconnect(dic)
        self.shootDialog.connect("key-press-event", self.__onKeyPressed)
        self.shootDialog.connect("key-release-event", self.__onKeyReleased)
        self.shootDialog.connect("delete-event", self.__onDelete)

        self.__keyPressedDict = {'Return': False,
                                 'Escape': False
                             }
        self.__key = {'Return': gtk.keysyms.Return,
                      'Escape': gtk.keysyms.Escape
                      }

        # Nokia plateform stuff
        try:
            import hildon
            self.__key['Home'] = gtk.keysyms.F8
            self.__key['End'] = gtk.keysyms.F7
        except ImportError:
            pass

        # Fill widgets
        self.refreshView()

        # Connect model signals
        self.__model.newPictSignal.connect(self.__addPicture)

    def _retreiveWidgets(self, shootingMode):
        """ Get widgets from widget tree.
        
        @param shootingMode: mode used to shoot ('mosaic', 'preset')
        @type shootingMode: str
        """
        self.shootDialog = self.wTree.get_widget("shootDialog")
        vbox = self.wTree.get_widget("vbox")
        drawingarea = self.wTree.get_widget("drawingarea")
        drawingarea.destroy()
        if shootingMode == 'mosaic':
            self.shootingArea = MosaicArea()
        else:
            self.shootingArea = PresetArea()
        vbox.pack_start(self.shootingArea)
        vbox.reorder_child(self.shootingArea, 0)
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
                if not self.__model.isShooting():
                    Logger().debug("shootController.__onKeyPressed(): start shooting")
                    self.__startShooting()
    
                # Pressing 'Return' while shooting...
                else:
    
                    # ...and not suspended suspends shooting
                    if not self.__model.isSuspended():
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
               if not self.__model.isShooting():
                   Logger().debug("shootController.__onKeyPressed(): close shooting dialog")
                   self.shootDialog.response(0)
   
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
        """ Manual shoot checkbutton togled.
        """
        Logger().trace("ShootController.____onManualShootCheckbuttonToggled()")
        switch = self.manualShootCheckbutton.get_active()
        self.__model.setManualShoot(switch)

    def __onDataFileEnableCheckbuttonToggled(self, widget):
        """ Data file enable checkbutton togled.
        """
        Logger().trace("ShootController.__onDataFileEnableCheckbuttonToggled()")
        switch = self.dataFileEnableCheckbutton.get_active()
        ConfigManager().setBoolean('Data', 'DATA_FILE_ENABLE', self.dataFileEnableCheckbutton.get_active())

    def __onStartButtonClicked(self, widget):
        """ Start button has been clicked.

        The model's start() method is called in a thread
        """
        Logger().trace("ShootController.__startButtonClicked()")
        self.__startShooting()

    def __onSuspendResumeButtonClicked(self, widget):
        """ SuspendResume button has been clicked.
        """
        Logger().trace("ShootController.__suspendResumeButtonClicked()")
        if self.__model.isShooting(): # Should always be true here, but...
            if not self.__model.isSuspended():
                self.__suspendShooting()
            else:
                self.__resumeShooting()

    def __onStopButtonClicked(self, widget):
        """ Stop button has been clicked.
        """
        Logger().trace("ShootController.__stopButtonClicked()")
        self.__stopShooting()

    def __onDoneButtonClicked(self, widget):
        """ Done button has been clicked.
        """
        Logger().trace("ShootController.__onDoneButtonClicked()")
        self.shootDialog.response(0)

    def __addPicture(self, yaw, pitch):
        Logger().trace("ShootController.__addPicture()")
        self.shootingArea.add_pict(yaw, pitch)

    # Real work
    def __startShooting(self):
        def checkEnd():
            """ Check end of shooting.

            This method executes once, then registers itself in the TKinter
            event handler to be execute again after a delay, and exits.
            This way, GUI events can be handled while model is shooting.
            """
            Logger().trace("ShootController.__startShooting().checkEnd()")

            # Check if model suspended (manual shoot mode)
            if self.__model.isSuspended():
                self.suspendResumeLabel.set_text("Resume")
            else:
                self.suspendResumeLabel.set_text("Suspend")

            # Check end of shooting
            if not self.__model.isShooting():
                Logger().debug("checkEnd(): model not shooting anymore")
                
                # Check status
                #if self.__model.error:
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
                Logger().debug("ShootController.__startShooting().checkEnd(): model thread over")
                
                return False # Stop execution by Gtk timeout

            self.refreshView() # Can conflict with Spy?

            return True

        self.shootingArea.clear()
        self.dataFileEnableCheckbutton.set_sensitive(False)
        self.startButton.set_sensitive(False)
        self.suspendResumeButton.set_sensitive(True)
        self.stopButton.set_sensitive(True)
        self.doneButton.set_sensitive(False)

        thread = threading.Thread(target=self.__model.start)
        thread.start()
        #self.__model.startEvent.wait() # Does not work under Nokia
        time.sleep(0.2)

        # Check end of shooting
        gobject.timeout_add(200, checkEnd)

    def __suspendShooting(self):
        self.__model.suspend()
        #self.suspendResumeLabel.set_text("Resume")

    def __resumeShooting(self):
        self.__model.resume()
        #self.suspendResumeLabel.set_text("Suspend")

    def __stopShooting(self):
        self.__model.stop()

        # Wait for shooting really stops
        # todo: use condition
        while self.__model.isShooting():
            time.sleep(0.1)

    def run(self):
        """ Run the dialog.
        """
        self.shootDialog.run()
        
    def destroyView(self):
        """ Destroy the view.
        """
        self.shootDialog.destroy()

    def refreshView(self):
        self.progressbar.set_fraction(self.__model.progress)
        self.progressbar.set_text(self.__model.sequence)
        self.dataFileEnableCheckbutton.set_active(ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE'))
