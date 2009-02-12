#!/usr/bin/env python
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

Main script

@author: FrÃ©dÃ©ric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import threading

import PyQt4.uic
from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.view.icons import qInitResources, qCleanupResources
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.qLoggingFormatter import QSpaceColorFormatter
from papywizard.common.exception import HardwareError
from papywizard.common.publisher import Publisher
from papywizard.hardware.head import Head, HeadSimulation
from papywizard.model.shooting import Shooting
from papywizard.controller.loggerController import LoggerController
from papywizard.controller.mainController import MainController
from papywizard.controller.spy import Spy
from papywizard.view.logBuffer import LogBuffer
from papywizard.view.messageDialog import ExceptionMessageDialog


class BlackHole:
    """ Dummy class for stderr redirection.
    """
    softspace = 0

    def write(self, text):
        pass


class Papywizard(object):
    """ Main application class.
    """
    def __init__(self):
        """ Init the Papywizard object.
        """
        self.logStream = LogBuffer()
        Logger().addStreamHandler(self.logStream, QSpaceColorFormatter)

    def init(self):
        """ Init the application.
        """
        Logger().info("Starting Papywizard...")

        # Init global Qt application
        qtApp = QtGui.QApplication(sys.argv)

        # Init resources and application
        qInitResources()

        # i18n stuff
        locale = QtCore.QLocale.system().name()
        Logger().debug("Papywizard.l10n(): locale=%s" % locale)
        qtTranslator = QtCore.QTranslator()
        if qtTranslator.load("locale/qt_%s" % locale):
            qtApp.installTranslator(qtTranslator)
        else:
            Logger().warning("Can't find qt translation file")
        appTranslator = QtCore.QTranslator()
        if appTranslator.load("locale/papywizard_%s" % locale):
            qtApp.installTranslator(appTranslator)
        else:
            Logger().warning("Can't find papywizard translation file")

        # Qt stylesheet
        try:
            styleSheet = file(config.USER_STYLESHEET_FILE)
            qtApp.setStyleSheet(styleSheet.read())
            styleSheet.close()
        except IOError:
            Logger().warning("No user Style Sheet found")
        styleSheet = qtApp.styleSheet()
        if styleSheet:
            if styleSheet.startsWith("file://"):
                Logger().info("Style Sheet loaded from command line param.")
            else:
                Logger().info("User Style Sheet loaded")

        # Create model
        head = Head()
        headSimulation = HeadSimulation()
        self.__model = Shooting(head, headSimulation)

        # Create spy thread
        Spy(self.__model, config.SPY_FAST_REFRESH)

        # Create publisher thread
        if config.PUBLISHER_ENABLE:
            self.__publisher = Publisher()

        # Create main controller
        self.__mainController = MainController(self.__model, self.logStream)

    def weave(str):
        """ Weave stuffs.
        """
        try:
            from papywizard.common.loggingAspects import logMethods
            logMethods(Head)
            logMethods(HeadSimulation)
            logMethods(MainController)
        except ImportError:
            Logger().warning("Logilab aspects module must be installed to use logging aspects")

    def run(self):
        """ Run the appliction.
        """

        # Start publisher thread if needed
        if config.PUBLISHER_ENABLE:
            self.__publisher.start()

        # Start spy thread
        Spy().start()

        # Set logger level
        Logger().setLevel(ConfigManager().get('Preferences', 'LOGGER_LEVEL'))

        # Enter Qt main loop
        self.__mainController.exec_()

    def shutdown(self):
        """ Shutdown the application.
        """

        # Shutdown controller
        self.__mainController.shutdown()

        # Stop spy thread
        Spy().stop()
        Spy().wait()

        #del self.__publisher

        # Shutdown model
        self.__model.shutdown()

        # Cleanup resources
        qCleanupResources()

        Logger().info("Papywizard stopped")


def main():

    threading.currentThread().setName("MainThread")

    # Init the logger
    if hasattr(sys, "frozen"):
        sys.stderr = BlackHole()
        Logger(defaultStream=False)
    else:
        Logger()

    app = Papywizard()
    try:
        app.init()
        #app.weave()
        app.run()
        app.shutdown()

    except Exception, msg:
        Logger().exception("main()")
        dialog = ExceptionMessageDialog("Unhandled exception", str(msg))
        dialog.exec_()


if __name__ == "__main__":
    main()
