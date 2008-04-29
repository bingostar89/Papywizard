# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Main entry.

@author: Frederic Mantegazza
@copyright: 2007-2008
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import sys

import gtk
import gobject

from common import config
from common.loggingServices import Logger
from common.preferences import Preferences
from common.serializer import Serializer
from common.exception import HardwareError
from model.shooting import Shooting
from view_gtk.mainWindow import MainWindow
from controller_gtk.mainController import MainController
from controller.spy import Spy
try:
    from hardware.head import Head, HeadSimulation
except ImportError:
    Logger().exception("Papywizard initial imports")
try:
    from view3D.view3D import View3D
except ImportError:
    Logger().exception("Papywizard initial imports")


def main():
    Logger().setConsoleLevel(config.LOGGER_LEVEL)

    # Create model (both real and simulated)
    try:
        head = Head()
    except (NameError, ImportError):
        Logger().exception("Creating real hardware")
        Logger().warning("Some libs are missing in order to use real hardware")
        head = None
    except HardwareError:
        Logger().exception("Creating real hardware")
        Logger().warning("Problem occured; unable to use real hardware")
        head = None
    headSimulation = HeadSimulation()
    model = Shooting(head, headSimulation)
    
    # Launch spy thread
    Spy(model, config.SPY_FAST_REFRESH)
    Spy().start()

    # Create 3D view
    if config.VIEW3D_ENABLE:
        try:
            view3D = View3D("Papywizard", scale=(1, 1, 1))
            Spy().newPosSignal.connect(view3D.draw)
            #Spy().newPosSignal.connect(view3D.viewFromCamera)
        except NameError:
            Logger().exception("main()")
            Logger().warning("Some libs are missing in order to use 3D view")
            view3D = None
    else:
        view3D = None

    # Create serializer, for async events
    serializer = Serializer()
    gobject.timeout_add(10, serializer.processWork)

    # Create main view
    view = MainWindow()
    
    # Create main controller
    controller = MainController(serializer, model, view, view3D)

    # Enter in Gtk mainloop
    gtk.gdk.threads_init()
    gtk.main()

    # App closed
    Spy().stop()
    Spy().join()
    headSimulation.stopGoto()
    model.shutdown()
    #view3D.terminate() # vpython has not yet a way to terminate the mainloop
    

if __name__ == "__main__":
    Logger().info("Starting Papywizard app...")
    main()
    Logger().info("Papywizard app stopped")
    sys.exit()
