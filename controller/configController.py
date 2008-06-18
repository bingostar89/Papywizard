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
           }
        self.__view.wTree.signal_autoconnect(dic)

        # Fill widgets
        self.refreshView()

    def __onOkButtonClicked(self, widget):
        """ Ok button has been clicked.

        Save back values to model.
        """
        Logger().trace("ConfigController.__onOkButtonClicked()")
        
        # Shooting
        self.__model.camera.timeValue = self.__view.timeValueSpinbutton.get_value()
        self.__model.camera.nbPicts = int(self.__view.nbPictsSpinbutton.get_value())
        self.__model.stabilizationDelay = self.__view.stabilizationDelaySpinbutton.get_value()
        self.__model.camera.sensorCoef = self.__view.sensorCoefSpinbutton.get_value()
        self.__model.camera.sensorRatio = config.SENSOR_RATIOS_INDEX[self.__view.sensorRatioCombobox.get_active()]
        self.__model.overlap = self.__view.overlapSpinbutton.get_value() / 100.
        self.__model.camera.lens.focal = self.__view.focalSpinbutton.get_value()
        self.__model.camera.lens.fisheye = self.__view.fisheyeCheckbutton.get_active()
        self.__model.cameraOrientation = config.CAMERA_ORIENTATION_INDEX[self.__view.cameraOrientationCombobox.get_active()]

        # Hardware
        ConfigManager().set('Hardware', 'DRIVER', 
                            config.DRIVER_INDEX[self.__view.driverCombobox.get_active()])
        ConfigManager().set('Hardware', 'BLUETOOTH_DEVICE_ADDRESS', self.__view.bluetoothDeviceAddressEntry.get_text())
        ConfigManager().set('Hardware', 'SERIAL_PORT', self.__view.serialPortEntry.get_text())
        
        # Misc
        ConfigManager().set('Logger', 'LOGGER_LEVEL',
                            config.LOGGER_INDEX[self.__view.loggerLevelCombobox.get_active()])
        ConfigManager().setBoolean('Data', 'DATA_FILE_ENABLE', self.__view.dataFileEnableCheckbutton.get_active())

    def __onCancelButtonClicked(self, widget):
        """ Cancel button has been clicked.

        Close the pref. dialog.
        """
        Logger().trace("ConfigController.__onCancelButtonClicked()")

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
                  
                  'hardwareDriver': ConfigManager().get('Hardware', 'Driver'),
                  'hardwareBluetoothDeviceAddress': ConfigManager().get('Hardware', 'BLUETOOTH_DEVICE_ADDRESS'),
                  'hardwareSerialPort': ConfigManager().get('Hardware', 'SERIAL_PORT'),
                  'loggerLevel': ConfigManager().get('Logger', 'LOGGER_LEVEL'),
                  'dataFileEnable': ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE')
                }
        self.__view.fillWidgets(values)
