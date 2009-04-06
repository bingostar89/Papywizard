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
from papywizard.view.messageDialog import WarningMessageDialog


class ConfigController(AbstractModalDialogController):
    """ Configuration controller object.
    """
    def _init(self):
        self._uiFile = "configDialog.ui"

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        AbstractModalDialogController._retreiveWidgets(self)

    def _initWidgets(self):
        pass

    def _connectSignals(self):
        AbstractModalDialogController._connectSignals(self)

        self.connect(self._view.cameraOrientationComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onCameraOrientationComboBoxCurrentIndexChanged)
        self.connect(self._view.lensTypeComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onLensTypeComboBoxCurrentIndexChanged)
        self.connect(self._view.dataStorageDirPushButton, QtCore.SIGNAL("clicked()"), self.__onDataStorageDirPushButtonClicked)

    def _disconnectSignals(self):
        AbstractModalDialogController._disconnectSignals(self)

        self.disconnect(self._view.cameraOrientationComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onCameraOrientationComboBoxCurrentIndexChanged)
        self.disconnect(self._view.lensTypeComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.__onLensTypeComboBoxCurrentIndexChanged)
        self.disconnect(self._view.dataStorageDirPushButton, QtCore.SIGNAL("clicked()"), self.__onDataStorageDirPushButtonClicked)

    # Callbacks
    def _onAccepted(self):
        """ Ok button has been clicked.

        Save back values to model.
        """
        Logger().trace("ConfigController._onAccepted()")

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

        # Camera/lens tab
        self._model.camera.sensorCoef = self._view.sensorCoefDoubleSpinBox.value()
        self._model.camera.sensorRatio = config.SENSOR_RATIO_INDEX[self._view.sensorRatioComboBox.currentIndex()]
        self._model.camera.sensorResolution = self._view.sensorResolutionDoubleSpinBox.value()
        self._model.camera.lens.type_ = config.LENS_TYPE_INDEX[self._view.lensTypeComboBox.currentIndex()]
        self._model.camera.lens.focal = self._view.focalDoubleSpinBox.value()
        self._model.camera.lens.opticalMultiplier = self._view.opticalMultiplierDoubleSpinBox.value()

        # Data tab
        ConfigManager().set('Core/DATA_STORAGE_DIR', unicode(self._view.dataStorageDirLineEdit.text()))
        ConfigManager().set('Core/DATA_FILE_FORMAT', unicode(self._view.dataFileFormatLineEdit.text()))
        ConfigManager().setBoolean('Core/DATA_FILE_ENABLE', bool(self._view.dataFileEnableCheckBox.isChecked()))
        ConfigManager().set('Core/DATA_TITLE', unicode(self._view.dataTitleLineEdit.text()))
        ConfigManager().set('Core/DATA_GPS',  unicode(self._view.dataGpsLineEdit.text()))
        ConfigManager().set('Core/DATA_COMMENT',  unicode(self._view.dataCommentLineEdit.text()))

        # Timer tab
        time_ = self._view.timerAfterTimeEdit.time()
        self._model.timerAfter = hmsAsStrToS(time_.toString("hh:mm:ss"))
        self._model.timerAfterEnable = self._view.timerAfterEnableCheckBox.isChecked()
        self._model.timerRepeat = self._view.timerRepeatSpinBox.value()
        self._model.timerRepeatEnable = self._view.timerRepeatEnableCheckBox.isChecked()
        time_ = self._view.timerEveryTimeEdit.time()
        self._model.timerEvery = hmsAsStrToS(time_.toString("hh:mm:ss"))

        # Misc tab
        ConfigManager().set('Core/LOGGER_LEVEL', config.LOGGER_INDEX[self._view.loggerLevelComboBox.currentIndex()])

        ConfigManager().save()

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
                self._view.focalDoubleSpinBox.setEnabled(True)
                self._view.opticalMultiplierLabel.setEnabled(True)
                self._view.opticalMultiplierDoubleSpinBox.setEnabled(True)
            else:
                self._view.focalDoubleSpinBox.setEnabled(False)
                self._view.opticalMultiplierLabel.setEnabled(False)
                self._view.opticalMultiplierDoubleSpinBox.setEnabled(False)
            Logger().debug("ConfigController.__onLensTypeComboBoxCurrentIndexChanged(): lens type set to '%s'" % type_)

    def __onDataStorageDirPushButtonClicked(self):
        """ Select data storage dir button clicked.

        Open a file dialog to select the dir.
        """
        Logger().trace("ConfigController.__onDataStorageDirPushButtonClicked()")
        dataStorageDir = ConfigManager().get('Core/DATA_STORAGE_DIR')
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

        # Camera/lens tab
        self._view.sensorCoefDoubleSpinBox.setValue(self._model.camera.sensorCoef)
        self._view.sensorRatioComboBox.setCurrentIndex(config.SENSOR_RATIO_INDEX[self._model.camera.sensorRatio])
        self._view.sensorResolutionDoubleSpinBox.setValue(self._model.camera.sensorResolution)
        self._view.lensTypeComboBox.setCurrentIndex(config.LENS_TYPE_INDEX[self._model.camera.lens.type_])
        self._view.focalDoubleSpinBox.setValue(self._model.camera.lens.focal)
        self._view.opticalMultiplierDoubleSpinBox.setValue(self._model.camera.lens.opticalMultiplier)

        # Data tab
        dataStorageDir = ConfigManager().get('Core/DATA_STORAGE_DIR')
        if not dataStorageDir:
            dataStorageDir = config.DATA_STORAGE_DIR
        self._view.dataStorageDirLineEdit.setText(dataStorageDir)
        self._view.dataFileFormatLineEdit.setText(ConfigManager().get('Core/DATA_FILE_FORMAT'))
        self._view.dataFileEnableCheckBox.setChecked(ConfigManager().getBoolean('Core/DATA_FILE_ENABLE'))
        dataTitle = ConfigManager().get('Core/DATA_TITLE')
        if not dataTitle:
            dataTitle = self.tr("Here goes the title")
        self._view.dataTitleLineEdit.setText(dataTitle)
        dataGps = ConfigManager().get('Core/DATA_GPS')
        if not dataGps:
            dataGps = self.tr("Here goes the location")
        self._view.dataGpsLineEdit.setText(dataGps)
        dataComment = ConfigManager().get('Core/DATA_COMMENT')
        if not dataComment:
            dataComment = self.tr("Generated by Papywizard %(version)s")
        self._view.dataCommentLineEdit.setText(dataComment)

        # Timer tab
        time_ = QtCore.QTime.fromString(QtCore.QString(sToHmsAsStr(self._model.timerAfter)), "hh:mm:ss")
        self._view.timerAfterTimeEdit.setTime(time_)
        self._view.timerAfterEnableCheckBox.setChecked(self._model.timerAfterEnable)
        self._view.timerRepeatSpinBox.setValue(self._model.timerRepeat)
        self._view.timerRepeatEnableCheckBox.setChecked(self._model.timerRepeatEnable)
        time_ = QtCore.QTime.fromString(QtCore.QString(sToHmsAsStr(self._model.timerEvery)), "hh:mm:ss")
        self._view.timerEveryTimeEdit.setTime(time_)

        # Misc tab
        loggerIndex = config.LOGGER_INDEX[ConfigManager().get('Core/LOGGER_LEVEL')]
        self._view.loggerLevelComboBox.setCurrentIndex(loggerIndex)

    def getSelectedTab(self):
        """ Return the selected tab.
        """
        return self._view.tabWidget.currentIndex()

    def setSelectedTab(self, index):
        """ Set the tab to be selected.
        """
        self._view.tabWidget.setCurrentIndex(index)
