# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Fr�d�ric Mantegazza

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

View

Implements
==========

- ConfigDialog

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import os.path

#import pygtk
#pygtk.require("2.0")
import gtk.glade

path = os.path.dirname(__file__)

from papywizard.common import config
from papywizard.common.loggingServices import Logger


class ConfigDialog(object):
    """ Preference dialog.
    """
    def __init__(self):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "configDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets()

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.validateButton = self.wTree.get_widget("validateButton")
        
        # Shooting preferences
        self.configDialog = self.wTree.get_widget("configDialog")
        self.timeValueSpinbutton = self.wTree.get_widget("timeValueSpinbutton")
        self.nbPictsSpinbutton = self.wTree.get_widget("nbPictsSpinbutton")
        self.stabilizationDelaySpinbutton = self.wTree.get_widget("stabilizationDelaySpinbutton")
        self.sensorCoefSpinbutton = self.wTree.get_widget("sensorCoefSpinbutton")
        self.sensorRatioCombobox = self.wTree.get_widget("sensorRatioCombobox")
        self.overlapSpinbutton = self.wTree.get_widget("overlapSpinbutton")
        self.focalSpinbutton = self.wTree.get_widget("focalSpinbutton")
        self.fisheyeCheckbutton = self.wTree.get_widget("fisheyeCheckbutton")
        self.cameraOrientationCombobox = self.wTree.get_widget("cameraOrientationCombobox")

        # Default shooting preferences
        self.defaultConfigDialog = self.wTree.get_widget("defautConfigDialog")
        self.defaultTimeValueSpinbutton = self.wTree.get_widget("defaultTimeValueSpinbutton")
        self.defaultNbPictsSpinbutton = self.wTree.get_widget("defaultNbPictsSpinbutton")
        self.defaultStabilizationDelaySpinbutton = self.wTree.get_widget("defaultStabilizationDelaySpinbutton")
        self.defaultSensorCoefSpinbutton = self.wTree.get_widget("defaultSensorCoefSpinbutton")
        self.defaultSensorRatioCombobox = self.wTree.get_widget("defaultSensorRatioCombobox")
        self.defaultOverlapSpinbutton = self.wTree.get_widget("defaultOverlapSpinbutton")
        self.defaultFocalSpinbutton = self.wTree.get_widget("defaultFocalSpinbutton")
        self.defaultFisheyeCheckbutton = self.wTree.get_widget("defaultFisheyeCheckbutton")
        self.defaultCameraOrientationCombobox = self.wTree.get_widget("defaultCameraOrientationCombobox")

        # Other preferences
        self.driverCombobox = self.wTree.get_widget("driverCombobox")
        self.bluetoothDeviceAddressEntry = self.wTree.get_widget("bluetoothDeviceAddressEntry")
        self.serialPortEntry = self.wTree.get_widget("serialPortEntry")
        self.loggerLevelCombobox = self.wTree.get_widget("loggerCLevelCombobox")
        self.dataFileEnableCheckbutton = self.wTree.get_widget("dataFileEnableCheckbutton")

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        # Shooting preferences
        self.timeValueSpinbutton.set_value(values['cameraTimeValue'])
        self.nbPictsSpinbutton.set_value(values['cameraNbPicts'])
        self.stabilizationDelaySpinbutton.set_value(values['shootingStabilizationDelay'])
        self.sensorCoefSpinbutton.set_value(values['cameraSensorCoef'])
        self.sensorRatioCombobox.set_active(config.SENSOR_RATIOS_INDEX[values['cameraSensorRatio']])
        self.overlapSpinbutton.set_value(values['shootingOverlap'])
        self.focalSpinbutton.set_value(values['lensFocal'])
        self.fisheyeCheckbutton.set_active(values['lensFisheye'])
        self.cameraOrientationCombobox.set_active(config.CAMERA_ORIENTATION_INDEX[values['shootingCameraOrientation']])

        try:
            
            # Default shooting preferences
            self.defaultTimeValueSpinbutton.set_value(values['defaultCameraTimeValue'])
            self.defaultNbPictsSpinbutton.set_value(values['defaultCameraNbPicts'])
            self.defaultStabilizationDelaySpinbutton.set_value(values['defaultShootingStabilizationDelay'])
            self.defaultSensorCoefSpinbutton.set_value(values['defaultCameraSensorCoef'])
            self.defaultSensorRatioCombobox.set_active(config.SENSOR_RATIOS_INDEX[values['defaultCameraSensorRatio']])
            self.defaultOverlapSpinbutton.set_value(values['defaultShootingOverlap'])
            self.defaultFocalSpinbutton.set_value(values['defaultLensFocal'])
            self.defaultFisheyeCheckbutton.set_active(values['defaultLensFisheye'])
            self.defaultCameraOrientationCombobox.set_active(config.CAMERA_ORIENTATION_INDEX[values['defaultShootingCameraOrientation']])
    
            # Other preferences
            self.driverCombobox.set_active(config.DRIVER_INDEX[values['hardwareDriver']])
            self.bluetoothDeviceAddressEntry.set_text(values['hardwareBluetoothDeviceAddress'])
            self.serialPortEntry.set_text(values['hardwareSerialPort'])
            self.loggerLevelCombobox.set_active(config.LOGGER_INDEX[values['loggerLevel']])
            self.dataFileEnableCheckbutton.set_active(values['dataFileEnable'])
        except KeyError:
            Logger().exception("ConfigDialog.fillWidget()", debug=True)
            