# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Hardware classes.

Implements class:

- Axis
- AxisSimulation

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time
import threading

from common import config
from common.loggingServices import Logger
from common.exception import HardwareError
from common.helpers import decodeAxisValue, encodeAxisValue, deg2cod, cod2deg


class Axis(object):
    """ Hardware axis.
    """
    def __init__(self, num, driver):
        """ Init the object.
        """
        self._num = num
        self._driver = driver

    def _sendCmd(self, cmd, param=""):
        """ Send a command to the axis.
        
        @param cmd: command to send
        @type cmd: str
        
        @return: answer
        @rtype: str
        
        @todo: check if bus is busy before sending command (really usefull?) -> in acquireBus ?
               Added try/except arround driver.sendCmd() call, and resend if failed.
        """
        cmd = "%s%d%s" % (cmd, self._num, param)
        for nbTry in xrange(3):
            try:
                answer = self._driver.sendCmd(cmd)
            except IOError:
                Logger().exception("Axis._sendCmd")
                Logger().warning("Axis._sendCmd(): axis %d can't sent command. Retrying..." % self._num)
            else:
                break
        if nbTry == 2:
            raise HardwareError("Axis %d can't send command" % self._num)
        #Logger().debug("Axis._sendCmd(): axis %d cmd=%s, ans=%s" % (self._num, cmd, answer))
        return answer

    def reset(self):
        """ Init the hardware.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            self._sendCmd("F")
            self._sendCmd("a")
            self._sendCmd("D")
        finally:
            self._driver.releaseBus()
    
    init = reset
    
    def read(self):
        """ Return the current position of axis.
        
        @return: position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            value = self._sendCmd("j")
        finally:
            self._driver.releaseBus()
        pos = cod2deg(decodeAxisValue(value))
        
        return pos

    def drive(self, pos, inc=False, wait=True):
        """ Drive the axis.
        
        @param pos: position to reach, in °
        @type pos: float
        
        @param inc: if True, pos is an increment
        @type inc: bool
        
        @param wait: if True, wait for end of movement,
                     returns immediatly otherwise.
        @type wait: boot
        """
        
        # Compute absolute position from increment if needed
        if inc:
            currentPos = self.read()
            pos = currentPos + inc
            
        # Drive to requested position
        strValue = encodeAxisValue(deg2cod(pos))
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            self._sendCmd("G", "00")
            self._sendCmd("S", strValue)
            self._sendCmd("J")
        finally:
            self._driver.releaseBus()
        
        # Wait end of movement
        if wait:
            self.waitEndOfDrive()
    
    def stopDrive(self):
        """ stop drive axis.
        """
        self._sendCmd("L")
        self.waitStop()
        #self.stopJog()
        
    def waitEndOfDrive(self):
        """ Wait for end of drive.
        """
        while True:
            status = self.getStatus()
            if status[1] == '0':
                break
            time.sleep(0.1)
        self.waitStop()
        
    #def drive2(self, pos, inc=False):
        #""" Drive the axis.
        
        #This method implements an external closed loop regulation.
        #It is faster for angles < 6-7°, because in this case, the
        #head does not accelerate to full speed, but rather stays at
        #minimum speed!!!
        
        #@param pos: position to reach, in °
        #@type pos: float
        
        #@param inc: if True, pos is an increment
        #@type inc: bool
        #"""
        
        ## Compute absolute position from increment if needed
        #if inc:
            #currentPos = self.read()
            #pos = currentPos + inc

        #self._driver.acquireBus()
        #try:
            #self._sendCmd("L")
            #initialPos = self.read()
            
            ## Compute direction
            #if pos > initialPos:
                #self._sendCmd("G", "30")
            #else:
                #self._sendCmd("G", "31")
                
            ## Load speed
            #self._sendCmd("I", "500000")
            
            ## Start move
            #self._sendCmd("J")
        #finally:
            #self._driver.releaseBus()
        
        ## Closed-loop drive
        #while abs(pos - self.read()) > .5: # optimal delta depends on speed/inertia
            ##time.sleep(0.05)
            #pass
        #self.stopJog()
        
        ## Final drive (auto) if needed
        #if abs(pos - self.read()) > config.AXIS_ACCURACY:
            #self.drive(pos)
    
    def startJog(self, dir):
        """ Start axis in specified direction.
        
        @param dir: direction ('+', '-')
        @type dir: char
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            if dir == '+':
                self._sendCmd("G", "30")
            elif dir == '-':
                self._sendCmd("G", "31")
            else:
                raise ValueError("Axis %d dir. must be in ('+', '-')" % self._num)
            
            self._sendCmd("I", "220000")
            self._sendCmd("J")
        finally:
            self._driver.releaseBus()
    
    def stopJog(self):
        """ Stop the axis.
        """
        self._sendCmd("L")
        self.waitStop()
       
    def waitStop(self):
        """ Wait until axis does not move anymore (inertia).
        """
        pos = self.read()
        time.sleep(0.05)
        while True:
            if round(abs(pos - self.read()), 1) == 0:
                break
            pos = self.read()
            time.sleep(0.05)

    def getStatus(self):
        """ Return the status of the axis.
        """
        return self._sendCmd("f")
    
    def setOutput(self, level):
        """ Set souput to level.
        
        The output of the V axis is wired to the shoot opto.
        Using thie method on the other axis does nothing.
        
        @param level: level to set to shoot output
        @type level: int
        """
        self._driver.acquireBus()
        try:
            if level:
                self._sendCmd("O", "1")
            else:
                self._sendCmd("O", "0")
        finally:
            self._driver.releaseBus()


class AxisSimulation(threading.Thread):
    """ Simulated hardware axis.
    """
    def __init__(self, num):
        """ Init the object.
        """
        super(AxisSimulation, self).__init__()
        self.setDaemon(1)
        
        self._num = num
        self.__pos = 0.
        self.__jog = False
        self.__drive = False
        self.__setpoint = None
        self.__dir = None
        self.__time = None
        self.__run = False

    def run(self):
        """ Main entry of the thread.
        """
        self.__run = True
        while self.__run:
            
            # Jog command
            if self.__jog:
                if self.__time == None:
                    self.__time = time.time()
                else:
                    inc = (time.time() - self.__time) * config.AXIS_SPEED
                    self.__time = time.time()
                    if self.__dir == '+':
                        self.__pos += inc
                    elif self.__dir == '-':
                        self.__pos -= inc
                    Logger().debug("AxisSimulation.run(): axis %d inc=%.1f, new __pos=%.1f" % (self._num, inc, self.__pos))
            else:
                self.__time = None
                    
            # Drive command. Check when stop
            if self.__drive:
                #Logger().trace("AxisSimulation.run(): axis %d driving" % self._num)
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
                
            time.sleep(config.SPY_FAST_REFRESH)
            
    def stop(self):
        """ Stop the thread.
        """
        self.__run = False

    def reset(self):
        """ Init the hardware.
        
        Nothing special to do.
        """
        self.__jog = False
        self.__drive = False
    
    init = reset
    
    def read(self):
        """ Return the current position of axis.
        
        @return: position, in °
        @rtype: float
        """
        return self.__pos

    def drive(self, pos, inc=False, wait=True):
        """ Drive the axis.
        
        @param pos: position to reach, in °
        @type pos: float
        
        @param inc: if True, pos is an increment
        @type inc: bool
        
        @param wait: if True, wait for end of movement,
                     returns immediatly otherwise.
        @type wait: boot
        """
        Logger().debug("AxisSimulation.drive(): axis %d drive to %.1f" % (self._num, pos))
        
        # Compute absolute position from increment if needed
        if inc:
            self.__setpoint = self.__pos + inc
        else:
            self.__setpoint = pos
        
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
    
    def stopDrive(self):
        """ Stop the axis while in drive mode.
        """
        self.__jog = False
        self.__drive = False

    def waitEndOfDrive(self):
        while self.__drive:
            time.sleep(0.1)
    
    def startJog(self, dir):
        self.__dir = dir
        self.__jog = True
    
    def stopJog(self):
        self.__jog = False
        self.waitStop()
       
    def waitStop(self):
        """ Wait until axis does not move anymore.
        
        Nothing special to do.
        """
        pass

    def getStatus(self):
        """ Return the status of the axis.
        """
        return "000"
    
    def setOutput(self, level):
        """ Set souput to level.
        
        The output of the V axis is wired to the shoot opto.
        Using thie method on the other axis does nothing.
        
        @param level: level to set to shoot output
        @type level: int
        """
        Logger().debug("AxisSimulation.setOutput(): axis %d level=%d" % (self._num, level))
        pass
