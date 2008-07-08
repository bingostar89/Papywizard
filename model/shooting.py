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

Model

Implements
==========

- Shooting

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import threading

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
        self.__shooting = False
        self.__suspend = False
        self.__stop = False
        self.__setParams = None
        self.__manualShoot = False

        self.realHardware = realHardware
        self.simulatedHardware = simulatedHardware
        self.hardware = self.simulatedHardware
        self.switchToRealHardwareSignal = Signal()
        self.newPictSignal = Signal()
        self.startEvent = threading.Event()
        self.startEvent.clear()
        self.camera = Camera()
        self.mosaic = Mosaic(self.camera)
        #self.fullSpherical = FullSpherical()

        self.position = self.hardware.readPosition()
        self.progress = 0.
        self.sequence = "Idle"

    # Properties
    def __getStabilizationDelay(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'SHOOTING_STABILIZATION_DELAY')
    
    def __setStabilizationDelay(self, stabilizationDelay):
        """
        """
        ConfigManager().setFloat('Preferences', 'SHOOTING_STABILIZATION_DELAY', stabilizationDelay, 1)
    
    stabilizationDelay = property(__getStabilizationDelay, __setStabilizationDelay)

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

    def setManualShoot(self, flag):
        """ Turn on/off manual shoot.

        In manual shoot mode, the head switch to suspend at each end of position.

        @param flag: flag for manual shoot
        @type flag: bool
        """
        self.__manualShoot = flag

    def initProgress(self):
        """ Init progress value.
        """
        self.progress = 0.
        self.sequence = "Idle" # find better

    def start(self):
        """ Start pano shooting.
        """
        def checkSuspendStop():
            """ Check if suspend or stop requested.
            """
            if self.__suspend:
                Logger().info("Suspend")
                self.sequence = "Idle"
                while self.__suspend:
                    time.sleep(0.1)
                Logger().info("Resume")
            if self.__stop:
                Logger().info("Stop")
                raise StopIteration

        Logger().trace("Shooting.start()")

        data = Data()
        values = {'stabilizationDelay': "%.1f" % self.stabilizationDelay,
                  'overlap': "%.2f" % self.mosaic.overlap,
                  'yawRealOverlap': "%.2f" % self.mosaic.yawRealOverlap,
                  'pitchRealOverlap': "%.2f" % self.mosaic.pitchRealOverlap,
                  'cameraOrientation': "%s" % self.mosaic.cameraOrientation,
                  'timeValue': "%.1f" % self.camera.timeValue,
                  'nbPicts': "%d" % self.camera.nbPicts,
                  'sensorCoef': "%.1f" % self.camera.sensorCoef,
                  'sensorRatio': "%s" % self.camera.sensorRatio,
                  'focal': "%.1f" % self.camera.lens.focal,
                  'fisheye': "%s" % self.camera.lens.fisheye,
                  'template': "mosaic",
                  'yawNbPicts': "%d" % self.mosaic.yawNbPicts,
                  'pitchNbPicts': "%d" % self.mosaic.pitchNbPicts
              }
        data.createHeader(values)
        self.error = False
        self.progress = 0.
        self.__stop = False
        self.__shooting = True
        self.startEvent.set()

        # Loop over all positions
        try:
            for i, (yaw, pitch) in enumerate(self.mosaic.iterPositions()):
                Logger().debug("Shooting.start(): Goto yaw=%.1f pitch=%.1f" % (yaw, pitch))
                Logger().info("Moving")
                self.sequence = "Moving"
                self.hardware.gotoPosition(yaw, pitch)

                checkSuspendStop()

                Logger().info("Stabilization")
                self.sequence = "Stabilizing"
                time.sleep(self.stabilizationDelay)

                if self.__manualShoot:
                    self.__suspend = True
                    Logger().info("Manual shoot")

                checkSuspendStop()

                Logger().info("Shooting")
                for pict in xrange(self.camera.nbPicts):
                    Logger().debug("Shooting.start(): Shooting %d/%d" % (pict + 1, self.camera.nbPicts))
                    self.sequence = "Shooting %d/%d" % (pict + 1, self.camera.nbPicts)
                    self.hardware.shoot(self.camera.timeValue)
                    data.addPicture(pict + 1, yaw, pitch)

                    checkSuspendStop()

                progressFraction = float((i + 1)) / float(self.mosaic.totalNbPicts)
                self.progress = progressFraction
                self.newPictSignal.emit(yaw, pitch) # Include progress?

            Logger().debug("Shooting.start(): finished")

        except StopIteration:
            Logger().debug("Shooting.start(): Stop detected")
            self.sequence = "Canceled"
        except:
            Logger().exception("Shooting.start()")
            self.error = True
        else:
            self.sequence = "Over"
            
        self.__shooting = False

    def isShooting(self):
        """ Test if shooting is running.

        @return: True if shooting is running, False otherwise
        @rtype: bool
        """
        return self.__shooting

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
