# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Frédéric Mantegazza

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

Model

Implements
==========

- Shooting

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from papywizard.common.loggingServices import Logger
from papywizard.common.signal import Signal
from papywizard.common.configManager import ConfigManager
from papywizard.common.exception import HardwareError
from papywizard.common.data import Data
from papywizard.model.camera import Camera
from papywizard.model.mosaic import Mosaic


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
        self.__running = False
        self.__suspend = False
        self.__stop = False
        self.__yawCoef = "--"
        self.__pitchCoef = "--"
        self.__progress = 0.
        self.__sequence = "Idle"
        self.__setParams = None
        self.__manualShoot = False

        self.realHardware = realHardware
        self.simulatedHardware = simulatedHardware
        self.hardware = self.simulatedHardware
        self.switchToRealHardwareSignal = Signal()
        self.camera = Camera()

        self.yawStart = 0.
        self.pitchStart = 0.
        self.yawEnd = 0.
        self.pitchEnd = 0.
        self.position = self.hardware.readPosition()

        #self.__computeParams('startEnd')

    def __getStabilizationDelay(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'SHOOTING_STABILIZATION_DELAY')
    
    def __setStabilizationDelay(self, stabilizationDelay):
        """
        """
        ConfigManager().setFloat('Preferences', 'SHOOTING_STABILIZATION_DELAY', stabilizationDelay, 1)
    
    stabilizationDelay = property(__getStabilizationDelay, __setStabilizationDelay)
    
    def __getOverlap(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'SHOOTING_OVERLAP')
    
    def __setOverlap(self, overlap):
        """
        """
        ConfigManager().setFloat('Preferences', 'SHOOTING_OVERLAP', overlap, 2)
        
    overlap = property(__getOverlap, __setOverlap)
    
    def __getCameraOrientation(self):
        """
        """
        return ConfigManager().get('Preferences', 'SHOOTING_CAMERA_ORIENTATION')
    
    def __setCameraOrientation(self, cameraOrientation):
        """
        """
        ConfigManager().set('Preferences', 'SHOOTING_CAMERA_ORIENTATION', cameraOrientation)

    cameraOrientation = property(__getCameraOrientation, __setCameraOrientation)

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
            nbPicts = int(round(((self.yawFov - self.overlap * cameraFov) / (cameraFov * (1 - self.overlap))) + 1))
        else:
            nbPicts = 1
        return nbPicts

    yawNbPicts = property(__getYawNbPicts, "Yaw nb picts")

    def __getPitchNbPicts(self):
        """
        """
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        if round(self.pitchFov - cameraFov, 1) >= 0.1:
           nbPicts = int(round(((self.pitchFov - self.overlap * cameraFov) / (cameraFov * (1 - self.overlap))) + 1))
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

    yawRealOverlap = property(__getRealYawOverlap, "Real yaw overlap")

    def __getRealPitchOverlap(self):
        """ Recompute real pitch overlap.
        """
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        if self.pitchNbPicts > 1:
            overlap = (self.pitchNbPicts * cameraFov - self.pitchFov) / (cameraFov * (self.pitchNbPicts - 1))
        else:
            overlap = 1.
        return overlap

    pitchRealOverlap = property(__getRealPitchOverlap, "Real pitch overlap")

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
            #self.yawRealOverlap = self.__getRealYawOverlap()
            #self.pitchRealOverlap = self.__getRealPitchOverlap()
        #elif setParam == 'fov':
            #Logger().warning("Shooting.__computeParam(): 'fov' setting not yet implemented")
        #elif setParam == 'nbPicts':
            #Logger().warning("Shooting.__computeParam(): 'nbPicts' setting not yet implemented")
        #else:
            #raise ValueError("param must be in ('startEnd', 'fov', 'nbPict')")

    def switchToRealHardware(self):
        """ Use real hardware.
        """
        try:
            #self.simulatedHardware.shutdown()
            self.realHardware.init()
            Logger().debug("Shooting.switchToRealHardware(): realHardware initialized")
            self.position = self.realHardware.readPosition()
            self.hardware = self.realHardware
            self.switchToRealHardwareSignal.emit(True)
        except HardwareError, message:
            Logger().exception("Shooting.switchToRealHardware()") 
            self.switchToRealHardwareSignal.emit(False, str(message))

    def switchToSimulatedHardware(self):
        """ Use simulated hardware.
        """
        self.realHardware.shutdown()
        self.hardware = self.simulatedHardware
        self.hardware.init()
        self.position = self.hardware.readPosition()

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

    def setYaw360(self):
        """ Compute start/end yaw position for 360°.
        
        Récupérer position courante et calculer début et fin pour avoir
        +-180°, overlap inclus
        """
        yaw, pitch = self.hardware.readPosition()
        cameraFov = self.camera.getYawFov(self.cameraOrientation)
        self.yawStart = yaw - 180. + cameraFov * (1 - self.overlap) / 2.
        self.yawEnd = yaw + 180. - cameraFov * (1 - self.overlap) / 2.
        self.yawStart = yaw - 180. + cameraFov * (1 - self.yawRealOverlap) / 2.
        self.yawEnd = yaw + 180. - cameraFov * (1 - self.yawRealOverlap) / 2.
        Logger().debug("Shooting.setYaw360(): startYaw=%.1f, endYaw=%.1f" % (self.yawStart, self.yawEnd))

    def setPitch180(self):
        """ Compute start/end pitch position for 180°.
        
        Récupérer position courante et calculer début et fin pour avoir
        +-90°, overlap inclus
        Tenir compte des butées softs !
        """
        yaw, pitch = self.hardware.readPosition()
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        self.pitchStart = pitch - 90. + cameraFov * (1 - self.overlap) / 2.
        self.pitchEnd = yaw + 90. - cameraFov * (1 - self.overlap) / 2.
        self.pitchStart = pitch - 90. + cameraFov * (1 - self.pitchRealOverlap) / 2.
        self.pitchEnd = yaw + 90. - cameraFov * (1 - self.pitchRealOverlap) / 2.
        Logger().debug("Shooting.setPitch180(): startPitch=%.1f, endPitch=%.1f" % (self.pitchStart, self.pitchEnd))

    def setManualShoot(self, flag):
        """ Turn on/off manual shoot.

        In manual shoot mode, the head switch to suspend at each end of position.

        @param flag: flag for manual shoot
        @type flag: bool
        """
        self.__manualShoot = flag

    def generate(self):
        """ Generate all shooting positions.
        
        @return: shooting positions
        @rtype: list of dict
        """

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
        yawInc *= cmp(self.yawEnd, self.yawStart)
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        try:
            pitchInc = (self.pitchFov - cameraFov) / (self.pitchNbPicts - 1)
        except ZeroDivisionError:
            pitchInc = self.pitchFov - cameraFov
        pitchInc *= cmp(self.pitchEnd, self.pitchStart)
        mosaic = Mosaic(self.yawNbPicts, self.pitchNbPicts)

        try:
            data = Data()
            values = {'stabilizationDelay': "%.1f" % self.stabilizationDelay,
                      'overlap': "%.2f" % self.overlap,
                      'yawRealOverlap': "%.2f" % self.yawRealOverlap,
                      'pitchRealOverlap': "%.2f" % self.pitchRealOverlap,
                      'cameraOrientation': "%s" % self.cameraOrientation,
                      'timeValue': "%.1f" % self.camera.timeValue,
                      'nbPicts': "%d" % self.camera.nbPicts,
                      'sensorCoef': "%.1f" % self.camera.sensorCoef,
                      'sensorRatio': "%s" % self.camera.sensorRatio,
                      'focal': "%.1f" % self.camera.lens.focal,
                      'fisheye': "%s" % self.camera.lens.fisheye,
                      'template': "mosaic",
                      'yawNbPicts': "%d" % self.yawNbPicts,
                      'pitchNbPicts': "%d" % self.pitchNbPicts
                  }
            data.createHeader(values)

            # Loop over all positions
            totalNbPicts = self.yawNbPicts * self.pitchNbPicts
            self.__progress = 0.
            for i, (yawCoef, pitchCoef) in enumerate(mosaic):
                yaw = self.yawStart + yawCoef * yawInc
                pitch = self.pitchStart + pitchCoef * pitchInc
                Logger().debug("Shooting.start(): Goto yaw=%.1f pitch=%.1f" % (yaw, pitch))
                self.__yawCoef = yawCoef
                self.__pitchCoef = pitchCoef
                Logger().info("Moving")
                self.__sequence = "Moving"
                self.hardware.gotoPosition(yaw, pitch)

                checkSuspendStop()

                Logger().info("Stabilization")
                self.__sequence = "Stabilizing"
                time.sleep(self.stabilizationDelay)

                if self.__manualShoot:
                    self.__suspend = True
                    Logger().info("Manual shoot")

                checkSuspendStop()

                Logger().info("Shooting")
                for pict in xrange(self.camera.nbPicts):
                    Logger().debug("Shooting.start(): Shooting %d/%d" % (pict + 1, self.camera.nbPicts))
                    self.__sequence = "Shooting %d/%d" % (pict + 1, self.camera.nbPicts)
                    self.hardware.shoot(self.camera.timeValue)
                    data.addImage(pict + 1, yaw, pitch)

                    checkSuspendStop()

                progressFraction = float((i + 1)) / float(totalNbPicts)
                self.__progress = progressFraction

            Logger().debug("Shooting.start(): finished")

        except StopIteration:
            Logger().debug("Shooting.start(): Stop detected")

        self.__yawCoef = "--"
        self.__pitchCoef = "--"
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
            yawIndex = "%s/%s" % (self.__yawCoef + 1, self.yawNbPicts)
        except TypeError:
            yawIndex = str(self.__yawCoef)
        try:
            pitchIndex = "%s/%s" % (self.__pitchCoef + 1, self.pitchNbPicts)
        except TypeError:
            pitchIndex = str(self.__pitchCoef)
        yawPos, pitchPos = self.hardware.readPosition()
        return {'yawPos': yawPos, 'pitchPos': pitchPos,
                'yawIndex': yawIndex, 'pitchIndex': pitchIndex,
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
        self.hardware.stopAxis()

    def shutdown(self):
        """ Cleanly terminate the model.

        Save values to preferences.
        """
        Logger().trace("Shooting.shutdown()")
        self.realHardware.shutdown()
        self.simulatedHardware.shutdown()
        self.camera.shutdown()
