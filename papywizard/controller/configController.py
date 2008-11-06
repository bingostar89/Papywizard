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

- ConfigController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import pygtk
pygtk.require("2.0")
import gtk

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractController
from papywizard.controller.messageController import WarningMessageController
from papywizard.controller.bluetoothChooserController import BluetoothChooserController


class ConfigController(AbstractController):
    """ Configuration controller object.
    """
    def _init(self):
        self._gladeFile = "configDialog.glade"
        self._signalDict = {"on_okButton_clicked": self.__onOkButtonClicked,
                            "on_cancelButton_clicked": self.__onCancelButtonClicked,
                            "on_lensTypeCombobox_changed": self.__onLensTypeComboboxChanged,
                            "on_driverCombobox_changed": self.__onDriverComboboxChanged,
                            "on_bluetoothChooseButton_clicked": self.__onBluetoothChooseButtonClicked,
                        }

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        super(ConfigController, self)._retreiveWidgets()

        self.stabilizationDelaySpinbutton = self.wTree.get_widget("stabilizationDelaySpinbutton")
        self.cameraOrientationCombobox = self.wTree.get_widget("cameraOrientationCombobox")
        self.overlapSpinbutton = self.wTree.get_widget("overlapSpinbutton")
        self.overlapSquareCheckbutton = self.wTree.get_widget("overlapSquareCheckbutton")
        self.startFromCombobox = self.wTree.get_widget("startFromCombobox")
        self.initialDirectionCombobox = self.wTree.get_widget("initialDirectionCombobox")
        self.crCheckbutton = self.wTree.get_widget("crCheckbutton")
        self.timeValueSpinbutton = self.wTree.get_widget("timeValueSpinbutton")
        self.bracketingNbPictsSpinbutton = self.wTree.get_widget("bracketingNbPictsSpinbutton")
        self.bracketingIntentCombobox = self.wTree.get_widget("bracketingIntentCombobox")
        self.sensorCoefSpinbutton = self.wTree.get_widget("sensorCoefSpinbutton")
        self.sensorRatioCombobox = self.wTree.get_widget("sensorRatioCombobox")
        self.mirrorLockupCheckbutton = self.wTree.get_widget("mirrorLockupCheckbutton")
        self.lensTypeCombobox = self.wTree.get_widget("lensTypeCombobox")
        self.focalLabel = self.wTree.get_widget("focalLabel")
        self.focalSpinbutton = self.wTree.get_widget("focalSpinbutton")
        self.driverCombobox = self.wTree.get_widget("driverCombobox")
        self.bluetoothDeviceAddressLabel = self.wTree.get_widget("bluetoothDeviceAddressLabel")
        self.bluetoothDeviceAddressEntry = self.wTree.get_widget("bluetoothDeviceAddressEntry")
        self.bluetoothChooseButton = self.wTree.get_widget("bluetoothChooseButton")
        self.serialPortLabel = self.wTree.get_widget("serialPortLabel")
        self.serialPortEntry = self.wTree.get_widget("serialPortEntry")
        self.ethernetHostPortLabel = self.wTree.get_widget("ethernetHostPortLabel")
        self.ethernetHostEntry = self.wTree.get_widget("ethernetHostEntry")
        self.ethernetPortSpinbutton = self.wTree.get_widget("ethernetPortSpinbutton")
        self.hardwareAutoConnectCheckbutton = self.wTree.get_widget("hardwareAutoConnectCheckbutton")
        self.loggerLevelCombobox = self.wTree.get_widget("loggerCLevelCombobox")
        self.dataFileFormatEntry = self.wTree.get_widget("dataFileFormatEntry")
        self.dataStorageDirFilechooserbutton = self.wTree.get_widget("dataStorageDirFilechooserbutton")

    # Callbacks
    def __onOkButtonClicked(self, widget):
        """ Ok button has been clicked.

        Save back values to model.
        """
        Logger().trace("ConfigController.__onOkButtonClicked()")

        self._model.stabilizationDelay = self.stabilizationDelaySpinbutton.get_value()
        self._model.cameraOrientation = config.SHOOTING_ORIENTATION_INDEX[self.cameraOrientationCombobox.get_active()]
        self._model.mosaic.overlap = self.overlapSpinbutton.get_value() / 100.
        self._model.mosaic.overlapSquare = self.overlapSquareCheckbutton.get_active()
        self._model.mosaic.startFrom = config.MOSAIC_START_FROM_INDEX[self.startFromCombobox.get_active()]
        self._model.mosaic.initialDirection = config.MOSAIC_INITIAL_DIR_INDEX[self.initialDirectionCombobox.get_active()]
        self._model.mosaic.cr = self.crCheckbutton.get_active()
        self._model.camera.timeValue = self.timeValueSpinbutton.get_value()
        self._model.camera.bracketingNbPicts = int(self.bracketingNbPictsSpinbutton.get_value())
        self._model.camera.bracketingIntent = config.CAMERA_BRACKETING_INTENT_INDEX[self.bracketingIntentCombobox.get_active()]
        self._model.camera.sensorCoef = self.sensorCoefSpinbutton.get_value()
        self._model.camera.sensorRatio = config.SENSOR_RATIOS_INDEX[self.sensorRatioCombobox.get_active()]
        self._model.camera.mirrorLockup = self.mirrorLockupCheckbutton.get_active()
        self._model.camera.lens.type_ = config.LENS_TYPE_INDEX[self.lensTypeCombobox.get_active()]
        self._model.camera.lens.focal = self.focalSpinbutton.get_value()
        ConfigManager().set('Hardware', 'DRIVER',
                            config.DRIVER_INDEX[self.driverCombobox.get_active()])
        ConfigManager().set('Hardware', 'BLUETOOTH_DEVICE_ADDRESS', self.bluetoothDeviceAddressEntry.get_text())
        ConfigManager().set('Hardware', 'SERIAL_PORT', self.serialPortEntry.get_text())
        ConfigManager().set('Hardware', 'ETHERNET_HOST', self.ethernetHostEntry.get_text())
        ConfigManager().setInt('Hardware', 'ETHERNET_PORT', int(self.ethernetPortSpinbutton.get_value()))
        ConfigManager().setBoolean('Hardware', 'AUTO_CONNECT', self.hardwareAutoConnectCheckbutton.get_active())
        ConfigManager().set('Logger', 'LOGGER_LEVEL',
                            config.LOGGER_INDEX[self.loggerLevelCombobox.get_active()])
        ConfigManager().set('Data', 'DATA_FILE_FORMAT', self.dataFileFormatEntry.get_text())
        newDir = self.dataStorageDirFilechooserbutton.get_current_folder()
        ConfigManager().set('Data', 'DATA_STORAGE_DIR', newDir)
        ConfigManager().save()

    def __onCancelButtonClicked(self, widget):
        """ Cancel button has been clicked.

        Close the pref. dialog.
        """
        Logger().trace("ConfigController.__onCancelButtonClicked()")

    def __onLensTypeComboboxChanged(self, widget):
        """ Lens type combobox has changed.

        Enable/disable focal lens.
        """
        Logger().trace("ConfigController.__onLensTypeComboboxChanged()")
        type_ = config.LENS_TYPE_INDEX[self.lensTypeCombobox.get_active()]
        if type_ == 'fisheye' and self._model.mode == 'mosaic':
            WarningMessageController(_("Wrong value for lens type"), _("Can't set lens type to 'fisheye'\n" \
                                                                       "while in 'mosaic' mode"))
            self.lensTypeCombobox.set_active(config.LENS_TYPE_INDEX['rectilinear'])
        else:
            if type_ == 'rectilinear':
                self.focalLabel.set_sensitive(True)
                self.focalSpinbutton.set_sensitive(True)
            else:
                self.focalLabel.set_sensitive(False)
                self.focalSpinbutton.set_sensitive(False)
            Logger().debug("ConfigController.__onLensTypeComboboxChanged(): lens type set to '%s'" % type_)

    def __onDriverComboboxChanged(self, widget):
        """ Driver combobox has changed.

        Enable/disable BT address / serial port.
        """
        Logger().trace("ConfigController.__onDriverComboboxChanged()")
        driver = config.DRIVER_INDEX[self.driverCombobox.get_active()]
        if driver == 'bluetooth':
            self.bluetoothDeviceAddressLabel.set_sensitive(True)
            self.bluetoothDeviceAddressEntry.set_sensitive(True)
            self.bluetoothChooseButton.set_sensitive(True)
            self.serialPortLabel.set_sensitive(False)
            self.serialPortEntry.set_sensitive(False)
            self.ethernetHostPortLabel.set_sensitive(False)
            self.ethernetHostEntry.set_sensitive(False)
            self.ethernetPortSpinbutton.set_sensitive(False)
        elif driver == 'serial':
            self.bluetoothDeviceAddressLabel.set_sensitive(False)
            self.bluetoothDeviceAddressEntry.set_sensitive(False)
            self.bluetoothChooseButton.set_sensitive(False)
            self.serialPortLabel.set_sensitive(True)
            self.serialPortEntry.set_sensitive(True)
            self.ethernetHostPortLabel.set_sensitive(False)
            self.ethernetHostEntry.set_sensitive(False)
            self.ethernetPortSpinbutton.set_sensitive(False)
        elif driver == 'ethernet':
            self.bluetoothDeviceAddressLabel.set_sensitive(False)
            self.bluetoothDeviceAddressEntry.set_sensitive(False)
            self.bluetoothChooseButton.set_sensitive(False)
            self.serialPortLabel.set_sensitive(False)
            self.serialPortEntry.set_sensitive(False)
            self.ethernetHostPortLabel.set_sensitive(True)
            self.ethernetHostEntry.set_sensitive(True)
            self.ethernetPortSpinbutton.set_sensitive(True)

    def __onBluetoothChooseButtonClicked(self, widget):
        """ Choose bluetooth button clicked.

        Open the bluetooth chooser dialog.
        """
        Logger().trace("ConfigController.__onBluetoothChooseButtonClicked()")
        controller = BluetoothChooserController(self, self._model, self._serializer)
        response = controller.run()
        controller.destroyView()
        if response == 0:
            address, name = controller.getSelectedBluetoothAddress()
            Logger().debug("ConfigController.__onChooseBluetoothButtonClicked(): address=%s, name=%s" % \
                            (address, name))
            self.bluetoothDeviceAddressEntry.set_text(address)

    # Real work
    def refreshView(self):
        self.stabilizationDelaySpinbutton.set_value(self._model.stabilizationDelay)
        self.cameraOrientationCombobox.set_active(config.SHOOTING_ORIENTATION_INDEX[self._model.cameraOrientation])
        self.overlapSpinbutton.set_value(int(100 * self._model.mosaic.overlap))
        self.overlapSquareCheckbutton.set_active(self._model.mosaic.overlapSquare)
        self.startFromCombobox.set_active(config.MOSAIC_START_FROM_INDEX[self._model.mosaic.startFrom])
        self.initialDirectionCombobox.set_active(config.MOSAIC_INITIAL_DIR_INDEX[self._model.mosaic.initialDirection])
        self.crCheckbutton.set_active(self._model.mosaic.cr)
        self.timeValueSpinbutton.set_value(self._model.camera.timeValue)
        self.bracketingNbPictsSpinbutton.set_value(self._model.camera.bracketingNbPicts)
        self.bracketingIntentCombobox.set_active(config.CAMERA_BRACKETING_INTENT_INDEX[self._model.camera.bracketingIntent])
        self.sensorCoefSpinbutton.set_value(self._model.camera.sensorCoef)
        self.sensorRatioCombobox.set_active(config.SENSOR_RATIOS_INDEX[self._model.camera.sensorRatio])
        self.mirrorLockupCheckbutton.set_active(self._model.camera.mirrorLockup)
        self.lensTypeCombobox.set_active(config.LENS_TYPE_INDEX[self._model.camera.lens.type_])
        self.focalSpinbutton.set_value(self._model.camera.lens.focal)
        try:
            driverIndex = config.DRIVER_INDEX[ConfigManager().get('Hardware', 'Driver')]
        except KeyError:
            driverIndex = 0
        self.driverCombobox.set_active(driverIndex)
        self.bluetoothDeviceAddressEntry.set_text(ConfigManager().get('Hardware', 'BLUETOOTH_DEVICE_ADDRESS'))
        self.serialPortEntry.set_text(ConfigManager().get('Hardware', 'SERIAL_PORT'))
        self.ethernetHostEntry.set_text(ConfigManager().get('Hardware', 'ETHERNET_HOST'))
        self.ethernetPortSpinbutton.set_value(ConfigManager().getInt('Hardware', 'ETHERNET_PORT'))
        self.hardwareAutoConnectCheckbutton.set_active(ConfigManager().getBoolean('Hardware', 'AUTO_CONNECT'))
        self.loggerLevelCombobox.set_active(config.LOGGER_INDEX[ConfigManager().get('Logger', 'LOGGER_LEVEL')])
        self.dataFileFormatEntry.set_text(ConfigManager().get('Data', 'DATA_FILE_FORMAT'))
        dataStorageDir = ConfigManager().get('Data', 'DATA_STORAGE_DIR')
        if not dataStorageDir:
            dataStorageDir = config.DATA_STORAGE_DIR
        self.dataStorageDirFilechooserbutton.set_current_folder(dataStorageDir)
