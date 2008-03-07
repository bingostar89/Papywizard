# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Main entry.

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import sys

from common import config
from common.loggingServices import Logger
from common.preferences import Preferences
from common.serializer import Serializer
from common.exception import HardwareError
from model.shooting import Shooting
from view.mainWindow import MainWindow
from controller.mainController import MainController
from controller.spy import Spy
try:
    from hardware.head import Head, HeadSimulation
except ImportError:
    Logger().exception("panohead initial imports")
try:
    from view3D.view3D import View3D
except ImportError:
    Logger().exception("panohead initial imports")


def main():
    def serializerProcessWork(root):
        """ Method called by Tkinter after method to call the serializer.
        
        @param root: Tkinter root window
        @type root: {Tk}
        """
        serializer.processWork()
        root.after(10, serializerProcessWork, root)
        
    Logger().setConsoleLevel(config.LOGGER_LEVEL)

    # Create model (both real and simulated)
    try:
        head = Head()
    except (NameError, HardwareError):
        Logger().exception("Creating real hardware")
        Logger().warning("Some libs are missing in order to use real hardware")
        head = None
    headSimulation = HeadSimulation()
    model = Shooting(head, headSimulation)
    
    # Launch spy thread
    Spy(model, config.SPY_FAST_REFRESH)
    Spy().start()

    # Create 3D view
    if config.VIEW3D_ENABLE:
        try:
            view3D = View3D("Panohead", scale=(1, 1, 1))
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

    # Create main view
    root = MainWindow()
    root.after(50, serializerProcessWork, root)
    
    # Create main controller
    controller = MainController(serializer, model, root, view3D)
    
    # Enter in Tkinter mainloop
    root.mainloop()

    # App closed
    Spy().stop()
    Spy().join()
    headSimulation.stopGoto()
    #view3D.terminate() # vpython has not yet a way to terminate the mainloop
    

if __name__ == "__main__":
    Logger().info("Starting panohead app...")
    main()
    Logger().info("Panohead app stopped")
    sys.exit()
