# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Model.

Implements class:

- Lens
- Camera
- Mosaic
- Shooting

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
from common.misc import Preferences, Signal


class Lens(object):
    """ Lens model.
    
    Lens orientation is landscape.
    """
    def __init__(self):
        """ Init object.
        
        Load values from preferences.
        """
        self.__prefs = Preferences().load()
        self.focal = self.__prefs['lens']['focal']
        self.fisheye = self.__prefs['lens']['fisheye']
        
        # Load Mosaic db record
    
    def __del__(self):
        """ Destructor.
        
        Save values to preferences.
        """
        Logger().trace("Lens.__del__()")
        self.__prefs['lens']['focal'] = self.focal
        self.__prefs['lens']['fisheye'] = self.fisheye
    
    def computeFov(self, size):
        """ Compute FoV.
        
        @param size: size of the sensor
        @type size: float
        
        @return: FoV of the lens
        @rtype: float
        """
        if self.fisheye:
            return 360. / math.pi * 2. * math.asin((size / 2.) / (2. * self.focal))
        else:
            return 360. / math.pi * math.atan(size / (2. * self.focal))


class Camera(object):
    """ Camera model.
    """
    def __init__(self):
        """ Init the Camera object.
        
        Load values from preferences.
        """
        self.lens = Lens()
        
        # Load Camera attributes from preferences
        self.__prefs = Preferences().load()
        self.sensorRatio = self.__prefs['camera']['sensorRatio']
        self.sensorCoef = self.__prefs['camera']['sensorCoef']
        self.timeValue = self.__prefs['camera']['timeValue']
        self.nbPicts = self.__prefs['camera']['nbPicts']
    
    def __del__(self):
        """ Destructor.
        
        Save values to preferences.
        """
        Logger().trace("Camera.__del__()")
        del self.lens
        
        self.__prefs['camera']['sensorRatio'] = self.sensorRatio
        self.__prefs['camera']['sensorCoef'] = self.sensorCoef
        self.__prefs['camera']['timeValue'] = self.timeValue
        self.__prefs['camera']['nbPicts'] = self.nbPicts
    
    def getYawFov(self, cameraOrientation):
        """ Compute the yaw FoV.
        
        @return: yaw FoV of the image
        @rtype: float
        
        @todo: handle 4:3 format
        """
        if cameraOrientation == 'landscape':
            sensorSize = 36.
        elif cameraOrientation == 'portrait':
            sensorSize = 24.
            
        return self.lens.computeFov(sensorSize / self.sensorCoef)
    
    def getPitchFov(self, cameraOrientation):
        """ Compute the pitch FoV.

        @return: pitch FoV of the image
        @rtype: float
        
        @todo: handle 4:3 format
        """
        if cameraOrientation == 'landscape':
            sensorSize = 24.
        elif cameraOrientation == 'portrait':
            sensorSize = 36.
            
        return self.lens.computeFov(sensorSize / self.sensorCoef)


