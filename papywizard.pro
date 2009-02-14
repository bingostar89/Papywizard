# Project file
#
# $Id$

# Forms
FORMS += papywizard/view/bluetoothChooserDialog.ui \
         papywizard/view/configDialog.ui \
         papywizard/view/helpAboutDialog.ui \
         papywizard/view/loggerDialog.ui \
         papywizard/view/mainWindow.ui \
         papywizard/view/nbPictsDialog.ui \
         papywizard/view/shootDialog.ui \
         papywizard/view/totalFovDialog.ui

# Common
SOURCES += papywizard/common/configManager.py \
           papywizard/common/config.py \
           papywizard/common/exception.py \
           papywizard/common/helpers.py \
           papywizard/common/loggingFormatter.py \
           papywizard/common/loggingServices.py \
           papywizard/common/orderedDict.py \
           papywizard/common/presetManager.py \
           papywizard/common/publisher.py \
           papywizard/common/qLoggingFormatter.py \
           papywizard/common/signal.py

# Controllers
SOURCES += papywizard/controller/abstractController.py \
           papywizard/controller/bluetoothChooserController.py \
           papywizard/controller/configController.py \
           papywizard/controller/helpAboutController.py \
           papywizard/controller/loggerController.py \
           papywizard/controller/mainController.py \
           papywizard/controller/nbPictsController.py \
           papywizard/controller/shootController.py \
           papywizard/controller/spy.py \
           papywizard/controller/totalFovController.py

# Hardware
SOURCES += papywizard/hardware/axis.py \
           papywizard/hardware/bluetoothDriver.py \
           papywizard/hardware/busDriver.py \
           papywizard/hardware/driverFactory.py \
           papywizard/hardware/ethernetDriver.py \
           papywizard/hardware/hardwareFactory.py \
           papywizard/hardware/head.py \
           papywizard/hardware/serialDriver.py\
           papywizard/hardware/simulator.py \
           papywizard/hardware/usbDriver.py

# Model
SOURCES += papywizard/model/camera.py \
           papywizard/model/data.py \
           papywizard/model/lens.py \
           papywizard/model/scan.py \
           papywizard/model/shooting.py

# Scripts
SOURCES += papywizard/scripts/main3D.py \
           papywizard/scripts/main.py \
           papywizard/scripts/mainSimul.py

# View 3D
           papywizard/view3D/povexport.py \
           papywizard/view3D/view3D.py

# Views
           papywizard/view/icons.py \
           papywizard/view/logBuffer.py \
           papywizard/view/messageDialog.py \
           papywizard/view/pictureItem.py \
           papywizard/view/shootingScene.py

# i18n
TRANSLATIONS += papywizard/common/i18n/papywizard_en.ts \
                papywizard/common/i18n/papywizard_fr.ts \
                papywizard/common/i18n/papywizard_pl.ts \
                papywizard/common/i18n/papywizard_de.ts \
                papywizard/common/i18n/papywizard_it.ts \
                papywizard/common/i18n/papywizard_es.ts
