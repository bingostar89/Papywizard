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

from papywizard.common.loggingServices import Logger
from papywizard.common.preferences import Preferences
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
        self.camera = Camera()
        self.mosaic = Mosaic()

        self.yawStart = 0.
        self.pitchStart = 0.
        self.yawEnd = 0.
        self.pitchEnd = 0.
        self.position = self.hardware.readPosition()

        self.__prefs = Preferences().load()
        self.delay = self.__prefs['shooting']['delay']
        self.overlap = self.__prefs['shooting']['overlap']
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
        if self.realHardware is not None:
            try:
                self.simulatedHardware.shutdown()
                self.realHardware.init()
                Logger().debug("Shooting.switchToRealHardware(): realHardware initialized")
                self.position = self.realHardware.readPosition()
                self.hardware = self.realHardware
            except HardwareError:
                Logger().exception("Shooting.switchToRealHardware()")
                Logger().warning("Can't switch to real hardware")
                raise
        else:
            raise HardwareError("No real hardware available")

    def switchToSimulatedHardware(self):
        """ Use simulated hardware.
        """
        self.realHardware.shutdown()
        self.hardware = self.simulatedHardware
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

    def setManualShoot(self, flag):
        """ Turn on/off manual shoot.

        In manual shoot mode, the head switch to suspend at each end of position.

        @param flag: flag for manual shoot
        @type flag: bool
        """
        self.__manualShoot = flag

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
            data = Data()
            data.addHeaderNode('focal', "%.1f" % self.camera.lens.focal)
            data.addHeaderNode('fisheye', "%s" % self.camera.lens.fisheye)
            data.addHeaderNode('sensorCoef', "%.1f" % self.camera.sensorCoef)
            data.addHeaderNode('sensorRatio', "%s" % self.camera.sensorRatio)
            data.addHeaderNode('cameraOrientation', "%s" % self.cameraOrientation)
            data.addHeaderNode('nbPicts', "%d" % self.camera.nbPicts)
            data.addHeaderNode('yawRealOverlap', "%.2f" % self.yawRealOverlap)
            data.addHeaderNode('pitchRealOverlap', "%.2f" % self.pitchRealOverlap)
            data.addHeaderNode('template', type="mosaic", yaw="%d" % self.yawNbPicts, pitch="%d" % self.pitchNbPicts)

            # Loop over all positions
            totalNbPicts = self.yawNbPicts * self.pitchNbPicts
            self.__progress = 0.
            for i, (yawCoef, pitchCoef) in enumerate(self.mosaic):
                yaw = self.yawStart + yawCoef * yawInc
                pitch = self.pitchStart + pitchCoef * pitchInc
                Logger().debug("Shooting.start(): Goto yaw=%.1f pitch=%.1f" % (yaw, pitch))
                self.__yawCoef = yawCoef
                self.__pitchCoef = pitchCoef
                Logger().info("Moving")
                self.__sequence = "Moving"
                self.hardware.gotoPosition(yaw, pitch)

                Logger().info("Stabilization")
                self.__sequence = "Stabilizing"
                time.sleep(self.delay)

                if self.__manualShoot:
                    self.__suspend = True
                    Logger().info("Manual shoot")

                checkSuspendStop()

                Logger().info("Shooting")
                for pict in xrange(self.camera.nbPicts):
                    Logger().debug("Shooting.start(): Shooting %d/%d" % (pict + 1, self.camera.nbPicts))
                    self.__sequence = "Shooting %d/%d" % (pict + 1, self.camera.nbPicts)
                    self.hardware.shoot(self.camera.timeValue)
                    data.addImageNode(pict + 1, yaw, pitch)

                    checkSuspendStop()

                self.__progress = float((i + 1)) / float(totalNbPicts)

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
        self.hardware.shutdown()
        self.camera.shutdown()
        self.mosaic.shutdown()

        self.__prefs['shooting']['delay'] = self.delay
        self.__prefs['shooting']['overlap'] = self.overlap
        self.__prefs['shooting']['cameraOrientation'] = self.cameraOrientation

        Preferences().save()
