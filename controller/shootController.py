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

import time
import threading

import gtk
import gobject

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.spy import Spy


class ShootController(AbstractController):
    """ Shoot controller object.
    """
    def __init__(self, parent, serializer, model, view):
        """ Init the object.

        @param parent: parent controller
        @type parent: {Controller}

        @param serializer: object used to serialize Tkinter events
        @type serializer: {Serializer]

        @param model: model to use
        @type mode: {Shooting}

        @param view: associated view
        @type view: {ConfigDialog}
        """
        self.__parent = parent
        self.__serializer = serializer
        self.__model = model
        self.__view = view

        # Connect signal/slots
        dic = {"on_manualShootCheckbutton_toggled": self.__onManualShootCheckbuttonToggled,
               "on_dataFileEnableCheckbutton_toggled": self.__onDataFileEnableCheckbuttonToggled,
               "on_startButton_clicked": self.__onStartButtonClicked,
               "on_suspendResumeButton_clicked": self.__onSuspendResumeButtonClicked,
               "on_stopButton_clicked": self.__onStopButtonClicked,
               "on_doneButton_clicked": self.__onDoneButtonClicked,
           }
        self.__view.wTree.signal_autoconnect(dic)
        self.__view.shootDialog.connect("key-press-event", self.__onKeyPressed)
        self.__view.shootDialog.connect("key-release-event", self.__onKeyReleased)

        self.__keyPressedDict = {'Left': False,
                                 'Right': False,
                                 'Up': False,
                                 'Down': False,
                                 'Home': False,
                                 'End': False
                             }
        self.__key = {'Right': gtk.keysyms.Right,
                      'Left': gtk.keysyms.Left,
                      'Up': gtk.keysyms.Up,
                      'Down': gtk.keysyms.Down,
                      'Home': gtk.keysyms.Home,
                      'End': gtk.keysyms.End,
                      'Return': gtk.keysyms.Return,
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

        # Connect Spy
        Spy().newPosSignal.connect(self.__refreshPos)

    # Callbacks
    def __onKeyPressed(self, widget, event, *args):

        # 'Right' key
        #elif event.keyval == self.__key['Right']:
            #if not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left']:
                #Logger().debug("shootController.__onKeyPressed(): 'Right' key pressed")
                #self.__keyPressedDict['Right'] = True
            #return True

        # 'Left' key
        #elif event.keyval == self.__key['Left']:
            #if not self.__keyPressedDict['Left'] and not self.__keyPressedDict['Right']:
                #Logger().debug("shootController.__onKeyPressed(): 'Left' key pressed")
                #self.__keyPressedDict['Left'] = True
            #return True

        # 'Up' key
        #elif event.keyval == self.__key['Up']:
            #if not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                #Logger().debug("shootController.__onKeyPressed(): 'Up' key pressed")
                #self.__keyPressedDict['Up'] = True
            #return True

        # 'Down' key
        #elif event.keyval == self.__key['Down']:
            #if not self.__keyPressedDict['Down'] and not self.__keyPressedDict['Up']:
                #Logger().debug("shootController.__onKeyPressed(): 'Down' key pressed")
                #self.__keyPressedDict['Down'] = True
            #return True

        # 'Home' key
        #elif event.keyval == self.__key['Home'] or event.keyval == gtk.keysyms.F6:
            #if not self.__keyPressedDict['Home'] and not self.__keyPressedDict['End'] and \
               #not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               #not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                #Logger().debug("shootController.__onKeyPressed(): 'Home' key pressed")
                #self.__keyPressedDict['Home'] = True
            #return True

        # 'End' key
        #elif event.keyval == self.__key['End'] or event.keyval == gtk.keysyms.F7:
            #if not self.__keyPressedDict['End'] and not self.__keyPressedDict['Home'] and \
               #not self.__keyPressedDict['Right'] and not self.__keyPressedDict['Left'] and \
               #not self.__keyPressedDict['Up'] and not self.__keyPressedDict['Down']:
                #Logger().debug("shootController.__onKeyPressed(): 'End' key pressed")
                #self.__keyPressedDict['End'] = True
            #return True

        # 'Return' key
        if event.keyval == self.__key['Return']:
            Logger().debug("shootController.__onKeyPressed(): 'Return' key pressed")

            # Pressing 'Return' while not shooting starts shooting
            if not self.__model.isShooting():
                Logger().info("shootController.__onKeyPressed(): start shooting")
                self.__startShooting()

            # Pressing 'Return' while shooting...
            else:

                # ...and not suspended suspends shooting
                if not self.__model.isSuspended():
                    Logger().info("shootController.__onKeyPressed(): suspend shooting")
                    self.__suspendShooting()

                #... and suspended resumes shooting
                else:
                    Logger().info("shootController.__onKeyPressed(): rerume shooting")
                    self.__resumeShooting()
            return True

        # 'Escape' key
        elif event.keyval == self.__key['Escape']:
            Logger().debug("shootController.__onKeyPressed(): 'Escape' key pressed")

            # Pressing 'Escape' while not shooting exit shoot dialog
            if not self.__model.isShooting():
                Logger().info("shootController.__onKeyPressed(): close shooting dialog")
                self.__view.shootDialog.response(0)

            # Pressing 'Escape' while shooting stops shooting
            else:
                Logger().info("shootController.__onKeyPressed(): stop shooting")
                self.__stopShooting()
            return True

        else:
            Logger().warning("MainController.__onKeyPressed(): unbind '%s' key" % event.keyval)

    def __onKeyReleased(self, widget, event, *args):
        return False

        # 'Right' key
        if event.keyval == self.__key['Right']:
            if self.__keyPressedDict['Right']:
                Logger().debug("MainController.__onKeyReleased(): 'Right' key released; stop 'yaw' axis")
                self.__model.hardware.stopAxis('yaw')
                self.__keyPressedDict['Right'] = False
            return True

        # 'Left' key
        if event.keyval == self.__key['Left']:
            if self.__keyPressedDict['Left']:
                Logger().debug("MainController.__onKeyReleased(): 'Left' key released; stop 'yaw' axis")
                self.__model.hardware.stopAxis('yaw')
                self.__keyPressedDict['Left'] = False
            return True

        # 'Up' key
        if event.keyval == self.__key['Up']:
            if self.__keyPressedDict['Up']:
                Logger().debug("MainController.__onKeyReleased(): 'Up' key released; stop 'pitch' axis")
                self.__model.hardware.stopAxis('pitch')
                self.__keyPressedDict['Up'] = False
            return True

        # 'Down' key
        if event.keyval == self.__key['Down']:
            if self.__keyPressedDict['Down']:
                Logger().debug("MainController.__onKeyReleased(): 'Down' key released; stop 'pitch' axis")
                self.__model.hardware.stopAxis('pitch')
                self.__keyPressedDict['Down'] = False
            return True

        # 'Home' key
        if event.keyval == self.__key['Home']:
            if self.__keyPressedDict['Home']:
                Logger().debug("MainController.__onKeyReleased(): 'Home' key released")
                self.__keyPressedDict['Home'] = False
            return True

        # 'End' key
        if event.keyval == self.__key['End']:
            if self.__keyPressedDict['End']:
                Logger().debug("MainController.__onKeyReleased(): 'End' key released")
                self.__keyPressedDict['End'] = False
            return True

        else:
            Logger().warning("MainController.__onKeyReleased(): unbind '%s' key" % event.keyval)

    def __onManualShootCheckbuttonToggled(self, widget):
        """ Manual shoot checkbutton togled.
        """
        Logger().trace("ShootController.____onManualShootCheckbuttonToggled()")
        switch = self.__view.manualShootCheckbutton.get_active()
        self.__model.setManualShoot(switch)

    def __onDataFileEnableCheckbuttonToggled(self, widget):
        """ Data file enable checkbutton togled.
        """
        Logger().trace("ShootController.__onDataFileEnableCheckbuttonToggled()")
        switch = self.__view.dataFileEnableCheckbutton.get_active()
        ConfigManager().setBoolean('Data', 'DATA_FILE_ENABLE', self.__view.dataFileEnableCheckbutton.get_active())
        ConfigManager().save()

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
        self.__view.shootDialog.response(0)

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
                self.__view.suspendResumeLabel.set_text("Resume")
            else:
                self.__view.suspendResumeLabel.set_text("Suspend")

            # Check end of shooting
            if not self.__model.isShooting():
                Logger().debug("checkEnd(): model not shooting anymore")
                self.__view.dataFileEnableCheckbutton.set_sensitive(True)
                self.__view.startButton.set_sensitive(True)
                self.__view.suspendResumeLabel.set_text("Suspend")
                self.__view.suspendResumeButton.set_sensitive(False)
                self.__view.stopButton.set_sensitive(False)
                self.__view.doneButton.set_sensitive(True)
                self.refreshView()
                thread.join()
                Logger().debug("ShootController.__startShooting().checkEnd(): model thread over")
                return False # Stop execution by Gtk

            self.refreshView() # Can conflict with Spy?

            return True

        self.__view.dataFileEnableCheckbutton.set_sensitive(False)
        self.__view.startButton.set_sensitive(False)
        self.__view.suspendResumeButton.set_sensitive(True)
        self.__view.stopButton.set_sensitive(True)
        self.__view.doneButton.set_sensitive(False)

        thread = threading.Thread(target=self.__model.start)
        thread.start()

        # Wait for shooting really starts
        # Use condition
        time.sleep(0.1)

        # Check end of shooting
        gobject.timeout_add(200, checkEnd)
        checkEnd()

    def __suspendShooting(self):
        self.__model.suspend()
        #self.__view.suspendResumeLabel.set_text("Resume")

    def __resumeShooting(self):
        self.__model.resume()
        #self.__view.suspendResumeLabel.set_text("Suspend")

    def __stopShooting(self):
        self.__model.stop()

        # Wait for shooting really stops
        # todo: use condition
        while self.__model.isShooting():
            time.sleep(0.1)

    def __refreshPos(self, yaw, pitch):
        """ Refresh position according to new pos.

        @param yaw: yaw axis value
        @type yaw: float

        @param pitch: pitch axix value
        @type pitch: float
        """
        Logger().trace("ShootController.__refreshPos()")

        # Hugly design!
        values = self.__model.getState()
        values.update({'yawPos': yaw, 'pitchPos': pitch})
        self.__serializer.apply(self.__view.fillWidgets, values)

    def refreshView(self):
        values = self.__model.getState()
        values['dataFileEnable'] = ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE')
        self.__view.fillWidgets(values)