class Mosaic(object):
    """ Mosaic model.
    
    This is an iterator which iters of positions to shoot. A
    template defines the way positions are generated.
    Use it just as any iterator:
    
    >>> mosaic = Mosaic()
    >>> mosaic.template = "Y+P+Y-"
    >>> mosaic.setMatrix(yaw=3, pitch=3)
    >>> for yaw, pitch in mosaic:
    ...     print yaw, pitch
    0 0
    1 0
    2 0
    2 1
    1 1
    0 1
    0 2
    1 2
    2 2
    """
    def __init__(self):
        """ Init the Mosaic object.
        
        Load values from preferences.
        """
        #self.__yawNbPicts = None
        #self.__pitchNbPicts = None
        self.__init = False
        
        self.__prefs = Preferences().load()
        self.template = self.__prefs['mosaic']['template']
        self.zenith = self.__prefs['mosaic']['zenith']
        self.nadir = self.__prefs['mosaic']['nadir']

    def __del__(self):
        """ Destructor.
        
        Save values to preferences.
        """
        Logger().trace("Mosaic.__del__()")
        self.__prefs['mosaic']['template'] = self.template
        self.__prefs['mosaic']['zenith'] = self.zenith
        self.__prefs['mosaic']['nadir'] = self.nadir

    def __iter__(self):
        """ Define Mosaic as an iterator.
        """
        if self.__yawNbPicts is None or self.__pitchNbPicts is None:
            raise ValueError("You must call setMatrix() first")
        
        # Init self.__yaw and self.__pitch according of the template (todo)
        self.__inc = [{'yaw': 1, 'pitch': 0},
                      {'yaw': 0, 'pitch': 1},
                      {'yaw': -1, 'pitch': 0},
                      {'yaw': 0, 'pitch': 1}
                      ]
        self.__start = {'yaw': 0, 'pitch': 0}
        self.__yaw = -1
        self.__yawInc = 1
        self.__pitch = 0
        self.__pitchInc = 1
        
        return self

    def setMatrix(self, yawNbPicts, pitchNbPicts):
        """ Define the number of pictures for both yaw/pitch directions.
        
        @param yawNbPicts: number of pictures for yaw direction
        @type yawNbPicts: int
        
        @param pitchNbPicts: number of pictures for pitch direction
        @type pitchNbPicts: int
        """
        self.__yawNbPicts = yawNbPicts
        self.__pitchNbPicts = pitchNbPicts

    #def generate(self, yawNbPicts, pitchNbPicts):
        #if not self.__init:
            #inc = [{'yaw': 1, 'pitch': 0},
                   #{'yaw': 0, 'pitch': 1},
                   #{'yaw': -1, 'pitch': 0},
                   #{'yaw': 0, 'pitch': 1}
                  #]
            #yaw = 0
            #pitch = 0
            #idx = 0
            #self.__init = True
            
        #yield yaw, pitch
        #yaw += inc[idx]['yaw']
        #pitch += inc[idx]['pitch']
        #if yaw >= yawNbPicts:
        

    def next(self):
        """ Return next (yaw, pitch) position.
        """
        self.__yaw += self.__yawInc
        if self.__yaw >= self.__yawNbPicts:
            self.__yaw = self.__yawNbPicts - 1
            self.__yawInc = -1
            self.__pitch += self.__pitchInc
            if self.__pitch >= self.__pitchNbPicts:
                self.__yawNbPicts = self.__pitchNbPicts = None
                raise StopIteration
            elif self.__pitch < 0:
                self.__yawNbPicts = self.__pitchNbPicts = None
                raise StopIteration
        elif self.__yaw < 0:
            self.__yaw = 0
            self.__yawInc = +1
            self.__pitch += self.__pitchInc
            if self.__pitch >= self.__pitchNbPicts:
                self.__yawNbPicts = self.__pitchNbPicts = None
                raise StopIteration
            elif self.__pitch < 0:
                self.__yawNbPicts = self.__pitchNbPicts = None
                raise StopIteration
        Logger().debug("Mosaic.next(): __yaw=%d, __pitch=%d" % (self.__yaw, self.__pitch))
        return self.__yaw, self.__pitch


