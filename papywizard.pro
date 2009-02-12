# Project file
#
# $Id$

FORMS += papywizard/view/bluetoothChooserDialog.ui \
         papywizard/view/configDialog.ui \
         papywizard/view/helpAboutDialog.ui \
         papywizard/view/loggerDialog.ui \
         papywizard/view/mainWindow.ui \
         papywizard/view/nbPictsDialog.ui \
         papywizard/view/shootDialog.ui \
         papywizard/view/totalFovDialog.ui

SOURCES += papywizard/common/configManager.py \
           papywizard/common/config.py \
           papywizard/common/exception.py \
           papywizard/common/helpers.py \
           papywizard/common/loggingAspects.py \
           papywizard/common/loggingFormatter.py \
           papywizard/common/loggingServices.py \
           papywizard/common/orderedDict.py \
           papywizard/common/presetManager.py \
           papywizard/common/publisher.py \
           papywizard/common/qLoggingFormatter.py \
           papywizard/common/signal.py

SOURCES += papywizard/controller/abstractController.py \
           papywizard/controller/bluetoothChooserController.py \
           papywizard/controller/configController.py \
           papywizard/controller/helpAboutController.py \
           papywizard/controller/loggerController.py \
           papywizard/controller/mainController.py \
           papywizard/controller/messageController.py \
           papywizard/controller/nbPictsController.py \
           papywizard/controller/shootController.py \
           papywizard/controller/spy.py \
           papywizard/controller/totalFovController.py

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

SOURCES += papywizard/model/camera.py \
           papywizard/model/data.py \
           papywizard/model/lens.py \
           papywizard/model/scan.py \
           papywizard/model/shooting.py

SOURCES += papywizard/scripts/main3D.py \
           papywizard/scripts/main.py \
           papywizard/scripts/mainSimul.py \
           papywizard/view3D/povexport.py \
           papywizard/view3D/view3D.py \
           papywizard/view/icons.py \
           papywizard/view/logBuffer.py \
           papywizard/view/messageDialog.py \
           papywizard/view/pictureItem.py \
           papywizard/view/shootingScene.py

TRANSLATIONS += locale/papywizard_en.ts \
                locale/papywizard_fr.ts \
                locale/papywizard_pl.ts \
                locale/papywizard_de.ts \
                locale/papywizard_it.ts
