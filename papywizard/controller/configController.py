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
from papywizard.common.helpers import hmsAsStrToS, hmsToS, sToHms, sToHmsAsStr
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
                            "on_cameraOrientationCombobox_changed": self.__onCameraOrientationComboboxChanged,
                            "on_lensTypeCombobox_changed": self.__onLensTypeComboboxChanged,
                            "on_driverCombobox_changed": self.__onDriverComboboxChanged,
                            "on_bluetoothChooseButton_clicked": self.__onBluetoothChooseButtonClicked,
                        }

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        super(ConfigController, self)._retreiveWidgets()

        self.notebook = self.wTree.get_widget("notebook")

        # Shooting page
        self.headOrientationCombobox = self.wTree.get_widget("headOrientationCombobox")
        self.cameraOrientationCombobox = self.wTree.get_widget("cameraOrientationCombobox")
        self.cameraRollSpinbutton = self.wTree.get_widget("cameraRollSpinbutton")
        self.stabilizationDelaySpinbutton = self.wTree.get_widget("stabilizationDelaySpinbutton")

        # Mosaic page
        self.overlapSpinbutton = self.wTree.get_widget("overlapSpinbutton")
        self.startFromCombobox = self.wTree.get_widget("startFromCombobox")
        self.initialDirectionCombobox = self.wTree.get_widget("initialDirectionCombobox")
        self.crCheckbutton = self.wTree.get_widget("crCheckbutton")

        # Camera page
        self.timeValueSpinbutton = self.wTree.get_widget("timeValueSpinbutton")
        self.bracketingNbPictsSpinbutton = self.wTree.get_widget("bracketingNbPictsSpinbutton")
        self.bracketingIntentCombobox = self.wTree.get_widget("bracketingIntentCombobox")
        self.sensorCoefSpinbutton = self.wTree.get_widget("sensorCoefSpinbutton")
        self.sensorRatioCombobox = self.wTree.get_widget("sensorRatioCombobox")
        self.mirrorLockupCheckbutton = self.wTree.get_widget("mirrorLockupCheckbutton")

        # Lens page
        self.lensTypeCombobox = self.wTree.get_widget("lensTypeCombobox")
        self.focalLabel = self.wTree.get_widget("focalLabel")
        self.focalSpinbutton = self.wTree.get_widget("focalSpinbutton")

        # Hardware page
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

        # Data page
        self.dataStorageDirFilechooserbutton = self.wTree.get_widget("dataStorageDirFilechooserbutton")
        self.dataFileFormatEntry = self.wTree.get_widget("dataFileFormatEntry")
        self.dataFileEnableCheckbutton = self.wTree.get_widget("dataFileEnableCheckbutton")
        self.dataTitleEntry = self.wTree.get_widget("dataTitleEntry")
        self.dataGpsEntry = self.wTree.get_widget("dataGpsEntry")
        self.dataCommentEntry = self.wTree.get_widget("dataCommentEntry")

        # Timer page
        self.timerAfterHourSpinbutton = self.wTree.get_widget("timerAfterHourSpinbutton")
        self.timerAfterMinuteSpinbutton = self.wTree.get_widget("timerAfterMinuteSpinbutton")
        self.timerAfterSecondSpinbutton = self.wTree.get_widget("timerAfterSecondSpinbutton")
        self.timerAfterEnableCheckbutton = self.wTree.get_widget("timerAfterEnableCheckbutton")
        self.timerRepeatSpinbutton = self.wTree.get_widget("timerRepeatSpinbutton")
        self.timerRepeatEnableCheckbutton = self.wTree.get_widget("timerRepeatEnableCheckbutton")
        self.timerEveryHourSpinbutton = self.wTree.get_widget("timerEveryHourSpinbutton")
        self.timerEveryMinuteSpinbutton = self.wTree.get_widget("timerEveryMinuteSpinbutton")
        self.timerEverySecondSpinbutton = self.wTree.get_widget("timerEverySecondSpinbutton")

        # Misc page
        self.loggerLevelCombobox = self.wTree.get_widget("loggerLevelCombobox")

    def _initWidgets(self):
        pass

    # Callbacks
    def __onOkButtonClicked(self, widget):
        """ Ok button has been clicked.

        Save back values to model.
        """
        Logger().trace("ConfigController.__onOkButtonClicked()")

        # Shooting page
        self._model.headOrientation = config.HEAD_ORIENTATION_INDEX[self.headOrientationCombobox.get_active()]
        self._model.cameraOrientation = config.CAMERA_ORIENTATION_INDEX[self.cameraOrientationCombobox.get_active()]
        if self._model.cameraOrientation == 'custom':
            self._model.cameraRoll = self.cameraRollSpinbutton.get_value()
        self._model.stabilizationDelay = self.stabilizationDelaySpinbutton.get_value()

        # Mosaic page
        self._model.mosaic.overlap = self.overlapSpinbutton.get_value() / 100.
        self._model.mosaic.startFrom = config.MOSAIC_START_FROM_INDEX[self.startFromCombobox.get_active()]
        self._model.mosaic.initialDirection = config.MOSAIC_INITIAL_DIR_INDEX[self.initialDirectionCombobox.get_active()]
        self._model.mosaic.cr = self.crCheckbutton.get_active()

        # Camera page
        self._model.camera.timeValue = self.timeValueSpinbutton.get_value()
        self._model.camera.bracketingNbPicts = int(self.bracketingNbPictsSpinbutton.get_value())
        self._model.camera.bracketingIntent = config.CAMERA_BRACKETING_INTENT_INDEX[self.bracketingIntentCombobox.get_active()]
        self._model.camera.sensorCoef = self.sensorCoefSpinbutton.get_value()
        self._model.camera.sensorRatio = config.SENSOR_RATIOS_INDEX[self.sensorRatioCombobox.get_active()]
        self._model.camera.mirrorLockup = self.mirrorLockupCheckbutton.get_active()

        # Lens page
        self._model.camera.lens.type_ = config.LENS_TYPE_INDEX[self.lensTypeCombobox.get_active()]
        self._model.camera.lens.focal = self.focalSpinbutton.get_value()

        # Hardware page
        ConfigManager().set('Preferences', 'HARDWARE_DRIVER',
                            config.DRIVER_INDEX[self.driverCombobox.get_active()])
        ConfigManager().set('Preferences', 'HARDWARE_BLUETOOTH_DEVICE_ADDRESS', self.bluetoothDeviceAddressEntry.get_text())
        ConfigManager().set('Preferences', 'HARDWARE_SERIAL_PORT', self.serialPortEntry.get_text())
        ConfigManager().set('Preferences', 'HARDWARE_ETHERNET_HOST', self.ethernetHostEntry.get_text())
        ConfigManager().setInt('Preferences', 'HARDWARE_ETHERNET_PORT', int(self.ethernetPortSpinbutton.get_value()))
        ConfigManager().setBoolean('Preferences', 'HARDWARE_AUTO_CONNECT', self.hardwareAutoConnectCheckbutton.get_active())

        # Data page
        newDir = self.dataStorageDirFilechooserbutton.get_current_folder()
        ConfigManager().set('Preferences', 'DATA_STORAGE_DIR', newDir)
        ConfigManager().set('Preferences', 'DATA_FILE_FORMAT', self.dataFileFormatEntry.get_text())
        ConfigManager().setBoolean('Preferences', 'DATA_FILE_ENABLE', bool(self.dataFileEnableCheckbutton.get_active()))
        ConfigManager().set('Preferences', 'DATA_TITLE', self.dataTitleEntry.get_text())
        ConfigManager().set('Preferences', 'DATA_GPS', self.dataGpsEntry.get_text())
        ConfigManager().set('Preferences', 'DATA_COMMENT', self.dataCommentEntry.get_text())

        # Timer page
        h = self.timerAfterHourSpinbutton.get_value()
        m = self.timerAfterMinuteSpinbutton.get_value()
        s = self.timerAfterSecondSpinbutton.get_value()
        self._model.timerAfter = hmsToS(h, m, s)
        self._model.timerAfterEnable = self.timerAfterEnableCheckbutton.get_active()
        self._model.timerRepeat = self.timerRepeatSpinbutton.get_value()
        self._model.timerRepeatEnable = self.timerRepeatEnableCheckbutton.get_active()
        h = self.timerEveryHourSpinbutton.get_value()
        m = self.timerEveryMinuteSpinbutton.get_value()
        s = self.timerEverySecondSpinbutton.get_value()
        self._model.timerEvery = hmsToS(h, m, s)

        # Misc page
        ConfigManager().set('Preferences', 'LOGGER_LEVEL',
                            config.LOGGER_INDEX[self.loggerLevelCombobox.get_active()])

        ConfigManager().save()

    def __onCancelButtonClicked(self, widget):
        """ Cancel button has been clicked.

        Close the pref. dialog.
        """
        Logger().trace("ConfigController.__onCancelButtonClicked()")

    def __onCameraOrientationComboboxChanged(self, widget):
        """ Camera orientation changed.
        """
        orientation = config.CAMERA_ORIENTATION_INDEX[self.cameraOrientationCombobox.get_active()]
        Logger().debug("ConfigController.__onCancelButtonClicked(): orientation=%s" % orientation)
        if orientation == 'portrait':
            self.cameraRollSpinbutton.set_sensitive(False)
            self.cameraRollSpinbutton.set_value(90.)
        elif orientation == 'landscape':
            self.cameraRollSpinbutton.set_sensitive(False)
            self.cameraRollSpinbutton.set_value(0.)
        else:
            if self._model.mode == 'mosaic':
                WarningMessageController(_("Wrong value for camera orientation"),
                                         _("Can't set camera orientation to 'custom'\nwhile in 'mosaic' mode"))
                self.cameraOrientationCombobox.set_active(config.CAMERA_ORIENTATION_INDEX[self._model.cameraOrientation])
            else:
                self.cameraRollSpinbutton.set_sensitive(True)
                self.cameraRollSpinbutton.set_value(self._model.cameraRoll)

    def __onLensTypeComboboxChanged(self, widget):
        """ Lens type combobox has changed.

        Enable/disable focal lens.
        """
        Logger().trace("ConfigController.__onLensTypeComboboxChanged()")
        type_ = config.LENS_TYPE_INDEX[self.lensTypeCombobox.get_active()]
        if type_ == 'fisheye' and self._model.mode == 'mosaic':
            WarningMessageController(_("Wrong value for lens type"),
                                     _("Can't set lens type to 'fisheye'\nwhile in 'mosaic' mode"))
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
        controller.shutdown()
        if response == 0:
            address, name = controller.getSelectedBluetoothAddress()
            Logger().debug("ConfigController.__onChooseBluetoothButtonClicked(): address=%s, name=%s" % \
                            (address, name))
            self.bluetoothDeviceAddressEntry.set_text(address)

    # Interface
    def selectPage(self, pageNum, disable=False):
        """ Select the specified page.

        @param pageNum: page num
        @type pageNum: int

        @param disable: if True, disable all other pages
        @type disable: bool
        """
        self.notebook.set_current_page(pageNum)
        #self.notebook.set_show_tabs(False)
        for iPage in xrange(self.notebook.get_n_pages()):
            if pageNum != iPage:
                page = self.notebook.get_nth_page(iPage)
                page.set_sensitive(False)
                label = self.notebook.get_tab_label(page)
                label.set_sensitive(False)

    def refreshView(self):

        # Shooting page
        self.headOrientationCombobox.set_active(config.HEAD_ORIENTATION_INDEX[self._model.headOrientation])
        self.cameraOrientationCombobox.set_active(config.CAMERA_ORIENTATION_INDEX[self._model.cameraOrientation])
        self.stabilizationDelaySpinbutton.set_value(self._model.stabilizationDelay)

        # Mosaic page
        self.overlapSpinbutton.set_value(int(100 * self._model.mosaic.overlap))
        self.startFromCombobox.set_active(config.MOSAIC_START_FROM_INDEX[self._model.mosaic.startFrom])
        self.initialDirectionCombobox.set_active(config.MOSAIC_INITIAL_DIR_INDEX[self._model.mosaic.initialDirection])
        self.crCheckbutton.set_active(self._model.mosaic.cr)

        # Camera page
        self.timeValueSpinbutton.set_value(self._model.camera.timeValue)
        self.bracketingNbPictsSpinbutton.set_value(self._model.camera.bracketingNbPicts)
        self.bracketingIntentCombobox.set_active(config.CAMERA_BRACKETING_INTENT_INDEX[self._model.camera.bracketingIntent])
        self.sensorCoefSpinbutton.set_value(self._model.camera.sensorCoef)
        self.sensorRatioCombobox.set_active(config.SENSOR_RATIOS_INDEX[self._model.camera.sensorRatio])
        self.mirrorLockupCheckbutton.set_active(self._model.camera.mirrorLockup)

        # Lens page
        self.lensTypeCombobox.set_active(config.LENS_TYPE_INDEX[self._model.camera.lens.type_])
        self.focalSpinbutton.set_value(self._model.camera.lens.focal)
        try:
            driverIndex = config.DRIVER_INDEX[ConfigManager().get('Preferences', 'HARDWARE_DRIVER')]
        except KeyError:
            driverIndex = 0

        # Hardware page
        self.driverCombobox.set_active(driverIndex)
        self.bluetoothDeviceAddressEntry.set_text(ConfigManager().get('Preferences', 'HARDWARE_BLUETOOTH_DEVICE_ADDRESS'))
        self.serialPortEntry.set_text(ConfigManager().get('Preferences', 'HARDWARE_SERIAL_PORT'))
        self.ethernetHostEntry.set_text(ConfigManager().get('Preferences', 'HARDWARE_ETHERNET_HOST'))
        self.ethernetPortSpinbutton.set_value(ConfigManager().getInt('Preferences', 'HARDWARE_ETHERNET_PORT'))
        self.hardwareAutoConnectCheckbutton.set_active(ConfigManager().getBoolean('Preferences', 'HARDWARE_AUTO_CONNECT'))

        # Data page
        dataStorageDir = ConfigManager().get('Preferences', 'DATA_STORAGE_DIR')
        self.dataFileFormatEntry.set_text(ConfigManager().get('Preferences', 'DATA_FILE_FORMAT'))
        if not dataStorageDir:
            dataStorageDir = config.DATA_STORAGE_DIR
        self.dataStorageDirFilechooserbutton.set_current_folder(dataStorageDir)
        self.dataFileEnableCheckbutton.set_active(ConfigManager().getBoolean('Preferences', 'DATA_FILE_ENABLE'))
        self.dataTitleEntry.set_text(ConfigManager().get('Preferences', 'DATA_TITLE'))
        self.dataGpsEntry.set_text(ConfigManager().get('Preferences', 'DATA_GPS'))
        self.dataCommentEntry.set_text(ConfigManager().get('Preferences', 'DATA_COMMENT'))

        # Timer page
        h, m, s = sToHms(self._model.timerAfter)
        self.timerAfterHourSpinbutton.set_value(h)
        self.timerAfterMinuteSpinbutton.set_value(m)
        self.timerAfterSecondSpinbutton.set_value(s)
        self.timerAfterEnableCheckbutton.set_active(self._model.timerAfterEnable)
        self.timerRepeatSpinbutton.set_value(self._model.timerRepeat)
        self.timerRepeatEnableCheckbutton.set_active(self._model.timerRepeatEnable)
        h, m, s = sToHms(self._model.timerEvery)
        self.timerEveryHourSpinbutton.set_value(h)
        self.timerEveryMinuteSpinbutton.set_value(m)
        self.timerEverySecondSpinbutton.set_value(s)

        # Misc page
        self.loggerLevelCombobox.set_active(config.LOGGER_INDEX[ConfigManager().get('Preferences', 'LOGGER_LEVEL')])
