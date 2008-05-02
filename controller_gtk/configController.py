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

import copy

from common import config
from common.loggingServices import Logger
from controller.abstractController import AbstractController


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

        # Connect signal/slots
        dic = {"on_okButton_clicked": self.__onOkButtonClicked,
               "on_cancelButton_clicked": self.__onCancelButtonClicked,
               "on_defaultButton_clicked": self.__onDefaultButtonClicked
           }
        self.__view.wTree.signal_autoconnect(dic)
        
        # Fill widgets
        self.refreshView()

    def __onOkButtonClicked(self, widget):
        """ Ok button has been clicked.
        
        Save back values to model.
        """
        Logger().trace("ConfigController.__onOkButtonClicked()")
        self.__model.camera.timeValue = self.__view.timeValueSpinbutton.get_value()
        self.__model.camera.nbPicts = self.__view.nbPictsSpinbutton.get_value()
        self.__model.delay = self.__view.delaySpinbutton.get_value()
        self.__model.camera.sensorCoef = self.__view.sensorCoefSpinbutton.get_value()
        self.__model.camera.sensorRatio = config.SENSOR_RATIOS_INDEX[self.__view.sensorRatioCombobox.get_active()]
        self.__model.overlap = self.__view.overlapSpinbutton.get_value() / 100.
        self.__model.camera.lens.focal = self.__view.focalSpinbutton.get_value()
        self.__model.camera.lens.fisheye = self.__view.fisheyeCheckbutton.get_active()
        self.__model.cameraOrientation = config.CAMERA_ORIENTATION_INDEX[self.__view.cameraOrientationCombobox.get_active()]

    def __onCancelButtonClicked(self, widget):
        """ Cancel button has been clicked.
        
        Close the pref. dialog.
        """
        Logger().trace("ConfigController.__onCancelButtonClicked()")

    def __onDefaultButtonClicked(self, widget):
        """ Default button has been clicked.
        
        Load default config values.
        """
        Logger().trace("ConfigController.__onDefaultButtonClicked()")
        defaultValues = copy.deepcopy(config.DEFAULT_PREFS)
        defaultValues['shooting']['overlap'] *= 100
        self.__view.fillWidgets(defaultValues)
        
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
