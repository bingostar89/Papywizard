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

Hardware

Implements
==========

 - OwlHardware
  - OwlHardware

Owl protocol
===================

Binary command format:
Every command starts with the module address, followed by the command, command type, motor number, value



When the Owl receives a command, it answers immediatly. The reply consits of:
- the address character for the host
- the address character of the module
- the status code as a decimal
- the return value of the command as a decimal number


The status codes are:
100 - Successfully executed, no error
101 - Command loaded into program EEPROM
1   - Wrong checksum
2   - Invalid command
3   - Wrong type
4   - Invalid value
5   - Command not available




Command                                         
Rotate left                    AROL<axis>,<velocity>
Rotate right                   AROR<axis>,<velocity>
Motor stop                     AMST<axis>
Move to position absolute      AMVP ABS,<axis>,<position>
Move to position relative      AMVP REL,<axis>,<offset>
Move to position Coordinate    AMVP COORD,<axis>,<coordinate number>
Get axis position              AGAP 1,<axis>
Zero axis position             ASAP 1,<axis>,0
Shutter Activate               ASIO 1,2,<state> (1/0)
Get input/output               AGIO <port>,2,0
Return to Binary control       ABIN

(also see Trinamic TMCL Firmware Manual).

@author: Frédéric Mantegazza
@copyright: (C) 2007-2010 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from PyQt4 import QtCore

from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.hardware.abstractHardware import AbstractHardware

ENCODER_ZERO = 0   #add zero counter in homing commands

