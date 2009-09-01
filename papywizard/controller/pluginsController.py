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

@todo: check what type(s) of driver(s) a plugin can use
"""

__revision__ = "$Id$"

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.hardware.bluetoothTransport import BluetoothTransport
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.controller.abstractController import AbstractModalDialogController
from papywizard.controller.bluetoothChooserController import BluetoothChooserController
from papywizard.view.messageDialog import WarningMessageDialog, ExceptionMessageDialog


class PluginsController(AbstractModalDialogController):
    """ Plugins controller object.
    """
    def _init(self):
        self._uiFile = "pluginsDialog.ui"

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        AbstractModalDialogController._retreiveWidgets(self)

    def _initWidgets(self):
        pass

    def _connectSignals(self):
        AbstractModalDialogController._connectSignals(self)
        self.connect(self._view.yawAxisComboBox, QtCore.SIGNAL("activated(const QString&)"), self.__onYawAxisComboBoxActivated)
        self.connect(self._view.pitchAxisComboBox, QtCore.SIGNAL("activated(const QString&)"), self.__onPitchAxisComboBoxActivated)
        self.connect(self._view.shutterComboBox, QtCore.SIGNAL("activated(const QString&)"), self.__onShutterComboBoxActivated)
        self.connect(self._view.bluetoothChoosePushButton, QtCore.SIGNAL("clicked()"), self.__onBluetoothChoosePushButtonClicked)

    def _disconnectSignals(self):
        AbstractModalDialogController._disconnectSignals(self)
        self.disconnect(self._view.yawAxisComboBox, QtCore.SIGNAL("activated(const QString&)"), self.__onYawAxisComboBoxActivated)
        self.disconnect(self._view.pitchAxisComboBox, QtCore.SIGNAL("activated(const QString&)"), self.__onPitchAxisComboBoxActivated)
        self.disconnect(self._view.shutterComboBox, QtCore.SIGNAL("activated(const QString&)"), self.__onShutterComboBoxActivated)
        self.disconnect(self._view.bluetoothChoosePushButton, QtCore.SIGNAL("clicked()"), self.__onBluetoothChoosePushButtonClicked)

    # Callbacks
    def _onAccepted(self):
        """ Ok button has been clicked.

        Save back values to model.
        """
        Logger().trace("PluginsController._onAccepted()")

        # Plugins tab
        previousPluginName = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        ConfigManager().set('Plugins/PLUGIN_YAW_AXIS', unicode(self._view.yawAxisComboBox.currentText()))
        newPluginName = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        newPlugin = PluginsManager ().get('yawAxis', newPluginName)[0]
        if previousPluginName != newPluginName:
            previousPlugin = PluginsManager ().get('yawAxis', previousPluginName)[0]
            previousPlugin.deactivate()
            newPlugin.activate()
        if hasattr(newPlugin, '_driver'):
            newPlugin._config['DRIVER_TYPE'] = unicode(self._view.yawAxisDriverComboBox.currentText())
        # todo: set config in a callback
        newPlugin._saveConfig()

        previousPluginName = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        ConfigManager().set('Plugins/PLUGIN_PITCH_AXIS', unicode(self._view.pitchAxisComboBox.currentText()))
        newPluginName = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        newPlugin = PluginsManager ().get('pitchAxis', newPluginName)[0]
        if previousPluginName != newPluginName:
            previousPlugin = PluginsManager ().get('pitchAxis', previousPluginName)[0]
            previousPlugin.deactivate()
            newPlugin.activate()
        if hasattr(newPlugin, '_driver'):
            newPlugin._config['DRIVER_TYPE'] = unicode(self._view.pitchAxisDriverComboBox.currentText())
        # todo: set config in a callback
        newPlugin._saveConfig()

        previousPluginName = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
        ConfigManager().set('Plugins/PLUGIN_SHUTTER', unicode(self._view.shutterComboBox.currentText()))
        newPluginName = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
        newPlugin = PluginsManager ().get('shutter', newPluginName)[0]
        if previousPluginName != newPluginName:
            previousPlugin = PluginsManager ().get('shutter', previousPluginName)[0]
            previousPlugin.deactivate()
            newPlugin.activate()
        if hasattr(newPlugin, '_driver'):
            newPlugin._config['DRIVER_TYPE'] = unicode(self._view.shutterDriverComboBox.currentText())
        # todo: set config in a callback
        newPlugin._saveConfig()

        # Drivers tab
        ConfigManager().set('Plugins/HARDWARE_BLUETOOTH_DEVICE_ADDRESS', unicode(self._view.bluetoothDeviceAddressLineEdit.text()))
        ConfigManager().set('Plugins/HARDWARE_SERIAL_PORT', unicode(self._view.serialPortLineEdit.text()))
        ConfigManager().set('Plugins/HARDWARE_ETHERNET_HOST', unicode(self._view.ethernetHostLineEdit.text()))
        ConfigManager().setInt('Plugins/HARDWARE_ETHERNET_PORT', self._view.ethernetPortSpinBox.value())
        ConfigManager().save()

    def __onYawAxisComboBoxActivated(self, pluginName):
        """ Yaw axis combo box.
        """
        Logger().debug("PluginsController.__onYawAxisComboBoxActivated(): plugin=%s" % pluginName)
        model, controllerClass = PluginsManager ().get('yawAxis', pluginName)
        if hasattr(model, '_driver'):
            self._view.yawAxisDriverComboBox.setEnabled(True)
            self._view.yawAxisDriverComboBox.setCurrentIndex(self._view.yawAxisDriverComboBox.findText(model._config['DRIVER_TYPE']))
        else:
            self._view.yawAxisDriverComboBox.setEnabled(False)
            #self._view.yawAxisDriverComboBox.setCurrentIndex(-1)

    def __onPitchAxisComboBoxActivated(self, pluginName):
        """ Pitch axis combo box.
        """
        Logger().debug("PluginsController.__onPitchAxisComboBoxActivated(): plugin=%s" % pluginName)
        model, controllerClass = PluginsManager ().get('pitchAxis', pluginName)
        if hasattr(model, '_driver'):
            self._view.pitchAxisDriverComboBox.setEnabled(True)
            self._view.pitchAxisDriverComboBox.setCurrentIndex(self._view.pitchAxisDriverComboBox.findText(model._config['DRIVER_TYPE']))
        else:
            self._view.pitchAxisDriverComboBox.setEnabled(False)
            #self._view.pitchAxisDriverComboBox.setCurrentIndex(-1)

    def __onShutterComboBoxActivated(self, pluginName):
        """ Shutter combo box.
        """
        Logger().debug("PluginsController.__onShutterComboBoxActivated(): plugin=%s" % pluginName)
        model, controllerClass = PluginsManager ().get('shutter', pluginName)
        if hasattr(model, '_driver'):
            self._view.shutterDriverComboBox.setEnabled(True)
            self._view.shutterDriverComboBox.setCurrentIndex(self._view.shutterDriverComboBox.findText(model._config['DRIVER_TYPE']))
        else:
            self._view.shutterDriverComboBox.setEnabled(False)
            #self._view.shutterDriverComboBox.setCurrentIndex(-1)

    def __onBluetoothChoosePushButtonClicked(self):
        """ Choose bluetooth button clicked.

        Open the bluetooth chooser dialog.
        """
        Logger().trace("PluginsController.__onBluetoothChoosePushButtonClicked()")
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        while QtGui.QApplication.hasPendingEvents():
            QtGui.QApplication.processEvents()  #QtCore.QEventLoop.ExcludeUserInputEvents)

        bluetoothTransport = BluetoothTransport()
        try:
            bluetoothDevices = bluetoothTransport.discoverDevices()
        except Exception, msg:
            QtGui.qApp.restoreOverrideCursor()
            Logger().exception("PluginsController.__onBluetoothChoosePushButtonClicked()")
            Logger().error("Can't scan bluetooth\n%s" % unicode(msg))
            dialog = ExceptionMessageDialog(self.tr("Can't scan bluetooth"), unicode(msg))
            dialog.exec_()
        else:
            QtGui.qApp.restoreOverrideCursor()
            controller = BluetoothChooserController(self, model=bluetoothDevices)
            response = controller.exec_()
            if response:
                address, name = controller.getSelectedBluetoothAddress()
                Logger().debug("PluginsController.__onChooseBluetoothButtonClicked(): address=%s, name=%s" % (address, name))
                self._view.bluetoothDeviceAddressLineEdit.setText(address)
            controller.shutdown()

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
        yawAxisPlugins = PluginsManager ().getList('yawAxis')
        if yawAxisPlugins:
            for model, controller in yawAxisPlugins:
                self._view.yawAxisComboBox.addItem(model.name)
            selectedPluginName = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
            self._view.yawAxisComboBox.setCurrentIndex(self._view.yawAxisComboBox.findText(selectedPluginName))
            selectedPlugin = PluginsManager ().get('yawAxis', selectedPluginName)[0]
            if hasattr(selectedPlugin, '_driver'):
                self._view.yawAxisDriverComboBox.setEnabled(True)
                driverType = selectedPlugin._config['DRIVER_TYPE']
                self._view.yawAxisDriverComboBox.setCurrentIndex(self._view.yawAxisDriverComboBox.findText(driverType))
            else:
                self._view.yawAxisDriverComboBox.setEnabled(False)
                #self._view.yawAxisDriverComboBox.setCurrentIndex(-1)

        pitchAxisPlugins = PluginsManager ().getList('pitchAxis')
        if pitchAxisPlugins:
            for model, controller in pitchAxisPlugins:
                self._view.pitchAxisComboBox.addItem(model.name)
            selectedPluginName = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
            self._view.pitchAxisComboBox.setCurrentIndex(self._view.pitchAxisComboBox.findText(selectedPluginName))
            selectedPlugin = PluginsManager ().get('pitchAxis', selectedPluginName)[0]
            if hasattr(selectedPlugin, '_driver'):
                self._view.pitchAxisDriverComboBox.setEnabled(True)
                driverType = selectedPlugin._config['DRIVER_TYPE']
                self._view.pitchAxisDriverComboBox.setCurrentIndex(self._view.pitchAxisDriverComboBox.findText(driverType))
            else:
                self._view.pitchAxisDriverComboBox.setEnabled(False)
                #self._view.pitchAxisDriverComboBox.setCurrentIndex(-1)

        shutterPlugins = PluginsManager ().getList('shutter')
        if shutterPlugins:
            for model, controller in shutterPlugins:
                self._view.shutterComboBox.addItem(model.name)
            selectedPluginName = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
            self._view.shutterComboBox.setCurrentIndex(self._view.shutterComboBox.findText(selectedPluginName))
            selectedPlugin = PluginsManager ().get('shutter', selectedPluginName)[0]
            if hasattr(selectedPlugin, '_driver'):
                self._view.shutterDriverComboBox.setEnabled(True)
                driverType = selectedPlugin._config['DRIVER_TYPE']
                self._view.shutterDriverComboBox.setCurrentIndex(self._view.shutterDriverComboBox.findText(driverType))
            else:
                self._view.shutterDriverComboBox.setEnabled(False)
                #self._view.shutterDriverComboBox.setCurrentIndex(-1)

        # Drivers tab
        self._view.bluetoothDeviceAddressLineEdit.setText(ConfigManager().get('Plugins/HARDWARE_BLUETOOTH_DEVICE_ADDRESS'))
        self._view.serialPortLineEdit.setText(ConfigManager().get('Plugins/HARDWARE_SERIAL_PORT'))
        self._view.ethernetHostLineEdit.setText(ConfigManager().get('Plugins/HARDWARE_ETHERNET_HOST'))
        self._view.ethernetPortSpinBox.setValue(ConfigManager().getInt('Plugins/HARDWARE_ETHERNET_PORT'))

    def getSelectedTab(self):
        """ Return the selected tab.
        """
        return self._view.tabWidget.currentIndex()

    def setSelectedTab(self, index):
        """ Set the tab to be selected.
        """
        self._view.tabWidget.setCurrentIndex(index)
