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

- PreferencesController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: configController.py 1645 2009-03-29 21:44:05Z fma $"

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.pluginManager import PluginManager
from papywizard.controller.abstractController import AbstractModalDialogController
from papywizard.controller.bluetoothChooserController import BluetoothChooserController
from papywizard.view.messageDialog import WarningMessageDialog


class PreferencesController(AbstractModalDialogController):
    """ Hardware preferences controller object.
    """
    def _init(self):
        self._uiFile = "preferencesDialog.ui"

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        AbstractModalDialogController._retreiveWidgets(self)

    def _initWidgets(self):
        pass

    def _connectSignals(self):
        AbstractModalDialogController._connectSignals(self)

        self.connect(self._view.bluetoothChoosePushButton, QtCore.SIGNAL("clicked()"), self.__onBluetoothChoosePushButtonClicked)
        self.connect(self._view.yawAxisConfigurePushButton, QtCore.SIGNAL("clicked()"), self.__onYawAxisConfigurePushButtonClicked)
        self.connect(self._view.pitchAxisConfigurePushButton, QtCore.SIGNAL("clicked()"), self.__onPitchAxisConfigurePushButtonClicked)
        self.connect(self._view.shutterConfigurePushButton, QtCore.SIGNAL("clicked()"), self.__onShutterConfigurePushButtonClicked)

    def _disconnectSignals(self):
        AbstractModalDialogController._disconnectSignals(self)

        self.disconnect(self._view.bluetoothChoosePushButton, QtCore.SIGNAL("clicked()"), self.__onBluetoothChoosePushButtonClicked)
        self.disconnect(self._view.yawAxisConfigurePushButton, QtCore.SIGNAL("clicked()"), self.__onYawAxisConfigurePushButtonClicked)
        self.disconnect(self._view.pitchAxisConfigurePushButton, QtCore.SIGNAL("clicked()"), self.__onPitchAxisConfigurePushButtonClicked)
        self.disconnect(self._view.shutterConfigurePushButton, QtCore.SIGNAL("clicked()"), self.__onShutterConfigurePushButtonClicked)

    # Callbacks
    def _onAccepted(self):
        """ Ok button has been clicked.

        Save back values to model.
        """
        Logger().trace("ConfigController._onAccepted()")

        # Plugins tab
        previousPlugin = ConfigManager().get('Core/PLUGIN_YAW_AXIS')
        ConfigManager().set('Core/PLUGIN_YAW_AXIS', unicode(self._view.yawAxisComboBox.currentText()))
        newPlugin = ConfigManager().get('Core/PLUGIN_YAW_AXIS')
        if previousPlugin != newPlugin:
            PluginManager().get('yawAxis', previousPlugin)[0].shutdown()
            PluginManager().get('yawAxis', newPlugin)[0].activate()

        previousPlugin = ConfigManager().get('Core/PLUGIN_PITCH_AXIS')
        ConfigManager().set('Core/PLUGIN_PITCH_AXIS', unicode(self._view.pitchAxisComboBox.currentText()))
        newPlugin = ConfigManager().get('Core/PLUGIN_PITCH_AXIS')
        if previousPlugin != newPlugin:
            PluginManager().get('pitchAxis', previousPlugin)[0].shutdown()
            PluginManager().get('pitchAxis', newPlugin)[0].activate()

        previousPlugin = ConfigManager().get('Core/PLUGIN_SHUTTER')
        ConfigManager().set('Core/PLUGIN_SHUTTER', unicode(self._view.shutterComboBox.currentText()))
        newPlugin = ConfigManager().get('Core/PLUGIN_SHUTTER')
        if previousPlugin != newPlugin:
            PluginManager().get('shutter', previousPlugin)[0].shutdown()
            PluginManager().get('shutter', newPlugin)[0].activate()

        # Drivers tab
        ConfigManager().set('Core/HARDWARE_BLUETOOTH_DEVICE_ADDRESS', unicode(self._view.bluetoothDeviceAddressLineEdit.text()))
        ConfigManager().set('Core/HARDWARE_SERIAL_PORT', unicode(self._view.serialPortLineEdit.text()))
        ConfigManager().set('Core/HARDWARE_ETHERNET_HOST', unicode(self._view.ethernetHostLineEdit.text()))
        ConfigManager().setInt('Core/HARDWARE_ETHERNET_PORT', self._view.ethernetPortSpinBox.value())
        ConfigManager().setBoolean('Core/HARDWARE_AUTO_CONNECT', self._view.hardwareAutoConnectCheckBox.isChecked())

        ConfigManager().save()

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

    def __onYawAxisConfigurePushButtonClicked(self):
        """ Yaw axis configure button clicked.
        """
        Logger().trace("ConfigController.__onYawAxisConfigurePushButtonClicked()")
        name = self._view.yawAxisComboBox.currentText()
        model, controllerClass = PluginManager().get('yawAxis', name)
        controller = controllerClass(self, model)
        controller.exec_()

    def __onPitchAxisConfigurePushButtonClicked(self):
        """ Yaw axis configure button clicked.
        """
        Logger().trace("ConfigController.__onPitchAxisConfigurePushButtonClicked()")
        name = self._view.pitchAxisComboBox.currentText()
        model, controllerClass = PluginManager().get('pitchAxis', name)
        controller = controllerClass(self, model)
        controller.exec_()

    def __onShutterConfigurePushButtonClicked(self):
        """ Yaw axis configure button clicked.
        """
        Logger().trace("ConfigController.__onShutterConfigurePushButtonClicked()")
        name = self._view.shutterComboBox.currentText()
        model, controllerClass = PluginManager().get('shutter', name)
        controller = controllerClass(self, model)
        controller.exec_()

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

        # Plugins tab
        yawAxisPlugins = PluginManager().getList('yawAxis')
        if yawAxisPlugins:
            for model, controller in yawAxisPlugins:
                self._view.yawAxisComboBox.addItem(model.name)
            selectedPlugin = ConfigManager().get('Core/PLUGIN_YAW_AXIS')
            self._view.yawAxisComboBox.setCurrentIndex(self._view.yawAxisComboBox.findText(selectedPlugin))
        pitchAxisPlugins = PluginManager().getList('pitchAxis')
        if pitchAxisPlugins:
            for model, controller in pitchAxisPlugins:
                self._view.pitchAxisComboBox.addItem(model.name)
            selectedPlugin = ConfigManager().get('Core/PLUGIN_PITCH_AXIS')
            self._view.pitchAxisComboBox.setCurrentIndex(self._view.pitchAxisComboBox.findText(selectedPlugin))
        shutterPlugins = PluginManager().getList('shutter')
        if shutterPlugins:
            for model, controller in shutterPlugins:
                self._view.shutterComboBox.addItem(model.name)
            selectedPlugin = ConfigManager().get('Core/PLUGIN_SHUTTER')
            self._view.shutterComboBox.setCurrentIndex(self._view.shutterComboBox.findText(selectedPlugin))

        # Drivers tab
        self._view.bluetoothDeviceAddressLineEdit.setText(ConfigManager().get('Core/HARDWARE_BLUETOOTH_DEVICE_ADDRESS'))
        self._view.serialPortLineEdit.setText(ConfigManager().get('Core/HARDWARE_SERIAL_PORT'))
        self._view.ethernetHostLineEdit.setText(ConfigManager().get('Core/HARDWARE_ETHERNET_HOST'))
        self._view.ethernetPortSpinBox.setValue(ConfigManager().getInt('Core/HARDWARE_ETHERNET_PORT'))
        self._view.hardwareAutoConnectCheckBox.setChecked(ConfigManager().getBoolean('Core/HARDWARE_AUTO_CONNECT'))

    def getSelectedTab(self):
        """ Return the selected tab.
        """
        return self._view.tabWidget.currentIndex()

    def setSelectedTab(self, index):
        """ Set the tab to be selected.
        """
        self._view.tabWidget.setCurrentIndex(index)
