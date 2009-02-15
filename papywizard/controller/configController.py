# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2009 Frédéric Mantegazza

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
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.helpers import hmsAsStrToS, hmsToS, sToHms, sToHmsAsStr
from papywizard.common.loggingServices import Logger
from papywizard.controller.abstractController import AbstractModalDialogController
from papywizard.controller.bluetoothChooserController import BluetoothChooserController
from papywizard.view.messageDialog import WarningMessageDialog


class ConfigController(AbstractModalDialogController):
    """ Configuration controller object.
    """
    def _init(self):
        self._uiFile = "configDialog.ui"

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        super(ConfigController, self)._retreiveWidgets()

    def _initWidgets(self):
        pass

    def _connectQtSignals(self):
        super(ConfigController, self)._connectQtSignals()

        self.connect(self._view.buttonBox, QtCore.SIGNAL("accepted()"), self.__onAccepted)
        self.connect(self._view.buttonBox, QtCore.SIGNAL("rejected()"), self.__onRejected)

        self.connect(self._view.cameraOrientationComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onCameraOrientationComboBoxCurrentIndexChanged)
        self.connect(self._view.bracketingNbPictsSpinBox, QtCore.SIGNAL("valueChanged(int)"), self.__onBracketingNbPictsSpinBoxValueChanged)
        self.connect(self._view.lensTypeComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onLensTypeComboBoxCurrentIndexChanged)
        self.connect(self._view.driverComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onDriverComboBoxCurrentIndexChanged)
        self.connect(self._view.bluetoothChoosePushButton, QtCore.SIGNAL("clicked()"), self.__onBluetoothChoosePushButtonClicked)
        self.connect(self._view.dataStorageDirPushButton, QtCore.SIGNAL("clicked()"), self.__onDataStorageDirPushButtonClicked)

    def _connectSignals(self):
        pass

    def _disconnectSignals(self):
        pass

    # Callbacks
    def __onAccepted(self):
        """ Ok button has been clicked.

        Save back values to model.
        """
        Logger().trace("ConfigController.__onAccepted()")

        # Shooting tab
        self._model.headOrientation = config.HEAD_ORIENTATION_INDEX[self._view.headOrientationComboBox.currentIndex()]
        self._model.cameraOrientation = config.CAMERA_ORIENTATION_INDEX[self._view.cameraOrientationComboBox.currentIndex()]
        if self._model.cameraOrientation == 'custom':
            self._model.cameraRoll = self._view.cameraRollDoubleSpinBox.value()
        self._model.stabilizationDelay = self._view.stabilizationDelayDoubleSpinBox.value()

        # Mosaic tab
        self._model.mosaic.overlap = self._view.overlapSpinBox.value() / 100.
        self._model.mosaic.startFrom = config.MOSAIC_START_FROM_INDEX[self._view.startFromComboBox.currentIndex()]
        self._model.mosaic.initialDirection = config.MOSAIC_INITIAL_DIR_INDEX[self._view.initialDirectionComboBox.currentIndex()]
        self._model.mosaic.cr = self._view.crCheckBox.isChecked()

        # Camera tab
        self._model.camera.timeValue = self._view.timeValueDoubleSpinBox.value()
        self._model.camera.mirrorLockup = self._view.mirrorLockupCheckBox.isChecked()
        self._model.camera.pulseWidthHigh = self._view.pulseWidthHighSpinBox.value()
        self._model.camera.pulseWidthLow = self._view.pulseWidthLowSpinBox.value()
        self._model.camera.bracketingNbPicts = self._view.bracketingNbPictsSpinBox.value()
        self._model.camera.bracketingIntent = config.CAMERA_BRACKETING_INTENT_INDEX[self._view.bracketingIntentComboBox.currentIndex()]
        self._model.camera.sensorCoef = self._view.sensorCoefDoubleSpinBox.value()
        self._model.camera.sensorRatio = config.SENSOR_RATIO_INDEX[self._view.sensorRatioComboBox.currentIndex()]
        self._model.camera.sensorResolution = self._view.sensorResolutionDoubleSpinBox.value()

        # Lens tab
        self._model.camera.lens.type_ = config.LENS_TYPE_INDEX[self._view.lensTypeComboBox.currentIndex()]
        self._model.camera.lens.focal = self._view.focalDoubleSpinBox.value()
        self._model.camera.lens.opticalMultiplier = self._view.opticalMultiplierDoubleSpinBox.value()

        # Hardware tab
        ConfigManager().set('Preferences', 'HARDWARE_DRIVER', config.DRIVER_INDEX[self._view.driverComboBox.currentIndex()])
        ConfigManager().set('Preferences', 'HARDWARE_BLUETOOTH_DEVICE_ADDRESS', str(self._view.bluetoothDeviceAddressLineEdit.text()))
        ConfigManager().set('Preferences', 'HARDWARE_SERIAL_PORT', str(self._view.serialPortLineEdit.text()))
        ConfigManager().set('Preferences', 'HARDWARE_ETHERNET_HOST', str(self._view.ethernetHostLineEdit.text()))
        ConfigManager().setInt('Preferences', 'HARDWARE_ETHERNET_PORT', self._view.ethernetPortSpinBox.value())
        ConfigManager().setBoolean('Preferences', 'HARDWARE_AUTO_CONNECT', self._view.hardwareAutoConnectCheckBox.isChecked())

        # Data tab
        ConfigManager().set('Preferences', 'DATA_STORAGE_DIR', str(self._view.dataStorageDirLineEdit.text()))
        ConfigManager().set('Preferences', 'DATA_FILE_FORMAT', str(self._view.dataFileFormatLineEdit.text()))
        ConfigManager().setBoolean('Preferences', 'DATA_FILE_ENABLE', bool(self._view.dataFileEnableCheckBox.isChecked()))
        ConfigManager().set('Preferences', 'DATA_TITLE', str(self._view.dataTitleLineEdit.text()))
        ConfigManager().set('Preferences', 'DATA_GPS', str(self._view.dataGpsLineEdit.text()))
        ConfigManager().set('Preferences', 'DATA_COMMENT', str(self._view.dataCommentLineEdit.text()))

        # Timer tab
        time_ = self._view.timerAfterTimeEdit.time()
        self._model.timerAfter = hmsAsStrToS(time_.toString("hh:mm:ss"))
        self._model.timerAfterEnable = self._view.timerAfterEnableCheckBox.isChecked()
        self._model.timerRepeat = self._view.timerRepeatSpinBox.value()
        self._model.timerRepeatEnable = self._view.timerRepeatEnableCheckBox.isChecked()
        time_ = self._view.timerEveryTimeEdit.time()
        self._model.timerEvery = hmsAsStrToS(time_.toString("hh:mm:ss"))

        # Misc tab
        ConfigManager().set('Preferences', 'LOGGER_LEVEL', config.LOGGER_INDEX[self._view.loggerLevelComboBox.currentIndex()])

        ConfigManager().save()

    def __onRejected(self):
        """ Cancel button has been clicked.

        Close the pref. dialog.
        """
        Logger().trace("ConfigController.__onRejected()")

    def __onCameraOrientationComboBoxCurrentIndexChanged(self, index):
        """ Camera orientation changed.
        """
        orientation = config.CAMERA_ORIENTATION_INDEX[index]
        Logger().debug("ConfigController.__onCameraOrientationComboBoxCurrentIndexChanged(): orientation=%s" % orientation)
        if orientation == 'portrait':
            self._view.cameraRollDoubleSpinBox.setEnabled(False)
            self._view.cameraRollDoubleSpinBox.setValue(90.)
        elif orientation == 'landscape':
            self._view.cameraRollDoubleSpinBox.setEnabled(False)
            self._view.cameraRollDoubleSpinBox.setValue(0.)
        else:
            if self._model.mode == 'mosaic':
                dialog = WarningMessageDialog(self.tr("Wrong value for camera orientation"),
                                              self.tr("Can't set camera orientation to 'custom' while in 'mosaic' mode"))
                dialog.exec_()
                self._view.cameraOrientationComboBox.setCurrentIndex(self._view.cameraOrientationComboBox.findText(self._model.cameraOrientation))
            else:
                self._view.cameraRollDoubleSpinBox.setEnabled(True)
                self._view.cameraRollDoubleSpinBox.setValue(self._model.cameraRoll)

    def __onBracketingNbPictsSpinBoxValueChanged(self, value):
        """ Bracketing nb picts spin box has change.

        Enable/disable bracketing intent combobox.
        """
        Logger().debug("ConfigController.__onBracketingNbPictsSpinBoxValueChanged(): value=%d" % value)
        self._view.bracketingIntentComboBox.setEnabled(value != 1)

    def __onLensTypeComboBoxCurrentIndexChanged(self, index):
        """ Lens type combobox has changed.

        Enable/disable focal lens entry.
        """
        type_ = config.LENS_TYPE_INDEX[index]
        Logger().debug("ConfigController.__onLensTypeComboBoxCurrentIndexChanged(): type=%s" % type_)
        if type_ == 'fisheye' and self._model.mode == 'mosaic':
            dialog = WarningMessageDialog(self.tr("Wrong value for lens type"),
                                          self.tr("Can't set lens type to 'fisheye' while in 'mosaic' mode"))
            dialog.exec_()
            self._view.lensTypeComboBox.setCurrentIndex(self._view.lensTypeComboBox.findText('rectilinear'))
        else:
            if type_ == 'rectilinear':
                self._view.focalLabel.setEnabled(True)
                self._view.focalDoubleSpinBox.setEnabled(True)
                self._view.opticalMultiplierLabel.setEnabled(True)
                self._view.opticalMultiplierDoubleSpinBox.setEnabled(True)
            else:
                self._view.focalLabel.setEnabled(False)
                self._view.focalDoubleSpinBox.setEnabled(False)
                self._view.opticalMultiplierLabel.setEnabled(False)
                self._view.opticalMultiplierDoubleSpinBox.setEnabled(False)
            Logger().debug("ConfigController.__onLensTypeComboBoxCurrentIndexChanged(): lens type set to '%s'" % type_)

    def __onDriverComboBoxCurrentIndexChanged(self, index):
        """ Driver combobox has changed.

        Enable/disable BT address / serial port.
        """
        driver = config.DRIVER_INDEX[index]
        Logger().debug("ConfigController.__onDriverComboBoxCurrentIndexChanged(): driver=%s" % driver)
        if driver == 'bluetooth':
            self._view.bluetoothDeviceAddressLabel.setEnabled(True)
            self._view.bluetoothDeviceAddressLineEdit.setEnabled(True)
            self._view.bluetoothChoosePushButton.setEnabled(True)
            self._view.serialPortLabel.setEnabled(False)
            self._view.serialPortLineEdit.setEnabled(False)
            self._view.ethernetHostPortLabel.setEnabled(False)
            self._view.ethernetHostLineEdit.setEnabled(False)
            self._view.ethernetPortSpinBox.setEnabled(False)
        elif driver == 'serial':
            self._view.bluetoothDeviceAddressLabel.setEnabled(False)
            self._view.bluetoothDeviceAddressLineEdit.setEnabled(False)
            self._view.bluetoothChoosePushButton.setEnabled(False)
            self._view.serialPortLabel.setEnabled(True)
            self._view.serialPortLineEdit.setEnabled(True)
            self._view.ethernetHostPortLabel.setEnabled(False)
            self._view.ethernetHostLineEdit.setEnabled(False)
            self._view.ethernetPortSpinBox.setEnabled(False)
        elif driver == 'ethernet':
            self._view.bluetoothDeviceAddressLabel.setEnabled(False)
            self._view.bluetoothDeviceAddressLineEdit.setEnabled(False)
            self._view.bluetoothChoosePushButton.setEnabled(False)
            self._view.serialPortLabel.setEnabled(False)
            self._view.serialPortLineEdit.setEnabled(False)
            self._view.ethernetHostPortLabel.setEnabled(True)
            self._view.ethernetHostLineEdit.setEnabled(True)
            self._view.ethernetPortSpinBox.setEnabled(True)

    def __onBluetoothChoosePushButtonClicked(self):
        """ Choose bluetooth button clicked.

        Open the bluetooth chooser dialog.
        """
        Logger().trace("ConfigController.__onBluetoothChoosePushButtonClicked()")
        controller = BluetoothChooserController(self, self._model)
        controller.show()
        controller.refreshBluetoothList()
        response = controller.exec_()
        if response:
            address, name = controller.getSelectedBluetoothAddress()
            Logger().debug("ConfigController.__onChooseBluetoothButtonClicked(): address=%s, name=%s" % (address, name))
            self._view.bluetoothDeviceAddressLineEdit.setText(address)
        controller.shutdown()

    def __onDataStorageDirPushButtonClicked(self):
        """ Select data storage dir button clicked.

        Open a file dialog to select the dir.
        """
        Logger().trace("ConfigController.__onDataStorageDirPushButtonClicked()")
        dataStorageDir = ConfigManager().get('Preferences', 'DATA_STORAGE_DIR')
        dirName = QtGui.QFileDialog.getExistingDirectory(self._view,
                                                         self.tr("Choose Data Storage dir"),
                                                         dataStorageDir,
                                                         QtGui.QFileDialog.ShowDirsOnly)
        if dirName:
            self._view.dataStorageDirLineEdit.setText(dirName)

    # Interface
    def selectTab(self, tabIndex, disable=False):
        """ Select the specified tab.

        @param tabIndex: page num
        @type tabIndex: int

        @param disable: if True, disable all other pages
        @type disable: bool
        """
        self._view.tabWidget.setCurrentIndex(tabIndex)
        for index in xrange(self._view.tabWidget.count()):
            self._view.tabWidget.setTabEnabled(index, tabIndex == index)

    def refreshView(self):

        # Shooting tab
        self._view.headOrientationComboBox.setCurrentIndex(config.HEAD_ORIENTATION_INDEX[self._model.headOrientation])
        self._view.cameraOrientationComboBox.setCurrentIndex(config.CAMERA_ORIENTATION_INDEX[self._model.cameraOrientation])
        self._view.stabilizationDelayDoubleSpinBox.setValue(self._model.stabilizationDelay)

        # Mosaic tab
        self._view.overlapSpinBox.setValue(int(100 * self._model.mosaic.overlap))
        self._view.startFromComboBox.setCurrentIndex(config.MOSAIC_START_FROM_INDEX[self._model.mosaic.startFrom])
        self._view.initialDirectionComboBox.setCurrentIndex(config.MOSAIC_INITIAL_DIR_INDEX[self._model.mosaic.initialDirection])
        self._view.crCheckBox.setChecked(self._model.mosaic.cr)

        # Camera tab
        self._view.timeValueDoubleSpinBox.setValue(self._model.camera.timeValue)
        self._view.mirrorLockupCheckBox.setChecked(self._model.camera.mirrorLockup)
        self._view.pulseWidthHighSpinBox.setValue(self._model.camera.pulseWidthHigh)
        self._view.pulseWidthLowSpinBox.setValue(self._model.camera.pulseWidthLow)
        self._view.bracketingNbPictsSpinBox.setValue(self._model.camera.bracketingNbPicts)
        self._view.bracketingIntentComboBox.setCurrentIndex(config.CAMERA_BRACKETING_INTENT_INDEX[self._model.camera.bracketingIntent])
        self._view.bracketingIntentComboBox.setEnabled(self._model.camera.bracketingNbPicts != 1)
        self._view.sensorCoefDoubleSpinBox.setValue(self._model.camera.sensorCoef)
        self._view.sensorRatioComboBox.setCurrentIndex(config.SENSOR_RATIO_INDEX[self._model.camera.sensorRatio])
        self._view.sensorResolutionDoubleSpinBox.setValue(self._model.camera.sensorResolution)

        # Lens tab
        self._view.lensTypeComboBox.setCurrentIndex(config.LENS_TYPE_INDEX[self._model.camera.lens.type_])
        self._view.focalDoubleSpinBox.setValue(self._model.camera.lens.focal)
        self._view.opticalMultiplierDoubleSpinBox.setValue(self._model.camera.lens.opticalMultiplier)

        # Hardware tab
        driverIndex = config.DRIVER_INDEX[ConfigManager().get('Preferences', 'HARDWARE_DRIVER')]
        self._view.driverComboBox.setCurrentIndex(driverIndex)
        self._view.bluetoothDeviceAddressLineEdit.setText(ConfigManager().get('Preferences', 'HARDWARE_BLUETOOTH_DEVICE_ADDRESS'))
        self._view.serialPortLineEdit.setText(ConfigManager().get('Preferences', 'HARDWARE_SERIAL_PORT'))
        self._view.ethernetHostLineEdit.setText(ConfigManager().get('Preferences', 'HARDWARE_ETHERNET_HOST'))
        self._view.ethernetPortSpinBox.setValue(ConfigManager().getInt('Preferences', 'HARDWARE_ETHERNET_PORT'))
        self._view.hardwareAutoConnectCheckBox.setChecked(ConfigManager().getBoolean('Preferences', 'HARDWARE_AUTO_CONNECT'))

        # Data tab
        dataStorageDir = ConfigManager().get('Preferences', 'DATA_STORAGE_DIR')
        if not dataStorageDir:
            dataStorageDir = config.DATA_STORAGE_DIR
        self._view.dataStorageDirLineEdit.setText(dataStorageDir)
        self._view.dataFileFormatLineEdit.setText(ConfigManager().get('Preferences', 'DATA_FILE_FORMAT'))
        self._view.dataFileEnableCheckBox.setChecked(ConfigManager().getBoolean('Preferences', 'DATA_FILE_ENABLE'))
        self._view.dataTitleLineEdit.setText(ConfigManager().get('Preferences', 'DATA_TITLE'))
        self._view.dataGpsLineEdit.setText(ConfigManager().get('Preferences', 'DATA_GPS'))
        self._view.dataCommentLineEdit.setText(ConfigManager().get('Preferences', 'DATA_COMMENT'))

        # Timer tab
        time_ = QtCore.QTime.fromString(QtCore.QString(sToHmsAsStr(self._model.timerAfter)), "hh:mm:ss")
        self._view.timerAfterTimeEdit.setTime(time_)
        self._view.timerAfterEnableCheckBox.setChecked(self._model.timerAfterEnable)
        self._view.timerRepeatSpinBox.setValue(self._model.timerRepeat)
        self._view.timerRepeatEnableCheckBox.setChecked(self._model.timerRepeatEnable)
        time_ = QtCore.QTime.fromString(QtCore.QString(sToHmsAsStr(self._model.timerEvery)), "hh:mm:ss")
        self._view.timerEveryTimeEdit.setTime(time_)

        # Misc tab
        loggerIndex = config.LOGGER_INDEX[ConfigManager().get('Preferences', 'LOGGER_LEVEL')]
        self._view.loggerLevelComboBox.setCurrentIndex(loggerIndex)

    def getSelectedTab(self):
        """ Return the selected tab.
        """
        return self._view.tabWidget.currentIndex()

    def setSelectedTab(self, index):
        """ Set the tab to be selected.
        """
        self._view.tabWidget.setCurrentIndex(index)
