# Project file
#
# $Id$

# Forms
FORMS += papywizard/view/ui/bluetoothChooserDialog.ui \
         papywizard/view/ui/configDialog.ui \
         papywizard/view/ui/helpAboutDialog.ui \
         papywizard/view/ui/loggerDialog.ui \
         papywizard/view/ui/mainWindow.ui \
         papywizard/view/ui/nbPictsDialog.ui \
         papywizard/view/ui/pluginsConfigDialog.ui \
         papywizard/view/ui/pluginsDialog.ui \
         papywizard/view/ui/shootDialog.ui \
         papywizard/view/ui/totalFovDialog.ui

# Common
SOURCES += papywizard/common/abstractPlugin.py \
           papywizard/common/bluetoothTransport.py \
           papywizard/common/config.py \
           papywizard/common/configManager.py \
           papywizard/common/exception.py \
           papywizard/common/helpers.py \
           papywizard/common/loggingFormatter.py \
           papywizard/common/loggingServices.py \
           papywizard/common/orderedDict.py \
           papywizard/common/pluginManager.py \
           papywizard/common/presetManager.py \
           papywizard/common/publisher.py \
           papywizard/common/qLoggingFormatter.py \
           papywizard/common/signal.py

# Controllers
SOURCES += papywizard/controller/abstractController.py \
           papywizard/controller/abstractPluginController.py \
           papywizard/controller/axisPluginController.py \
           papywizard/controller/bluetoothChooserController.py \
           papywizard/controller/configController.py \
           papywizard/controller/hardwarePluginController.py \
           papywizard/controller/helpAboutController.py \
           papywizard/controller/loggerController.py \
           papywizard/controller/mainController.py \
           papywizard/controller/nbPictsController.py \
           papywizard/controller/pluginsController.py \
           papywizard/controller/shootController.py \
           papywizard/controller/shutterPluginController.py \
           papywizard/controller/spy.py \
           papywizard/controller/totalFovController.py

# Hardware
SOURCES += papywizard/hardware/abstractAxisPlugin.py \
           papywizard/hardware/abstractDriver.py \
           papywizard/hardware/abstractShutterPlugin.py \
           papywizard/hardware/axis.py \
           papywizard/hardware/bluetoothDriver.py \
           papywizard/hardware/driverFactory.py \
           papywizard/hardware/ethernetDriver.py \
           papywizard/hardware/hardwareFactory.py \
           papywizard/hardware/hardwarePlugin.py \
           papywizard/hardware/head.py \
           papywizard/hardware/serialDriver.py \
           papywizard/hardware/simulator.py \
           papywizard/hardware/usbDriver.py

# Model
SOURCES += papywizard/model/camera.py \
           papywizard/model/data.py \
           papywizard/model/lens.py \
           papywizard/model/scan.py \
           papywizard/model/shooting.py

# Scripts
SOURCES += papywizard/scripts/main.py

# Plugins
SOURCES += papywizard/plugins/eosUtilityPlugins.py \
           papywizard/plugins/merlinOrionPlugins.py \
           papywizard/plugins/pololuServoPlugins.py \
           papywizard/plugins/simulationPlugins.py \
           papywizard/plugins/tetheredPlugins.py \
           papywizard/plugins/timelordPlugins.py

# Views
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
                papywizard/common/i18n/papywizard_es.ts

