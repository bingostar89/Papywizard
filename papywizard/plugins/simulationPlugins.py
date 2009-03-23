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

Axis plugin

Implements
==========

- AxisPlugin

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: axisPlugin.py 1595 2009-03-12 12:39:38Z fma $"

from PyQt4 import QtCore

from papywizard.hardware.axisPlugin import AxisPlugin


class SimulationAxis(AxisPlugin, QtCore.QThread):
    """ Simulated hardware axis.
    """
    def _init(self):
        AbstractAxis.__init__(self, num)
        QtCore.QThread.__init__(self)

        self._manualSpeed = 1.
        self.__pos = 0.
        self.__jog = False
        self.__drive = False
        self.__setpoint = None
        self.__dir = None
        self.__time = None
        self.__run = False
        self.__name = None

    def run(self):
        """ Main entry of the thread.
        """
        threading.currentThread().setName(self.__name)
        self.__run = True
        while self.__run:

            # Jog command
            if self.__jog:
                if self.__time == None:
                    self.__time = time.time()
                else:
                    if self.__drive:
                        inc = (time.time() - self.__time) * config.AXIS_SPEED
                    else:
                        inc = (time.time() - self.__time) * config.AXIS_SPEED * self._manualSpeed
                    self.__time = time.time()
                    if self.__dir == '+':
                        self.__pos += inc
                    elif self.__dir == '-':
                        self.__pos -= inc
                    #Logger().debug("AxisSimulation.run(): axis %d inc=%.1f, new __pos=%.1f" % (self._num, inc, self.__pos))
            else:
                self.__time = None

            # Drive command. Check when stop
            if self.__drive:
                #Logger().trace("AxisSimulation.run(): ax&is %d driving" % self._num)
                if self.__dir == '+':
                    if self.__pos >= self.__setpoint:
                        self.__jog = False
                        self.__drive = False
                        self.__pos = self.__setpoint
                elif self.__dir == '-':
                    if self.__pos <= self.__setpoint:
                        self.__jog = False
                        self.__drive = False
                        self.__pos = self.__setpoint

            self.msleep(config.SPY_FAST_REFRESH)

        Logger().debug("AxisSimulation.run(): axis simulation thread terminated")

    def stopThread(self):
        """ Stop the thread.
        """
        self.__run = False

    def init(self):
        self.__jog = False
        self.__drive = False

    def reset(self):
        self.__jog = False
        self.__drive = False

    def read(self):
        return self.__pos - self._offset

    def drive(self, pos, inc=False, useOffset=True, wait=True):
        Logger().debug("AxisSimulation.drive(): axis %d drive to %.1f" % (self._num, pos))

        # Compute absolute position from increment if needed
        if inc:
            self.__setpoint = self.__pos + inc
        else:
            if useOffset:
                self.__setpoint = pos + self._offset
            else:
                self.__setpoint = pos

        self._checkLimits(self.__setpoint)

        # Drive to requested position
        if self.__setpoint > self.__pos:
            self.__dir = '+'
        elif self.__setpoint < self.__pos:
            self.__dir = '-'
        else:
            return
        self.__drive = True
        self.__jog = True

        # Wait end of movement
        if wait:
            self.waitEndOfDrive()

    def stop(self):
        self.__jog = False
        self.__drive = False

    def waitEndOfDrive(self):
        while self.__drive:
            time.sleep(0.1)

    def startJog(self, dir_):
        self.__dir = dir_
        self.__jog = True

    def waitStop(self):
        pass

    def isMoving(self):
        return self.__jog

    def getStatus(self):
        return "000"

    def setOutput(self, level):
        Logger().debug("AxisSimulation.setOutput(): axis %d level=%d" % (self._num, level))

    def setManualSpeed(self, speed):
        if speed == 'slow':
            self._manualSpeed = .2
        elif speed == 'normal':
            self._manualSpeed = 1.
        elif speed == 'fast':
            self._manualSpeed = 2.
