# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Model.

Implements class:

- Shooting

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time

from common.loggingServices import Logger
from common.preferences import Preferences
from common.exception import HardwareError
from camera import Camera
from mosaic import Mosaic


class Shooting(object):
    """ Shooting model.
    """
    def __init__(self, realHardware, simulatedHardware):
        """ Init the object.

        @param realHardware: real hardware head
        @type realHardware: {Head}

        @param simulatedHardware: simulated hardware head
        @type simulatedHardware: {HeadSimulation}
        """
        self.__realHardware = realHardware
        self.__simulatedHardware = simulatedHardware
        self.__running = False
        self.__suspend = False
        self.__stop = False
        self.__yawCoef = "--"
        self.__pitchCoef = "--"
        self.__progress = "..."
        self.__sequence = "Idle"
        self.__setParams = None
        
        self.hardware = self.__simulatedHardware
        self.camera = Camera()
        self.mosaic = Mosaic()
        
        self.yawStart = 0.
        self.pitchStart = 0.
        self.yawEnd = 0.
        self.pitchEnd = 0.
        #self.yawFov = 0.
        #self.pitchFov = 0.
        #self.yawNbPicts = 0
        #self.pitchNbPicts = 0
        self.position = self.hardware.readPosition()

        self.__prefs = Preferences().load()
        self.delay = self.__prefs['shooting']['delay']
        self.overlap = self.__prefs['shooting']['overlap']
        #self.realYawOverlap = self.overlap
        #self.realPitchOverlap = self.overlap
        self.manualShoot = self.__prefs['shooting']['manualShoot']
        self.cameraOrientation = self.__prefs['shooting']['cameraOrientation']
        
        #self.__computeParams('startEnd')
   
    def __getYawFov(self):
        """
        """
        cameraFov = self.camera.getYawFov(self.cameraOrientation)
        return abs(self.yawEnd - self.yawStart) + cameraFov
    
    yawFov = property(__getYawFov, "Total yaw FoV")
    
    def __getPitchFov(self):
        """
        """
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        return abs(self.pitchEnd - self.pitchStart) + cameraFov

    pitchFov = property(__getPitchFov, "Total pitch FoV")
    
    def __getYawNbPicts(self):
        """
        """
        cameraFov = self.camera.getYawFov(self.cameraOrientation)
        if round(self.yawFov - cameraFov, 1) >= 0.1:
            nbPicts = int(((self.yawFov - self.overlap * cameraFov) / (cameraFov * (1 - self.overlap))) + 1)
        else:
            nbPicts = 1
        return nbPicts

    yawNbPicts = property(__getYawNbPicts, "Yaw nb picts")

    def __getPitchNbPicts(self):
        """
        """
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        if round(self.pitchFov - cameraFov, 1) >= 0.1:
           nbPicts = int(((self.pitchFov - self.overlap * cameraFov) / (cameraFov * (1 - self.overlap))) + 1)
        else:
            nbPicts = 1
        return nbPicts

    pitchNbPicts = property(__getPitchNbPicts, "Pitch nb picts")
    
    def __getRealYawOverlap(self):
        """ Recompute real yaw overlap.
        """
        cameraFov = self.camera.getYawFov(self.cameraOrientation)
        if self.yawNbPicts > 1:
            overlap = (self.yawNbPicts * cameraFov - self.yawFov) / (cameraFov * (self.yawNbPicts - 1))
        else:
            overlap = 1.
        return overlap

    realYawOverlap = property(__getRealYawOverlap, "Real yaw overlap")
   
    def __getRealPitchOverlap(self):
        """ Recompute real pitch overlap.
        """
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        if self.pitchNbPicts > 1:
            overlap = (self.pitchNbPicts * cameraFov - self.pitchFov) / (cameraFov * (self.pitchNbPicts - 1))
        else:
            overlap = 1.
        return overlap

    realPitchOverlap = property(__getRealPitchOverlap, "Real pitch overlap")
   
    #def __computeParams(self, setParam):
        #""" Compute missing params from given params.
        
        #@param setParam: given params type ('startEnd', 'fov', 'nbPict')
        #@type setParam: str
        
        #@todo: add fov and nbPicts
        #"""
        #if setParam == 'startEnd':
            #self.yawFov = self.__getYawFov()
            #self.pitchFov = self.__getPitchFov()
            #self.yawNbPicts = self.__getYawNbPicts()
            #self.pitchNbPicts = self.__getPitchNbPicts()
            #self.realYawOverlap = self.__getRealYawOverlap()
            #self.realPitchOverlap = self.__getRealPitchOverlap()
        #elif setParam == 'fov':
            #Logger().warning("Shooting.__computeParam(): 'fov' setting not yet implemented")
        #elif setParam == 'nbPicts':
            #Logger().warning("Shooting.__computeParam(): 'nbPicts' setting not yet implemented")
        #else:
            #raise ValueError("param must be in ('startEnd', 'fov', 'nbPict')")

    def switchToRealHardware(self):
        """ Use real hardware.
        """
        if self.__realHardware is not None:
            try:
                self.__realHardware.init()
                self.position = self.__realHardware.readPosition()
                self.hardware = self.__realHardware
            except HardwareError:
                Logger().exception("Shooting.switchToRealHardware()")
                Logger().warning("Can't switch to real hardware")
                raise
        else:
            raise HardwareError("No real hardware available")
            
    def switchToSimulatedHardware(self):
        """ Use simulated hardware.
        """
        self.hardware = self.__simulatedHardware
        self.position = self.hardware.readPosition()
        self.hardware.init()

    def storeStartPosition(self):
        """ Store current position as start position.
        """
        self.yawStart, self.pitchStart = self.hardware.readPosition()
        Logger().debug("Shooting.storeStartPosition(): yaw=%.1f, pitch=%.1f" % (self.yawStart, self.pitchStart))
        #self.__computeParams('startEnd')
    
    def storeEndPosition(self):
        """ Store current position as end position.
        """
        self.yawEnd, self.pitchEnd = self.hardware.readPosition()
        Logger().debug("Shooting.storeEndPosition(): yaw=%.1f, pitch=%.1f" % (self.yawEnd, self.pitchEnd))
        #self.__computeParams('startEnd')
    
    def start(self):
        """ Start pano shooting.
        """
        def checkSuspendStop():
            """ Check if suspend or stop requested.
            """
            if self.__suspend:
                Logger().info("Suspend")
                self.__sequence = "Idle"
                while self.__suspend:
                    time.sleep(0.1)
                Logger().info("Resume")
            if self.__stop:
                Logger().info("Stop")
                raise StopIteration
            
        Logger().trace("Shooting.start()")
        self.__running = True
        
        cameraFov = self.camera.getYawFov(self.cameraOrientation)
        try:
            yawInc = (self.yawFov - cameraFov) / (self.yawNbPicts - 1)
        except ZeroDivisionError:
            yawInc = self.yawFov - cameraFov
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        try:
            pitchInc = (self.pitchFov - cameraFov) / (self.pitchNbPicts - 1)
        except ZeroDivisionError:
            pitchInc = self.pitchFov - cameraFov
        self.mosaic.setMatrix(self.yawNbPicts, self.pitchNbPicts)
        
        try:
            
            # Loop over all positions
            for yawCoef, pitchCoef in self.mosaic:
                yaw = self.yawStart + yawCoef * yawInc
                pitch = self.pitchStart + pitchCoef * pitchInc
                Logger().debug("Shooting.start(): Goto yaw=%.1f pitch=%.1f" % (yaw, pitch))
                self.__yawCoef = yawCoef
                self.__pitchCoef = pitchCoef
                Logger().info("Moving")
                self.__sequence = "Moving"
                #self.__progress = "..."
                self.hardware.gotoPosition(yaw, pitch)
    
                Logger().info("Stabilization")
                self.__sequence = "Stabilizing"
                time.sleep(self.delay)
    
                checkSuspendStop()
    
                # todo: implement manual shooting (must be in controller. Use yield here?)
                Logger().info("Shooting")
                for pict in xrange(self.camera.nbPicts):
                    Logger().debug("Shooting.start(): Shooting %d/%d" % (pict + 1, self.camera.nbPicts + 1))
                    self.__sequence = "Shooting %d/%d" % (pict + 1, self.camera.nbPicts)
                    self.hardware.shoot(self.camera.timeValue)
    
                    checkSuspendStop()
            
            # Zenith/Nadir
            # todo: implement stab., manual shooting and multiple shots
            if self.mosaic.zenith:
                Logger().info("Moving")
                Logger().debug("Shooting.start(): Goto zenith")
                self.__yawCoef = "zenith"
                self.__pitchCoef = "zenith"
                self.__sequence = "Moving"
                #self.__progress = "..."
                self.hardware.gotoPosition(0., -90.)

                Logger().info("Stabilization")
                self.__sequence = "Stabilizing"
                time.sleep(self.delay)
                
                checkSuspendStop()
                    
                Logger().info("Shooting")
                for pict in xrange(self.camera.nbPicts):
                    Logger().debug("Shooting.start(): Shooting %d/%d" % (pict + 1, self.camera.nbPicts + 1))
                    self.__sequence = "Shooting %d/%d" % (pict + 1, self.camera.nbPicts)
                    self.hardware.shoot(self.camera.timeValue)
    
                    checkSuspendStop()
                
            if self.mosaic.nadir:
                Logger().info("Moving")
                Logger().debug("Shooting.start(): Goto nadir")
                self.__yawCoef = "nadir"
                self.__pitchCoef = "nadir"
                self.__sequence = "Moving"
                #self.__progress = "..."
                self.hardware.gotoPosition(0., 90.)

                Logger().info("Stabilization")
                self.__sequence = "Stabilizing"
                time.sleep(self.delay)
    
                checkSuspendStop()
    
                Logger().info("Shooting")
                for pict in xrange(self.camera.nbPicts):
                    Logger().debug("Shooting.start(): Shooting %d/%d" % (pict + 1, self.camera.nbPicts + 1))
                    self.__sequence = "Shooting %d/%d" % (pict + 1, self.camera.nbPicts)
                    self.hardware.shoot(self.camera.timeValue)
    
                    checkSuspendStop()
        
        except StopIteration:
            Logger().debug("Shooting.start(): Stop detected")
        
        self.__yawCoef = "--"
        self.__pitchCoef = "--"
        self.__progress = "..."
        self.__sequence = "Idle"
        self.__stop = False
        self.__running = False
    
    def getState(self):
        """ Return shooting state.
        
        @return: key 'yawPos': yaw position
                     'pitchPos': pitch position
                     'yawCoef': yaw mosaic coef
                     'pitchCoef': pitch mosaic coef
                     'progress': shooting progress (num of pict)
                     'sequence': shooting sequence
                 
        @rtype: dict
        """
        try:
            yawCoef = self.__yawCoef + 1
        except TypeError:
            yawCoef = self.__yawCoef
        try:
            pitchCoef = self.__pitchCoef + 1
        except TypeError:
            pitchCoef = self.__pitchCoef
        yawPos, pitchPos = self.hardware.readPosition()
        return {'yawPos': yawPos, 'pitchPos': pitchPos,
                'yawCoef': yawCoef, 'pitchCoef': pitchCoef,
                'progress': self.__progress, 'sequence': self.__sequence}
    
    def isShooting(self):
        """ Test if shooting is running.
        
        @return: True if shooting is running, False otherwise
        @rtype: bool
        """
        return self.__running
    
    def suspend(self):
        """ Suspend execution of pano shooting.
        """
        Logger().trace("Shooting.suspend()")
        self.__suspend = True
    
    def isSuspended(self):
        """ Test if shotting is suspended.
        
        @return: True if shooting is suspended, False otherwise
        @rtype: bool
        """
        return self.__suspend
    
    def resume(self):
        """ Resume  execution of shooting.
        """
        Logger().trace("Shooting.resume()")
        self.__suspend = False
    
    def stop(self): 
        """ Cancel execution of shooting.
        """
        Logger().trace("Shooting.stop()")
        self.__stop = True
        self.__suspend = False
        #self.hardware.stopAxis('yaw')
        #self.hardware.stopAxis('pitch')
        self.hardware.stopGoto()

    def shutdown(self):
        """ Cleanly terminate the model.
        
        Save values to preferences.
        """
        Logger().trace("Shooting.shutdown()")
        self.camera.shutdown()
        self.mosaic.shutdown()
        
        self.__prefs['shooting']['delay'] = self.delay
        self.__prefs['shooting']['overlap'] = self.overlap
        self.__prefs['shooting']['manualShoot'] = self.manualShoot
        self.__prefs['shooting']['cameraOrientation'] = self.cameraOrientation
        
        Preferences().save()
