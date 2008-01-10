# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Controller.

Implements class:

- ConfigController

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import Tkinter as tk

from common import config
from common.loggingServices import Logger
from abstractController import AbstractController


class ConfigController(AbstractController):
    """ Configuration controller object.
    """
    def __init__(self, parent, model, view):
        """ Init the object.

        @param parent: parent controller
        @type parent: {Controller}

        @param model: model to use
        @type mode: {Shooting}

        @param view: associated view
        @type view: {ConfigDialog}
        """
        self.__parent = parent
        self.__model = model
        self.__view = view
        
        # Bind events
        self.__view.okButton.config(command=self.__okButtonClicked)
        self.__view.cancelButton.config(command=self.__cancelButtonClicked)
        self.__view.defaultButton.config(command=self.__defaultButtonClicked)
        
        # Fill widgets
        self.refreshView()
        
        self.__view.protocol("WM_DELETE_WINDOW", self.__view.destroy)
        self.__view.wait_window(self.__view)

    def __okButtonClicked(self):
        """ Ok button has been clicked.
        
        Save back values to model.
        """
        Logger().trace("ConfigController.__okButtonClicked()")
        self.__model.camera.timeValue = self.__view.timeValueVar.get()
        self.__model.camera.nbPicts = self.__view.nbPictsVar.get()
        self.__model.delay = self.__view.delayVar.get()
        self.__model.camera.sensorCoef = self.__view.sensorCoefVar.get()
        self.__model.camera.sensorRatio = self.__view.sensorRatioVar.get()
        self.__model.overlap = self.__view.overlapVar.get() / 100.
        self.__model.camera.lens.focal = self.__view.focalVar.get()
        self.__model.camera.lens.fisheye = bool(self.__view.fisheyeVar.get())
        self.__model.cameraOrientation = self.__view.cameraOrientationVar.get()
        self.__model.manualShoot = bool(self.__view.manualShootVar.get())
        self.__view.destroy()

    def __cancelButtonClicked(self):
        """ Cancel button has been clicked.
        
        Close the pref. dialog.
        """
        Logger().trace("ConfigController.__cancelButtonClicked()")
        self.__view.destroy()

    def __defaultButtonClicked(self):
        """ Default button has been clicked.
        
        Load default config values.
        """
        Logger().trace("ConfigController.__defaultButtonClicked()")
        self.__view.fillWidgets(config.DEFAULT_PREFS)
        
    def refreshView(self):
        values = {'shooting': {'overlap': int(100 * self.__model.overlap),
                               'manualShoot': self.__model.manualShoot,
                               'cameraOrientation': self.__model.cameraOrientation,
                               'delay': self.__model.delay
                               },
                  'mosaic': {'template': self.__model.mosaic.template
                           },
                  'camera': {'sensorCoef': self.__model.camera.sensorCoef,
                             'sensorRatio': self.__model.camera.sensorRatio,
                             'timeValue': self.__model.camera.timeValue,
                             'nbPicts' : self.__model.camera.nbPicts,
                         },
                  'lens': {'focal': self.__model.camera.lens.focal,
                           'fisheye': self.__model.camera.lens.fisheye
                       }
                }
        self.__view.fillWidgets(values)
