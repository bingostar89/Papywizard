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

- Mosaic

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.model.scan import Scan


class Mosaic(Scan):
    """ Mosaic model.
    """
    def __init__(self, camera):
        """ Init the Mosaic object.
        
        @param camera: camera object
        @type camera: {Camera}
        """
        self.__camera = camera
        
        self.yawStart = 0.
        self.pitchStart = 0.
        self.yawEnd = 0.
        self.pitchEnd = 0.
        self.__yawIndex = None
        self.__pitchIndex = None
        self.__yawInc = None
        self.__pitchInc = None
        self.__yawIndex = None
        self.__pitchIndex = None

        #self.__yawSens = None
        #self.__pitchSens = None
        

    def __iter__(self):
        """ Define Mosaic as an iterator.
        """
        yawCameraFov = self.__camera.getYawFov(self.cameraOrientation)
        pitchCameraFov = self.__camera.getPitchFov(self.cameraOrientation)
        try:
            self.__yawInc = (self.yawFov - yawCameraFov) / (self.yawNbPicts - 1)
        except ZeroDivisionError:
            self.__yawInc = self.yawFov - yawCameraFov
        try:
            self.__pitchInc = (self.pitchFov - pitchCameraFov) / (self.pitchNbPicts - 1)
        except ZeroDivisionError:
            self.__pitchInc = self.pitchFov - pitchCameraFov
        self.__yawInc *= cmp(self.yawEnd, self.yawStart)
        self.__pitchInc *= cmp(self.pitchEnd, self.pitchStart)

        # Init mosaic shooting params (should be in preferences)
        self.__firstMove = "yaw"
        self.__yawCR = False
        self.__pitchCR = False
        
        #if self.__yawInc > 0:
            #self.__yawIndex = 0
            #self.__yawSens = 1
        #else:
            #self.__yawIndex = self.yawNbPicts - 1
            #self.__yawSens = -1
        #if self.__pitchInc > 0:
            #self.__pitchIndex = 0
            #self.__pitchSens = 1
        #else:
            #self.__pitchIndex = self.pitchNbPicts - 1
            #self.__pitchSens = -1
            
        self.__yawIndex = 0
        self.__yawSens = 1
        self.__pitchIndex = 0
        self.__pitchSens = 1
            
        return self.next2()

    def next2(self):
        """ Return next (yaw, pitch) index position.
        """
        while True:
            yaw = self.yawStart + self.__yawIndex * self.__yawInc
            pitch = self.pitchStart + self.__pitchIndex * self.__pitchInc
            Logger().debug("Mosaic.next(): __yawIndex=%d, __pitchIndex=%d" % (self.__yawIndex, self.__pitchIndex))
            Logger().debug("Mosaic.next(): yaw=%.1f, pitch=%.1f" % (yaw, pitch))
            yield yaw, pitch
            
            # Compute next position
            if self.__firstMove == "yaw":
                self.__yawIndex += self.__yawSens
            elif self.__firstMove == "pitch":
                self.__pitchIndex += self.__pitchSens

            for i in xrange(2):
                if self.__yawIndex == self.yawNbPicts: # __yawSens was 1
                    if self.__firstMove == "pitch":
                        raise StopIteration
                    if self.__yawCR:
                        self.__yawIndex = 0
                        self.__yawSens = 1
                    else:
                        self.__yawIndex = self.yawNbPicts - 1
                        self.__yawSens = -1
                    self.__pitchIndex += self.__pitchSens
                    continue
                elif self.__yawIndex == -1:            # __yawSens was -1
                    if self.__firstMove == "pitch":
                        raise StopIteration
                    if self.__yawCR:
                        self.__yawIndex = self.yawNbPicts - 1
                        self.__yawSens = -1
                    else:
                        self.__yawIndex = 0
                        self.__yawSens = 1
                    self.__pitchIndex += self.__pitchSens
                    continue
                
                if self.__pitchIndex == self.pitchNbPicts: # __pitchSens was 1
                    if self.__firstMove == "yaw":
                        raise StopIteration
                    if self.__pitchCR:
                        self.__pitchIndex = 0
                        self.__pitchSens = 1
                    else:
                        self.__pitchIndex = self.pitchNbPicts - 1
                        self.__pitchSens = -1
                    self.__yawIndex += self.__yawSens
                    continue
                elif self.__pitchIndex == -1:              # __pitchSens was -1
                    if self.__firstMove == "yaw":
                        raise StopIteration
                    if self.__pitchCR:
                        self.__pitchIndex = self.pitchNbPicts - 1
                        self.__pitchSens = -1
                    else:
                        self.__pitchIndex = 0
                        self.__pitchSens = 1
                    self.__yawIndex += self.__yawSens
                    continue
                
                break

    #def next(self):
        #""" Return next (yaw, pitch) index position.
        #"""
        #self.__yawIndex += self.__yawSens
        #if self.__yawIndex >= self.yawNbPicts:
            #self.__yawIndex = self.yawNbPicts - 1
            #self.__yawSens = -1
            #self.__pitchIndex += self.__pitchSens
            #if self.__pitchIndex >= self.pitchNbPicts:
                #raise StopIteration
            #elif self.__pitchIndex < 0:
                #raise StopIteration
        #elif self.__yawIndex < 0:
            #self.__yawIndex = 0
            #self.__yawSens = +1
            #self.__pitchIndex += self.__pitchSens
            #if self.__pitchIndex >= self.pitchNbPicts:
                #raise StopIteration
            #elif self.__pitchIndex < 0:
                #raise StopIteration
            
        #yaw = self.yawStart + self.__yawIndex * self.__yawInc
        #pitch = self.pitchStart + self.__pitchIndex * self.__pitchInc
        #Logger().debug("Mosaic.next(): __yawIndex=%d, __pitchIndex=%d" % (self.__yawIndex, self.__pitchIndex))
        #Logger().debug("Mosaic.next(): yaw=%.1f, pitch=%.1f" % (yaw, pitch))
        
        #return yaw, pitch

    # Properties
    def __getTemplate(self):
        """
        """
        return ConfigManager().get('Preferences', 'SHOOTING_MOSAIC_TEMPLATE')
    
    def __setTemplate(self, template):
        """
        """
        ConfigManager().set('Preferences', 'SHOOTING_MOSAIC_TEMPLATE', template)

    template = property(__getTemplate, __setTemplate)
    
    def __getCameraOrientation(self):
        """
        """
        return ConfigManager().get('Preferences', 'SHOOTING_MOSAIC_CAMERA_ORIENTATION')
    
    def __setCameraOrientation(self, cameraOrientation):
        """
        """
        ConfigManager().set('Preferences', 'SHOOTING_MOSAIC_CAMERA_ORIENTATION', cameraOrientation)

    cameraOrientation = property(__getCameraOrientation, __setCameraOrientation)
    
    def __getOverlap(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'SHOOTING_MOSAIC_OVERLAP')
    
    def __setOverlap(self, overlap):
        """
        """
        ConfigManager().setFloat('Preferences', 'SHOOTING_MOSAIC_OVERLAP', overlap, 2)
        
    overlap = property(__getOverlap, __setOverlap)

    def __getYawFov(self):
        """
        """
        yawCameraFov = self.__camera.getYawFov(self.cameraOrientation)
        return abs(self.yawEnd - self.yawStart) + yawCameraFov

    yawFov = property(__getYawFov, "Total yaw FoV")

    def __getPitchFov(self):
        """
        """
        pitchCameraFov = self.__camera.getPitchFov(self.cameraOrientation)
        return abs(self.pitchEnd - self.pitchStart) + pitchCameraFov

    pitchFov = property(__getPitchFov, "Total pitch FoV")

    def __getYawNbPicts(self):
        """
        """
        yawCameraFov = self.__camera.getYawFov(self.cameraOrientation)
        if round(self.yawFov - yawCameraFov, 1) >= 0.1:
            nbPicts = int(((self.yawFov - self.overlap * yawCameraFov) / (yawCameraFov * (1 - self.overlap))) + 1)
        else:
            nbPicts = 1
        return nbPicts

    yawNbPicts = property(__getYawNbPicts, "Yaw nb picts")

    def __getPitchNbPicts(self):
        """
        """
        pitchCameraFov = self.__camera.getPitchFov(self.cameraOrientation)
        if round(self.pitchFov - pitchCameraFov, 1) >= 0.1:
           nbPicts = int(((self.pitchFov - self.overlap * pitchCameraFov) / (pitchCameraFov * (1 - self.overlap))) + 1)
        else:
            nbPicts = 1
        return nbPicts

    pitchNbPicts = property(__getPitchNbPicts, "Pitch nb picts")

    def __getTotalNbPicts(self):
        """
        """
        return self.yawNbPicts * self.pitchNbPicts
    
    totalNbPicts = property(__getTotalNbPicts)

    def __getYawRealOverlap(self):
        """ Recompute real yaw overlap.
        """
        yawCameraFov = self.__camera.getYawFov(self.cameraOrientation)
        if self.yawNbPicts > 1:
            overlap = (self.yawNbPicts * yawCameraFov - self.yawFov) / (yawCameraFov * (self.yawNbPicts - 1))
        else:
            overlap = 1.
        return overlap

    yawRealOverlap = property(__getYawRealOverlap, "Yaw real overlap")

    def __getPitchRealOverlap(self):
        """ Recompute real pitch overlap.
        """
        pitchCameraFov = self.__camera.getPitchFov(self.cameraOrientation)
        if self.pitchNbPicts > 1:
            overlap = (self.pitchNbPicts * pitchCameraFov - self.pitchFov) / (pitchCameraFov * (self.pitchNbPicts - 1))
        else:
            overlap = 1.
        return overlap

    pitchRealOverlap = property(__getPitchRealOverlap, "Pitch real overlap")

    def __totalNbPicts(self):
        return self.__yawNbPicts * self.__pitchNbPicts

    # Public methods
    def storeStartPosition(self, yaw, pitch):
        """ Store current position as start position.
        """
        self.yawStart, self.pitchStart = yaw, pitch
        Logger().debug("Shooting.storeStartPosition(): yaw=%.1f, pitch=%.1f" % (self.yawStart, self.pitchStart))

    def storeEndPosition(self, yaw, pitch):
        """ Store current position as end position.
        """
        self.yawEnd, self.pitchEnd = yaw, pitch
        Logger().debug("Shooting.storeEndPosition(): yaw=%.1f, pitch=%.1f" % (self.yawEnd, self.pitchEnd))
        
    def setYaw360(self, yaw):
        """ Compute start/end yaw position for 360°.
        """
        yawCameraFov = self.__camera.getPitchFov(self.cameraOrientation)
        self.yawStart = yaw - 180. + yawCameraFov * (1 - self.overlap) / 2.
        self.yawEnd = yaw + 180. - yawCameraFov * (1 - self.overlap) / 2.
        Logger().debug("Mosaic.setYaw360(): startYaw=%.1f, endYaw=%.1f" % (self.yawStart, self.yawEnd))

    def setPitch180(self, pitch):
        """ Compute start/end pitch position for 180°.
        """
        pitchCameraFov = self.__camera.getPitchFov(self.cameraOrientation)
        self.pitchStart = pitch - 90. + pitchCameraFov * (1 - self.overlap) / 2.
        self.pitchEnd = pitch + 90. - pitchCameraFov * (1 - self.overlap) / 2.
        Logger().debug("Mosaic.setPitch180(): startPitch=%.1f, endPitch=%.1f" % (self.pitchStart, self.pitchEnd))
