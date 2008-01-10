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
from common.signal import Signal
from common.exception import HardwareError


class Spy(threading.Thread):
    """ Spy.
    
    This controller periodically polls the hardware to get
    its position. When a change is detected, it emits
    a signal, passing new hardware position.
    """
    __state = {}
    __init = True

    def __new__(cls, *args, **kwds):
        """ Implement the Borg pattern.
        """
        self = object.__new__(cls, *args, **kwds)
        self.__dict__ = cls.__state
        return self

    def __init__(self, model=None, refresh=None):
        """ Init the object.

        @param model: model to use
        @type mode: {Shooting}

        @param view3D: associated view
        @type view3D: {Head3D}
        """
        if Spy.__init:
            if model is None or refresh is None:
                raise ValueError("Spy first call must have correct params")
            super(Spy, self).__init__()
            self.setDaemon(1)
            self.__model = model
            self.__run = False
            self.__suspend = False
            self.__refresh = refresh
            self.newPosSignal = Signal()
            Spy.__init = False
        
    def run(self):
        """ Main entry of the thread.
        """
        self.__run = True
        try:
            self.__yaw, self.__pitch = self.__model.hardware.readPosition()
        except HardwareError:
            Logger().exception("Spy.run()")
        try:
            self.newPosSignal.emit(self.__yaw, self.__pitch)
        except:
            Logger().exception("Spy.run()")
        while self.__run:
            if self.__suspend:
                while self.__suspend:
                    time.sleep(0.01)
            try:
                yaw, pitch = self.__model.hardware.readPosition()
            except HardwareError:
                Logger().exception("Spy.run()")
            if yaw != self.__yaw or pitch != self.__pitch:
                Logger().debug("Spy.run(): new yaw=%.1f, new pitch=%.1f" % (yaw, pitch))
                try:
                    self.newPosSignal.emit(yaw, pitch)
                except:
                    Logger().exception("Spy.run()")
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