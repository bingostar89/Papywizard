# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Controller.

Implements class:

- Spy

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import math
import time
import threading

from common import config
from common.loggingServices import Logger


class Head3DController(threading.Thread):
    """ Controller for 3D head view.
    
    This controller periodically polls the hardware to get
    the hardware position. When a change is detected, it emits
    a signal, passing new hardware position.
    """
    def __init__(self, model, view3D):
        """ Init the object.

        @param model: model to use
        @type mode: {Shooting}

        @param view3D: associated view
        @type view3D: {Head3D}
        """
        super(Head3DController, self).__init__()
        self.setDaemon(1)

        self.__model = model
        self.__view3D = view3D
        self.__run = False
        self.__suspend = False
        self.__refresh = config.VIEW3D_CONTROLLER_REFRESH
        
    def run(self):
        """ Main entry of the thread.
        """
        self.__run = True
        self.__yaw, self.__pitch = self.__model.hardware.readPosition()
        self.__view3D.draw(self.__yaw, self.__pitch)
        while self.__run:
            if self.__suspend:
                while self.__suspend:
                    time.sleep(0.01)
            yaw, pitch = self.__model.hardware.readPosition()
            if yaw != self.__yaw or pitch != self.__pitch:
                Logger().debug("Head3DController.run(): yaw=%.1f, pitch=%.1f" % (yaw, pitch))
                self.__view3D.draw(self.__yaw, self.__pitch)
                self.__yaw = yaw
                self.__pitch = pitch
            
            time.sleep(self.__refresh)
            
    def stop(self):
        """ Stop the thread.
        """
        self.__run = False
        self.__suspend = True

    def suspend(self):
        """ Suspend thread execution.
        """
        self.__suspend = True
        
    def resume(self):
        """ Resume thread execution.
        """
        self.__suspend = False
        
    def setRefreshRate(self, refresh):
        """ Set the refresh rate.
        
        @param refresh: refresh rate
        @type refresh: float
        """
        self.__refresh = refresh