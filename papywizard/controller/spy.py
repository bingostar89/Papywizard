# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2010 Frédéric Mantegazza

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

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import threading

from PyQt4 import QtCore, QtNetwork

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.signal import Signal
from papywizard.common.exception import HardwareError

spy = None


class SpyObject(QtCore.QThread):
    """ Spy.

    This controller periodically polls the hardware to get
    its position. When a change is detected, it emits
    a signal, passing the new hardware position.
    """
    def __init__(self, model):
        """ Init the object.

        @param model: model to use
        @type model: {Shooting}
        """
        QtCore.QThread.__init__(self)
        self.__model = model
        self.__run = False
        self.__suspend = True  # The spy starts suspended
        self.__yaw = None
        self.__pitch = None

    # Signals
    def update(self, yaw, pitch):
        """ Update position.

        @param yaw: position yaw
        @type yaw: float

        @param pitch: position pitch
        @type pitch: float
        """
        self.emit(QtCore.SIGNAL("update"), yaw, pitch)

    # Main loop
    def run(self):
        """ Main entry of the thread.
        """
        threading.currentThread().setName("Spy")
        Logger().info("Starting Spy...")

        # Enter main loop
        self.__run = True
        try:
            while self.__run:
                if self.__suspend:
                    Logger().info("Spy suspended")
                    while self.__suspend:
                        self.msleep(config.SPY_REFRESH_DELAY)
                    Logger().info("Spy resumed")
                if not self.__run:
                    break
                self.refresh()
                self.msleep(config.SPY_REFRESH_DELAY)

            Logger().info("Spy stopped")
        except:
            Logger().exception("Spy.run()")
            Logger().critical("Spy thread crashed")

    def refresh(self, force=False):
        """ Execute one refresh.

        @param force: if True, emit signal even if same position
        @type force: bool
        """
        try:
            yaw, pitch = self.__model.head.readPosition()
            if force or yaw != self.__yaw or pitch != self.__pitch:
                #Logger().debug("Spy.execute(): new yaw=%.1f, new pitch=%.1f" % (yaw, pitch))
                try:

                    # Emit Qt signal
                    self.update(yaw, pitch)
                except:
                    Logger().exception("Spy.refresh(): can't emit signal")
                self.__yaw = yaw
                self.__pitch = pitch
        except: # HardwareError:
            Logger().exception("Spy.refresh(): can't read position")

    def stop(self):
        """ Stop the thread.
        """
        self.__run = False
        self.__suspend = False

    def suspend(self):
        """ Suspend thread execution.
        """
        self.__suspend = True

    def resume(self):
        """ Resume thread execution.
        """

        # Force a refresh
        #self.refresh(force=True) # Lead to a dead lock...

        self.__suspend = False

    def isRunning(self):
        """ Test if spy is running.

        warning: this method overloads the QThread one!!!

        @return: True if running, False if not
        @rtype: bool
        """
        return self.__run

    def isSuspended(self):
        """ Test if spy is suspended.

        @return: True if suspended, False if not
        @rtype: bool
        """
        return self.__suspend


# Spy factory
def Spy(model=None):
    global spy
    if spy is None:
        if model is None:
            raise ValueError("Spy first call must have correct params")
        spy = SpyObject(model)

    return spy
