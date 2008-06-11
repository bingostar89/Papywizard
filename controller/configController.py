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

- ConfigController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import copy

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractController


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
        
        # Shooting preferences
        self.__model.camera.timeValue = self.__view.timeValueSpinbutton.get_value()
        self.__model.camera.nbPicts = int(self.__view.nbPictsSpinbutton.get_value())
        self.__model.stabilizationDelay = self.__view.stabilizationDelaySpinbutton.get_value()
        self.__model.camera.sensorCoef = self.__view.sensorCoefSpinbutton.get_value()
        self.__model.camera.sensorRatio = config.SENSOR_RATIOS_INDEX[self.__view.sensorRatioCombobox.get_active()]
        self.__model.overlap = self.__view.overlapSpinbutton.get_value() / 100.
        self.__model.camera.lens.focal = self.__view.focalSpinbutton.get_value()
        self.__model.camera.lens.fisheye = self.__view.fisheyeCheckbutton.get_active()
        self.__model.cameraOrientation = config.CAMERA_ORIENTATION_INDEX[self.__view.cameraOrientationCombobox.get_active()]

        # Default shooting preferences
        ConfigManager().setFloat('DefaultPreferences', 'CAMERA_TIME_VALUE',
                                 self.__view.defaultTimeValueSpinbutton.get_value(), 1)
        ConfigManager().setInt('DefaultPreferences', 'CAMERA_NB_PICTS',
                               self.__view.defaultNbPictsSpinbutton.get_value())
        ConfigManager().setFloat('DefaultPreferences', 'SHOOTING_STABILIZATION_DELAY',
                                 self.__view.defaultStabilizationDelaySpinbutton.get_value(), 1)
        ConfigManager().setFloat('DefaultPreferences', 'CAMERA_SENSOR_COEF',
                                 self.__view.defaultSensorCoefSpinbutton.get_value(), 1)
        ConfigManager().set('DefaultPreferences', 'CAMERA_SENSOR_RATIO',
                            config.SENSOR_RATIOS_INDEX[self.__view.defaultSensorRatioCombobox.get_active()])
        ConfigManager().setFloat('DefaultPreferences', 'SHOOTING_OVERLAP',
                                 self.__view.defaultOverlapSpinbutton.get_value() / 100., 2)
        ConfigManager().setFloat('DefaultPreferences', 'LENS_FOCAL',
                                 self.__view.defaultFocalSpinbutton.get_value(), 1)
        ConfigManager().setBoolean('DefaultPreferences', 'LENS_FISHEYE',
                                   self.__view.defaultFisheyeCheckbutton.get_active())
        ConfigManager().set('DefaultPreferences', 'SHOOTING_CAMERA_ORIENTATION',
                            config.CAMERA_ORIENTATION_INDEX[self.__view.defaultCameraOrientationCombobox.get_active()])

        # Others preferences
        ConfigManager().set('Hardware', 'DRIVER', 
                            config.DRIVER_INDEX[self.__view.driverCombobox.get_active()])
        ConfigManager().set('Hardware', 'BLUETOOTH_DEVICE_ADDRESS', self.__view.bluetoothDeviceAddressEntry.get_text())
        ConfigManager().set('Hardware', 'SERIAL_PORT', self.__view.serialPortEntry.get_text())
        ConfigManager().set('Logger', 'LOGGER_LEVEL',
                            config.LOGGER_INDEX[self.__view.loggerLevelCombobox.get_active()])
        ConfigManager().setBoolean('Data', 'DATA_FILE_ENABLE', self.__view.dataFileEnableCheckbutton.get_active())

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
        defaultValues = {'shootingOverlap': int(100 * ConfigManager().getFloat('DefaultPreferences', 'SHOOTING_OVERLAP')),
                         'shootingCameraOrientation': ConfigManager().get('DefaultPreferences', 'SHOOTING_CAMERA_ORIENTATION'),
                         'shootingStabilizationDelay': ConfigManager().getFloat('DefaultPreferences', 'SHOOTING_STABILIZATION_DELAY'),
                         'mosaicTemplate': ConfigManager().get('DefaultPreferences', 'MOSAIC_TEMPLATE'),
                         'cameraSensorCoef': ConfigManager().getFloat('DefaultPreferences', 'CAMERA_SENSOR_COEF'),
                         'cameraSensorRatio': ConfigManager().get('DefaultPreferences', 'CAMERA_SENSOR_RATIO'),
                         'cameraTimeValue': ConfigManager().getFloat('DefaultPreferences', 'CAMERA_TIME_VALUE'),
                         'cameraNbPicts' : ConfigManager().getInt('DefaultPreferences', 'CAMERA_NB_PICTS'),
                         'lensFocal': ConfigManager().getFloat('DefaultPreferences', 'LENS_FOCAL'),
                         'lensFisheye': ConfigManager().getBoolean('DefaultPreferences', 'LENS_FISHEYE')
                     }
        self.__view.fillWidgets(defaultValues)

    def refreshView(self):
        values = {'shootingOverlap': int(100 * self.__model.overlap),
                  'shootingCameraOrientation': self.__model.cameraOrientation,
                  'shootingStabilizationDelay': self.__model.stabilizationDelay,
                  'mosaicTemplate': self.__model.mosaic.template,
                  'cameraSensorCoef': self.__model.camera.sensorCoef,
                  'cameraSensorRatio': self.__model.camera.sensorRatio,
                  'cameraTimeValue': self.__model.camera.timeValue,
                  'cameraNbPicts' : self.__model.camera.nbPicts,
                  'lensFocal': self.__model.camera.lens.focal,
                  'lensFisheye': self.__model.camera.lens.fisheye,
                  
                  'defaultShootingOverlap': int(100 * ConfigManager().getFloat('DefaultPreferences', 'SHOOTING_OVERLAP')),
                  'defaultShootingCameraOrientation': ConfigManager().get('DefaultPreferences', 'SHOOTING_CAMERA_ORIENTATION'),
                  'defaultShootingStabilizationDelay': ConfigManager().getFloat('DefaultPreferences', 'SHOOTING_STABILIZATION_DELAY'),
                  'defaultMosaicTemplate': ConfigManager().get('DefaultPreferences', 'MOSAIC_TEMPLATE'),
                  'defaultCameraSensorCoef': ConfigManager().getFloat('DefaultPreferences', 'CAMERA_SENSOR_COEF'),
                  'defaultCameraSensorRatio': ConfigManager().get('DefaultPreferences', 'CAMERA_SENSOR_RATIO'),
                  'defaultCameraTimeValue': ConfigManager().getFloat('DefaultPreferences', 'CAMERA_TIME_VALUE'),
                  'defaultCameraNbPicts' : ConfigManager().getInt('DefaultPreferences', 'CAMERA_NB_PICTS'),
                  'defaultLensFocal': ConfigManager().getFloat('DefaultPreferences', 'LENS_FOCAL'),
                  'defaultLensFisheye': ConfigManager().getBoolean('DefaultPreferences', 'LENS_FISHEYE'),
                  
                  'hardwareDriver': ConfigManager().get('Hardware', 'Driver'),
                  'hardwareBluetoothDeviceAddress': ConfigManager().get('Hardware', 'BLUETOOTH_DEVICE_ADDRESS'),
                  'hardwareSerialPort': ConfigManager().get('Hardware', 'SERIAL_PORT'),
                  'loggerLevel': ConfigManager().get('Logger', 'LOGGER_LEVEL'),
                  'dataFileEnable': ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE')
                }
        self.__view.fillWidgets(values)
