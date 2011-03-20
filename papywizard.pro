# Project file
#
# $Id$

# Forms
FORMS += papywizard/view/ui/bluetoothChooserDialog.ui \
         papywizard/view/ui/configDialog.ui \
         papywizard/view/ui/counterDialog.ui \
         papywizard/view/ui/helpAboutDialog.ui \
         papywizard/view/ui/loggerDialog.ui \
         papywizard/view/ui/mainWindow.ui \
         papywizard/view/ui/nbPictsDialog.ui \
         papywizard/view/ui/pluginsConfigDialog.ui \
         papywizard/view/ui/pluginsDialog.ui \
         papywizard/view/ui/pluginsStatusDialog.ui \
         papywizard/view/ui/shootDialog.ui \
         papywizard/view/ui/totalFovDialog.ui

# common
SOURCES += papywizard/common/configManager.py \
           papywizard/common/config.py \
           papywizard/common/exception.py \
           papywizard/common/helpers.py \
;            papywizard/common/i18n.py \
           papywizard/common/loggingFormatter.py \
           papywizard/common/loggingServices.py \
           papywizard/common/orderedDict.py \
;            papywizard/common/pixmaps.py \
           papywizard/common/presetManager.py \
           papywizard/common/publisher.py \
           papywizard/common/qLoggingFormatter.py \
           papywizard/common/signal.py

# controller
SOURCES += papywizard/controller/abstractController.py \
           papywizard/controller/bluetoothChooserController.py \
           papywizard/controller/configController.py \
           papywizard/controller/counterController.py \
           papywizard/controller/helpAboutController.py \
           papywizard/controller/loggerController.py \
           papywizard/controller/mainController.py \
           papywizard/controller/nbPictsController.py \
           papywizard/controller/pluginsController.py \
           papywizard/controller/pluginsStatusController.py \
           papywizard/controller/shootController.py \
           papywizard/controller/spy.py \
           papywizard/controller/totalFovController.py

# driver
SOURCES += papywizard/driver/abstractDriver.py \
           papywizard/driver/bluetoothDriver.py \
           papywizard/driver/bluetoothTransport.py \
           papywizard/driver/driverFactory.py \
           papywizard/driver/ethernetDriver.py \
           papywizard/driver/serialDriver.py \
           papywizard/driver/usbDriver.py

# hardware
SOURCES += papywizard/hardware/abstractHardware.py \
           papywizard/hardware/claussHardware.py \
           papywizard/hardware/gigaPanBotHardware.py \
           papywizard/hardware/merlinOrionHardware.py \
           papywizard/hardware/pixOrbHardware.py \
           papywizard/hardware/pololuServoHardware.py \
           papywizard/hardware/ursaMinorUsbHardware.py

# model
SOURCES += papywizard/model/camera.py \
           papywizard/model/data.py \
           papywizard/model/head.py \
           papywizard/model/lens.py \
           papywizard/model/scan.py \
           papywizard/model/shooting.py

# Plugins
SOURCES += papywizard/plugins/abstractAxisPlugin.py \
           papywizard/plugins/abstractHardwarePlugin.py \
           papywizard/plugins/abstractPluginController.py \
           papywizard/plugins/abstractPlugin.py \
           papywizard/plugins/abstractShutterPlugin.py \
           papywizard/plugins/axisPluginController.py \
           papywizard/plugins/claussPlugins.py \
           papywizard/plugins/dslrRemoteProPlugins.py \
           papywizard/plugins/eosUtilityPlugins.py \
           papywizard/plugins/genericTetheredPlugins.py \
           papywizard/plugins/gigaPanBotPlugins.py \
           papywizard/plugins/gphotoBracketPlugins.py \
           papywizard/plugins/hardwarePluginController.py \
           papywizard/plugins/merlinOrionPlugins.py \
           papywizard/plugins/nkRemotePlugins.py \
           papywizard/plugins/panoduinoPlugins.py \
           papywizard/plugins/pixOrbPlugins.py \
           papywizard/plugins/pluginsConnector.py \
           papywizard/plugins/pluginsManager.py \
           papywizard/plugins/shutterPluginController.py \
           papywizard/plugins/shutterPlugin.py \
           papywizard/plugins/simulationPlugins.py \
           papywizard/plugins/timelordPlugins.py \
           papywizard/plugins/ursaMinorBt2Plugins.py \
           papywizard/plugins/ursaMinorUsbPlugins.py

# scripts
SOURCES += papywizard/scripts/main.py \
           papywizard/scripts/simulator.py

# simulator
SOURCES += papywizard/simulator/gigaPanBotCommandDispatcher.py \
           papywizard/simulator/gigaPanBotSimulator.py \
           papywizard/simulator/merlinOrionCommandDispatcher.py \
           papywizard/simulator/merlinOrionSimulator.py \
           papywizard/simulator/pixOrbCommandDispatcher.py \
           papywizard/simulator/pixOrbSimulator.py

# View
SOURCES += papywizard/view/icons.py \
           papywizard/view/logBuffer.py \
           papywizard/view/messageDialog.py \
           papywizard/view/pictureItem.py \
           papywizard/view/pluginFields.py \
           papywizard/view/shootingScene.py

# i18n
TRANSLATIONS += papywizard/common/i18n/papywizard_en.ts \
                papywizard/common/i18n/papywizard_fr.ts \
                papywizard/common/i18n/papywizard_pl.ts \
                papywizard/common/i18n/papywizard_de.ts \
                papywizard/common/i18n/papywizard_it.ts \
                papywizard/common/i18n/papywizard_es.ts \
                papywizard/common/i18n/papywizard_cs.ts