class Shooting(object):
    """ Shooting model.
    """
    def __init__(self, hardware):
        """ Init the object.

        @param hardware: hardware head
        @type hardware: {Head}
        """
        self.hardware = hardware
        self.__running = False
        self.__suspend = False
        self.__stop = False
        self.__yawCoef = "--"
        self.__pitchCoef = "--"
        self.__progress = "..."
        self.__sequence = "Idle"
        self.__setParams = None
        
        self.camera = Camera()
        self.mosaic = Mosaic()
        
        self.yawStart = 0.
        self.pitchStart = 0.
        self.yawEnd = 0.
        self.pitchEnd = 0.
        self.yawFov = 0.
        self.pitchFov = 0.
        self.yawNbPicts = 0
        self.pitchNbPicts = 0
        self.position = hardware.readPosition()

        self.__prefs = Preferences().load()
        self.delay = self.__prefs['shooting']['delay']
        self.overlap = self.__prefs['shooting']['overlap']
        self.realYawOverlap = self.overlap
        self.realPitchOverlap = self.overlap
        self.manualShoot = self.__prefs['shooting']['manualShoot']
        self.cameraOrientation = self.__prefs['shooting']['cameraOrientation']
        
        self.__computeParams('startEnd')

    def __del__(self):
        """ Destructor.
        
        Save values to preferences.
        """
        Logger().trace("Shooting.__del__()")
        del self.camera
        del self.mosaic
        
        self.__prefs['shooting']['delay'] = self.delay
        self.__prefs['shooting']['overlap'] = self.overlap
        self.__prefs['shooting']['manualShoot'] = self.manualShoot
        self.__prefs['shooting']['cameraOrientation'] = self.cameraOrientation
        
        Preferences().save()
   
    def __getYawFov(self):
        """
        """
        cameraFov = self.camera.getYawFov(self.cameraOrientation)
        return abs(self.yawEnd - self.yawStart) + cameraFov
    
    def __getPitchFov(self):
        """
        """
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        return abs(self.pitchEnd - self.pitchStart) + cameraFov
    
    def __getYawNbPicts(self):
        """
        """
        cameraFov = self.camera.getYawFov(self.cameraOrientation)
        if round(self.yawFov - cameraFov, 1) >= 0.1:
            nbPicts = int(((self.yawFov - self.overlap * cameraFov) / (cameraFov * (1 - self.overlap))) + 1)
        else:
            nbPicts = 1
        return nbPicts
    
    def __getPitchNbPicts(self):
        """
        """
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        if round(self.pitchFov - cameraFov, 1) >= 0.1:
           nbPicts = int(((self.pitchFov - self.overlap * cameraFov) / (cameraFov * (1 - self.overlap))) + 1)
        else:
            nbPicts = 1
        return nbPicts
    
    def __getRealYawOverlap(self):
        """ Recompute real yaw overlap.
        """
        cameraFov = self.camera.getYawFov(self.cameraOrientation)
        if self.yawNbPicts > 1:
            overlap = (self.yawNbPicts * cameraFov - self.yawFov) / (cameraFov * (self.yawNbPicts - 1))
        else:
            overlap = 1.
        return overlap
   
    def __getRealPitchOverlap(self):
        """ Recompute real pitch overlap.
        """
        cameraFov = self.camera.getPitchFov(self.cameraOrientation)
        if self.pitchNbPicts > 1:
            overlap = (self.pitchNbPicts * cameraFov - self.pitchFov) / (cameraFov * (self.pitchNbPicts - 1))
        else:
            overlap = 1.
        return overlap
   
    def __computeParams(self, setParam):
        """ Compute missing params from given params.
        
        @param setParam: given params type ('startEnd', 'fov', 'nbPict')
        @type setParam: str
        
        @todo: add fov and nbPicts
        """
        if setParam == 'startEnd':
            self.yawFov = self.__getYawFov()
            self.pitchFov = self.__getPitchFov()
            self.yawNbPicts = self.__getYawNbPicts()
            self.pitchNbPicts = self.__getPitchNbPicts()
            self.realYawOverlap = self.__getRealYawOverlap()
            self.realPitchOverlap = self.__getRealPitchOverlap()
        elif setParam == 'fov':
            Logger().warning("Shooting.__computeParam(): 'fov' setting not yet implemented")
        elif setParam == 'nbPicts':
            Logger().warning("Shooting.__computeParam(): 'nbPicts' setting not yet implemented")
        else:
            raise ValueError("param must be in ('startEnd', 'fov', 'nbPict')")

    def setHead(self, hardware):
        """ Set the new hardware head to use.
        
        Used to switch from real to simulated hardware.

        @param hardware: hardware head
        @type hardware: {Head}
        """
        self.hardware = hardware

    def storeStartPosition(self):
        """ Store current position as start position.
        """
        self.yawStart, self.pitchStart = self.hardware.readPosition()
        Logger().debug("Shooting.storeStartPosition(): yaw=%.1f, pitch=%.1f" % (self.yawStart, self.pitchStart))
        self.__computeParams('startEnd')
    
    def storeEndPosition(self):
        """ Store current position as end position.
        """
        self.yawEnd, self.pitchEnd = self.hardware.readPosition()
        Logger().debug("Shooting.storeStartPosition(): yaw=%.1f, pitch=%.1f)" % (self.yawEnd, self.pitchEnd))
        self.__computeParams('startEnd')
    
    def start(self):
        """ Start pano shooting.
        """
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
        self.mosaic.setMatrix(self.yawNbPicts, self.pitchNbPicts)  # also give incs to receive exact positions
        
        # Loop over all positions
        for yawCoef, pitchCoef in self.mosaic:
            yaw = self.yawStart + yawCoef * yawInc
            pitch = self.pitchStart + pitchCoef * pitchInc
            Logger().debug("Shooting.start(): Goto yaw=%.1f pitch=%.1f" % (yaw, pitch))
            self.__yawCoef = yawCoef
            self.__pitchCoef = pitchCoef
            Logger().info("Shooting.start(): Moving")
            self.__sequence = "Moving"
            #self.__progress = "..."
            self.hardware.gotoPosition(yaw, pitch)

            Logger().info("Shooting.start(): Stabilization")
            self.__sequence = "Stabilizing"
            time.sleep(self.delay)

            if self.__suspend:
                self.__sequence = "Idle"
                while self.__suspend:
                    time.sleep(0.1)
            if self.__stop:
                break

            # todo: implement manual shooting (must be in controller!)
            for pict in xrange(self.camera.nbPicts):
                Logger().info("Shooting.start(): Shooting")
                Logger().debug("Shooting.start(): Shooting %d/%d" % (pict + 1, self.camera.nbPicts + 1))
                self.__sequence = "Shooting %d/%d" % (pict + 1, self.camera.nbPicts)
                self.hardware.shoot(self.camera.timeValue)
        
        # Zenith/Nadir
        # todo: implement stab., manual shooting and multiple shots
        if self.mosaic.zenith:
            if not self.__stop:
                Logger().info("Shooting.start(): Moving")
                Logger().debug("Shooting.start(): Goto zenith")
                self.__yawCoef = "zenith"
                self.__pitchCoef = "zenith"
                self.__sequence = "Moving"
                #self.__progress = "..."
                self.hardware.gotoPosition(0., -90.)
            if not self.__stop:
                Logger().info("Shooting.start(): Shooting")
                Logger().debug("Shooting.start(): Shooting zenith")
                self.__sequence = "Shooting zenith"
                self.hardware.shoot(self.camera.timeValue)
            
        if self.mosaic.nadir:
            if not self.__stop:
                Logger().info("Shooting.start(): Moving")
                Logger().debug("Shooting.start(): Goto nadir")
                self.__yawCoef = "nadir"
                self.__pitchCoef = "nadir"
                self.__sequence = "Moving"
                #self.__progress = "..."
                self.hardware.gotoPosition(0., 90.)
            if not self.__stop:
                Logger().info("Shooting.start(): Shooting")
                Logger().debug("Shooting.start(): Shooting nadir")
                self.__sequence = "Shooting nadir"
                self.hardware.shoot(self.camera.timeValue)
        
        self.__yawCoef = "--"
        self.__pitchCoef = "--"
        self.__progress = "..."
        self.__sequence = "Idle"
        self.__stop = False
        self.__running = False
    
    def getState(self):
        """ Return shooting state.
        
        @return: key 'yawCoef': yaw mosaic coef
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
        return {'yawCoef': yawCoef, 'pitchCoef': pitchCoef, 'progress': self.__progress, 'sequence': self.__sequence}
    
    def isShooting(self):
        """ Test if shooting is running.
        
        @return: True if shooting is running, False otherwise
        @rtype: bool
        """
        return self.__running
    
    def suspend(self):
        """ Suspend execution of pano shooting.
        """
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
        self.__suspend = False
    
    def stop(self): 
        """ Cancel execution of shooting.
        """
        self.__stop = True
        self.__suspend = False
        self.hardware.stopAxis('yaw')
        self.hardware.stopAxis('pitch')


class Spy(threading.Thread):
    """ Real time spy object.
    
    The Spy periodically polls the hardware to get
    the hardware position. When a change is detected, it emits
    a signal, passing new hardware position.
    """
    def __init__(self, model):
        """ Init the object.

        @param model: model to use
        @type mode: {Shooting}
        """
        super(Spy, self).__init__()
        self.setDaemon(1)

        self.__model = model
        self.__run = False
        self.newPosSignal = Signal()
        
    def run(self):
        """ Main entry of the thread.
        """
        self.__run = True
        self.__yaw, self.__pitch = self.__model.hardware.readPosition()
        self.newPosSignal.emit(self.__yaw, self.__pitch)
        while self.__run:
            yaw, pitch = self.__model.hardware.readPosition()
            if yaw != self.__yaw or pitch != self.__pitch:
                Logger().debug("Spy.run(): yaw=%.1f, pitch=%.1f" % (yaw, pitch))
                self.newPosSignal.emit(yaw, pitch)
                self.__yaw = yaw
                self.__pitch = pitch
            
            time.sleep(config.SPY_REFRESH)
            
    def stop(self):
        """ Stop the thread.
        """
        self.__run = False
