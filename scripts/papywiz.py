#!/usr/bin/env python
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

Main script

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path
import traceback
import StringIO

import pygtk
pygtk.require("2.0")
import gtk
import gobject

try:
    import papywizard
except ImportError:
    path = os.path.dirname(__file__)
    sys.path.append(os.path.join(path, os.path.pardir))
from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.serializer import Serializer
from papywizard.common.exception import HardwareError
from papywizard.hardware.head import Head, HeadSimulation
from papywizard.model.shooting import Shooting
from papywizard.controller.mainController import MainController
from papywizard.controller.spy import Spy
from papywizard.view.logBuffer import LogBuffer
if config.VIEW3D_ENABLE:
    from papywizard.view3D.view3D import View3D


class Papywizard(object):
    """ Main application class.
    """
    def __init__(self):
        """ Init the application.
        """
        gtkLogStream = LogBuffer()
        Logger().addStreamHandler(gtkLogStream)
        Logger().setLevel(ConfigManager().get('Logger', 'LOGGER_LEVEL'))

        Logger().info("Starting Papywizard app...")

        # Threads
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()

        # Create hardware and model
        head = Head()
        headSimulation = HeadSimulation()
        self.__model = Shooting(head, headSimulation)

        # Launch spy thread
        Spy(self.__model, config.SPY_FAST_REFRESH)
        Spy().start()

        # Create 3D view
        if config.VIEW3D_ENABLE:
            self.__view3D = View3D("Papywizard", scale=(1, 1, 1))
            Spy().newPosSignal.connect(self.__view3D.draw)
            #Spy().newPosSignal.connect(self.__view3D.viewFromCamera)

        # Create serializer, for async events
        serializer = Serializer()
        gobject.timeout_add(50, serializer.processWork)

        # Create main controller
        controller = MainController(serializer, self.__model, gtkLogStream)

    def run(self):
        """ Run the appliction.
        """
        gtk.main()

    def shutdown(self):
        """ Shutdown the application.
        """
        Spy().stop()
        Spy().join()
        self.__model.shutdown()

        # Threads
        gtk.gdk.threads_leave()

        #if config.VIEW3D_ENABLE:
            #self.__view3D.terminate() # vpython has not yet a way to terminate the mainloop

        Logger().info("Papywizard app stopped")


def main():
    try:
        app = Papywizard()
        app.run()
        app.shutdown()

    except Exception, msg:
        Logger().exception("main()")
        tracebackString = StringIO.StringIO()
        traceback.print_exc(file=tracebackString)
        message = tracebackString.getvalue().strip()
        tracebackString.close()
        messageDialog = gtk.MessageDialog(flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
                                          message_format="Internal error")
        messageDialog.format_secondary_text(message)
        messageDialog.run()
        messageDialog.destroy()


if __name__ == "__main__":
    main()
