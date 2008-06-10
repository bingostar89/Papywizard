# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Fr�d�ric Mantegazza

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

Spy

Implements
==========

- Spy

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import threading

from papywizard.common.loggingServices import Logger
from papywizard.common.signal import Signal
from papywizard.common.exception import HardwareError


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
            try:
                self.__yaw, self.__pitch = self.__model.hardware.readPosition()
                Logger().debug("Spy.__init__(): yaw=%.1f, pitch=%.1f" % (self.__yaw, self.__pitch))
            except HardwareError:
                Logger().exception("Spy.run()")
            Spy.__init = False
        
    def run(self):
        """ Main entry of the thread.
        """
        self.__run = True
        while self.__run:
            if self.__suspend:
                while self.__suspend:
                    time.sleep(self.__refresh)
            self.execute()
            
            time.sleep(self.__refresh)
            
    def execute(self):
        """ Execute one refresh.
        """
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
            
        return True

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