class OwlHardware(AbstractHardware):
    """ Owl low-level hardware.
    """
    def _init(self):
        AbstractHardware._init(self)
        self.__encoderFullCircle = None
        
    def __zeroAxisValue(self): #added for zeroing axis home position
        
        cmd = "ASAP 1,", self._axis,", 0" #zero axis position
        self._driver.empty()
        self._driver.write("%s\r" % cmd)
        c = ''
        c = self._driver.read(100)
        (header, errorCode, replyValue) = c.split(' ') #splits incoming string
        if errorCode != '100':
            raise HardwareError("Axis did not set home")#check  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def __shutdown(): #not sure if already set or should be in Plugin!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       
        cmd = "AMVP ABS, 0, 0"               #send axis 0 home
        self._driver.empty()
        self._driver.write("%s\r" % cmd)
        c = ''
        c = self._driver.read(100)
        (header, errorCode, replyValue) = c.split(' ') #splits incoming string
        if errorCode != '100':
            raise HardwareError("Axis did not go home")#check  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        cmd = "AMVP ABS, 1, 0"               #send axis 1 home
        self._driver.empty()
        self._driver.write("%s\r" % cmd)
        c = ''
        c = self._driver.read(100)
        (header, errorCode, replyValue) = c.split(' ') #splits incoming string
        if errorCode != '100':
            raise HardwareError("Axis did not go home")#check  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        cmd = "ABIN"                         #return module to binary input
        self._driver.empty()
        self._driver.write("%s\r" % cmd)
            

    def __decodeAxisValue(self, strValue):
        """ Decode value from axis.

        Values (position, speed...) returned by axis are
        strings of an integer value.

        @param strValue: value returned by axis
        @type strValue: str

        @return: value
        @rtype: int
        """
        value = int(strValue)
        return value

    def __encodeAxisValue(self, value):
        """ Encode value for axis.

        Values (position, speed...) to send to axis must be
        string of an integer.

        @param value: value
        @type value: int

        @return: value to send to axis
        @rtype: str
        """
        strValue = str(value)
        return strValue.upper()

    def __encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        return codPos * 360 / 1152000

    def __angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: int
        """
        return int(pos * 1152000 / 360.)

    def __sendCmd(self, cmd):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @return: answer
        @rtype: str
        """
        Logger().debug("OwlHardware.__sendCmd(): cmd=%s" % (repr(cmd)))
        for nbTry in xrange(self._nbRetry):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write("%s\r" % cmd)
                c = ''
                '''c = self._driver.read(100)
                (header, errorCode, replyValue) = c.split(' ')
                if errorCode != '100':
                    raise IOError("Error in command %s (err=%s)" % (repr(cmd), c))'''
                answer = ""
                while True:
                    c = self._driver.read(1)
                    if c == '\r':
                        break
                    answer += c
                (header, errorCode, replyValue) = answer.split(" ")
                answer = (replyValue)
                if errorCode == '100':
                    return answer #will this work 

            except IOError:
                Logger().exception("OwlHardware.__sendCmd")
                Logger().warning("OwlHardware.__sendCmd(): axis %d can't sent command %s. Retrying..." % (self._axis, repr(cmd)))
            else:
                break
        else:
            raise HardwareError("axis %d can't send command %s" % (self._axis, repr(cmd)))
        #Logger().debug("OwlHardware.__sendCmd(): axis %d ans=%s" % (self._axis, repr(answer)))

        return answer

    def init(self):
        """ Init the Owl hardware.

        Done only once.
        """
        if self._axis == 0:            
            self._driver.acquireBus()
            try:
                
                self.__encoderFullCircle = 1152000
            
                cmd = '\x01\x8B\x00\x00\x00\x00\x00\x00\x8C' #set module to ascii
                self._driver.empty()
                self._driver.write("%s\r" % cmd)
            
                cmd = 'ASGP 67, 0, 33' #echo cancel
                self._driver.empty()
                self._driver.write("%s\r" % cmd)
                c = ''
                answer = ""
                while True:
                    c = self._driver.read(1)
                    if c == '\r':
                        break
                    answer += c
                (header, errorCode, replyValue) = answer.split(" ")
                #Logger().debug("int(): answer=%s header=%s errorCode=%s replyValue=%s" % (answer, header, errorCode, replyValue))
                value = int(replyValue)
                
                if errorCode != '100':
                    raise HardwareError("Module did not initialize properly")
                    Logger().debug("OwlHardware.init(): encoder full circle=%s" % self.__encoderFullCircle)

            finally:
                self._driver.releaseBus()
        return

    def read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            cmd = "AGAP 1, %d" % self._axis
            value = self.__sendCmd(cmd)
            Logger().debug("read(): value=%s" % (value))
            
        finally:
            self._driver.releaseBus()
        pos = self.__encoderToAngle(self.__decodeAxisValue(value))
        return pos

    def drive(self, pos):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float
        """
        strValue = self.__encodeAxisValue(self.__angleToEncoder(pos))
        self._driver.acquireBus()
        try:
            cmd = "AMSP %d" % self._axis
            self.__sendCmd(cmd) #stop motor
            cmd = "AMVP ABS, %d, %s" % (self._axis, strValue)
            self.__sendCmd(cmd) #goto absolute position
            
        finally:
            self._driver.releaseBus()

    def stop(self):
        """ Stop the axis.
        """
        self._driver.acquireBus()
        try:
            cmd = "AMST %d" % self._axis
            self.__sendCmd(cmd)
        finally:
            self._driver.releaseBus()

    def startJog(self, dir_, speed):
        """ Start the axis.

        @param dir_: direction ('+', '-')
        @type dir_: str

        @param speed: speed
        @type speed: int
        """
        self._driver.acquireBus()
        try:
            if dir_ == '+':
                cmd = "AROR %d, %d" %(self._axis, speed)
                self.__sendCmd(cmd)
            elif dir_ == '-':
                cmd = "AROL %d, %d" %(self._axis, speed)
                self.__sendCmd(cmd)
            else:
                raise ValueError("Axis %d dir. must be in ('+', '-')" % self._axis)
        finally:
            self._driver.releaseBus()

    def getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self._driver.acquireBus()
        try:
            cmd = "AGAP 3, %d" % self._axis
            return self.__sendCmd(cmd)
        finally:
            self._driver.releaseBus()

    def setOutput(self, state):
        """ Set output state.

        @param state: new state of the the output
        @type state: bool
        """
        self._driver.acquireBus()
        try:
            if state == True:
	      cmd = "ASIO 0, 2, 1"
	      self.__sendCmd(cmd)
	      time.sleep(0.1)
	      cmd = "ASIO 1, 2, 1"
	      self.__sendCmd(cmd)
	    elif state == False:	      
	      cmd = "ASIO 1, 2, 0"
	      self.__sendCmd(cmd)
	      cmd = "ASIO 0, 2, 0"
	      self.__sendCmd(cmd)
            
        finally:
            self._driver.releaseBus()
